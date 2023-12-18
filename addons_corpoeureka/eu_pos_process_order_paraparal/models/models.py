# -*- coding: utf-8 -*-
from datetime import datetime
import logging

import psycopg2
import pytz

from odoo import api, models, tools, _

_logger = logging.getLogger(__name__)

class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model
    def _process_order(self, order, draft, existing_order):
        """Create or update an pos.order from a given dictionary.

        :param dict order: dictionary representing the order.
        :param bool draft: Indicate that the pos_order is not validated yet.
        :param existing_order: order to be updated or False.
        :type existing_order: pos.order.
        :returns: id of created/updated pos.order
        :rtype: int
        """
        order = order['data']
        pos_session = self.env['pos.session'].browse(order['pos_session_id'])
        if pos_session.state == 'closing_control' or pos_session.state == 'closed':
            order['pos_session_id'] = self._get_valid_session(order).id

        pos_order = False
        if not existing_order:
            pos_order = self.create(self._order_fields(order))
        else:
            pos_order = existing_order
            pos_order.lines.unlink()
            order['user_id'] = pos_order.user_id.id
            pos_order.write(self._order_fields(order))

        coupon_id = order.get('coupon_id', False)
        if coupon_id:
            coup_max_amount = order.get('coup_maxamount',False)
            pos_order.write({'coupon_id':  coupon_id})
            pos_order.coupon_id.update({
                'coupon_count': pos_order.coupon_id.coupon_count + 1,
                'max_amount': coup_max_amount
            })

        if pos_order.config_id.discount_type == 'percentage':
            pos_order.update({'discount_type': "Percentage"})
            pos_order.lines.update({'discount_line_type': "Percentage"})
        if pos_order.config_id.discount_type == 'fixed':
            pos_order.update({'discount_type': "Fixed"})
            pos_order.lines.update({'discount_line_type': "Fixed"})

        pos_order = pos_order.with_company(pos_order.company_id)
        self = self.with_company(pos_order.company_id)
        self._process_payment_lines(order, pos_order, pos_session, draft)

        if not draft:
            try:
                pos_order.action_pos_order_paid()
            except psycopg2.DatabaseError:
                # do not hide transactional errors, the order(s) won't be saved!
                raise
            except Exception as e:
                _logger.error('Could not fully process the POS Order: %s', tools.ustr(e))

        if order['get_delivery_charge_data'] and order['get_delivery_charge']:
            get_delivery_data = order.get('get_delivery_charge_data')
            get_delivery_charge = order.get('get_delivery_charge_data')
            time = '00:00'
            if get_delivery_data.get('DeliveryTime'):
                time = get_delivery_data.get('DeliveryTime')
            delivery_datetime_str = get_delivery_data.get('DeliveryDate') + " " + time + ":00"
            local = pytz.timezone(self.env.user.tz)
            delivery_datetime = datetime.strptime(delivery_datetime_str, "%Y-%m-%d %H:%M:%S")
            local_dt = local.localize(delivery_datetime, is_dst=None)
            utc_dt = local_dt.astimezone(pytz.utc)
            dt_string = str(utc_dt)
            new_dt = dt_string[:19]
            utc_delivery_datetime = datetime.strptime(new_dt, '%Y-%m-%d %H:%M:%S')
            vals = {
                'is_delivery_charge': get_delivery_data.get('IsDeliveryCharge'),
                'delivery_user_id': int(get_delivery_data.get('DeliveryUser')),
                'delivery_date': utc_delivery_datetime,
                'delivery_address': get_delivery_data.get('CustomerAddress'),
                'delivery_charge_amt': get_delivery_charge.get('amount'),
                'delivery_type': 'pending',
            }
            pos_order.write(vals)

        pos_order._create_order_picking()

        create_invoice = False
        if pos_order.to_invoice and pos_order.state == 'paid':
            if pos_order.amount_total > 0:  
                create_invoice = True
            elif pos_order.amount_total < 0:
                if pos_order.session_id.config_id.credit_note == "create_note":
                    create_invoice = True

        if create_invoice:
            pos_order.action_pos_order_invoice()
            if pos_order.discount_type and pos_order.discount_type == "Fixed":
                invoice = pos_order.account_move
                for line in invoice.invoice_line_ids : 
                    pos_line = line.pos_order_line_id
                    if pos_line and pos_line.discount_line_type == "Fixed":
                        line.write({'price_unit':pos_line.price_unit})

        if pos_order:
            if order['wallet_type']:
                self.wallet_management(order, pos_order)
            if order.get('giftcard') or order.get('redeem') or order.get('recharge'):
                self.gift_card_management(order, pos_order)
            if order.get('voucher_redeem'):
                self.gift_voucher_management(order)
            if order.get('partner_id') and pos_order:
                self.loyalty_management(order, pos_order)

        return pos_order.id