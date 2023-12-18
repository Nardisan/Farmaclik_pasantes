# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
from datetime import timedelta
from functools import partial

import psycopg2
import pytz
import re

from odoo import api, fields, models, tools, _
from odoo.tools import float_is_zero, float_round
from odoo.exceptions import ValidationError, UserError
from odoo.http import request
from odoo.osv.expression import AND
import base64

_logger = logging.getLogger(__name__)
class ReportSessionSummary(models.AbstractModel):

    _name = 'report.pos_report_session_summary.report_session_summary'

    def _get_report_values_session(self, date_start=False, date_stop=False, session_id=False):
        """ Serialise the orders of the requested time period, configs and sessions.

        :param date_start: The dateTime to start, default today 00:00:00.
        :type date_start: str.
        :param date_stop: The dateTime to stop, default date_start + 23:59:59.
        :type date_stop: str.
        :param config_ids: Pos Config id's to include.
        :type config_ids: list of numbers.
        :param session_ids: Pos Config id's to include.
        :type session_ids: list of numbers.

        :returns: dict -- Serialised sales.
        """
        domain = [('session_id', '=', session_id)]

       
        orders = self.env['pos.order'].search(domain)
        user_currency = self.env.company.currency_id

        total = 0.0
        total_ref = 0.0
        products_sold = {}
        taxes = {}
        session = {}
        commissions_doctor = []
        for order in orders:
            ses = session.get(order.session_id.id, False)
            if not ses:
                session[order.session_id.id] = {
                    'session': order.session_id.name,
                    'config_id':order.session_id.config_id.name,
                    'user_id' : order.session_id.user_id.name,
                    'employee_id': order.employee_id.name,
                }
                
            if user_currency != order.pricelist_id.currency_id:
                total += order.pricelist_id.currency_id._convert(
                    order.amount_total, user_currency, order.company_id, order.date_order or fields.Date.today())
            else:
                total += order.amount_total
            currency = order.session_id.currency_id
            total_ref += order.amount_total_ref
            for line in order.lines:
                key = (line.product_id, line.price_unit,line.price_unit_ref, line.discount)
                products_sold.setdefault(key, 0.0)
                products_sold[key] += line.qty

                if line.tax_ids_after_fiscal_position:
                    line_taxes = line.tax_ids_after_fiscal_position.sudo().compute_all(line.price_unit * (1-(line.discount or 0.0)/100.0), currency, line.qty, product=line.product_id, partner=line.order_id.partner_id or False)
                    for tax in line_taxes['taxes']:
                        taxes.setdefault(tax['id'], {'name': tax['name'], 'tax_amount':0.0, 'base_amount':0.0})
                        taxes[tax['id']]['tax_amount'] += tax['amount']
                        taxes[tax['id']]['base_amount'] += tax['base']
                else:
                    taxes.setdefault(0, {'name': _('No Taxes'), 'tax_amount':0.0, 'base_amount':0.0})
                    taxes[0]['base_amount'] += line.price_subtotal_incl

            if order.ref_doctor_id:
                commissions_doctor.append(order.ref_doctor_id.name)
        dic = []
        doctor_list = []
        i=0

        for commission in commissions_doctor:
            count = commissions_doctor.count(commission)
            if commission not in doctor_list:
                dic.append({
                        'name': commission,
                        'count':count
                        })
            if len(commissions_doctor) != count:
                doctor_list.append(commission)
                i+=1
            else:
                break 

        payment_ids = self.env["pos.payment"].search([('pos_order_id', 'in', orders.ids)]).ids
        if payment_ids:
            self.env.cr.execute("""
                SELECT method.name, sum(amount) total, sum(amount_ref) total_ref
                FROM pos_payment AS payment,
                     pos_payment_method AS method
                WHERE payment.payment_method_id = method.id
                    AND payment.session_id = %s
                GROUP BY method.name
            """, (session_id,))
            payments = self.env.cr.dictfetchall()
        else:
            payments = []

        
        return {
            'sessions':list(session.values()),
            'currency_precision': user_currency.decimal_places,
            'total_paid': user_currency.round(total),
            'total_paid_ref': total_ref,
            'payments': payments,
            'company_name': self.env.company.name,
            'taxes': list(taxes.values()),
            'commissions':dic,
            'products': sorted([{
                'product_id': product.id,
                'product_name': product.name,
                'code': product.default_code,
                'quantity': qty,
                'price_unit': price_unit,
                'price_unit_ref': price_unit_ref,
                'discount': discount,
                'uom': product.uom_id.name
            } for (product, price_unit,price_unit_ref, discount), qty in products_sold.items()], key=lambda l: l['product_name'])
        }
    
    @api.model
    def _get_report_values(self, docids, data=None):
        data = dict(data or {})
        session = self.env['pos.session'].browse(docids)
        data.update(self._get_report_values_session(session.start_at, session.stop_at, session.id))
        # docs = self.env[model].browse(self.env.context.get('active_ids', []))
        # return (data)
        return {
            'doc_ids': docids,
            'doc_model': 'pos.session',
            'docs': session,
            'data':data,
        }
