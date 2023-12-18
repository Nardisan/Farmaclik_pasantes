# -*- coding: utf-8 -*-

import datetime
import logging

from dateutil.relativedelta import relativedelta

from odoo import models, fields, SUPERUSER_ID

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        line_id = self.order_line.filtered(lambda line: line.product_id.product_tmpl_id.is_membership)
        line_count = len(line_id)
        if line_count == 1:
            self.check_membership_product(line_id)
        return res

    def delivery(self):
        delivery_wizard = self.env['choose.delivery.carrier'].with_context({
            'default_order_id': self.sale_normal_delivery_charges.id,
            'default_carrier_id': self.normal_delivery.id
        })
        choose_delivery_carrier = delivery_wizard.save()
        choose_delivery_carrier.button_confirm()

    def only_membership_line(self):
        only_membership_line = False
        if len(self.order_line) == 1 and self.order_line.product_id.product_tmpl_id.is_membership:
            only_membership_line = True
        return only_membership_line

    def validate_membership_order(self):
        line_id = self.order_line.filtered(lambda line: line.product_id.product_tmpl_id.is_membership)
        line_count = len(line_id)
        if line_count == 1:
            active_membership_id = self.env['user.membership'].search(
                [('partner_id', '=', self.partner_id.id), ('state', '=', 'active')], limit=1)
            advanced_booked_membership_id = self.env['user.membership'].search(
                [('partner_id', '=', self.partner_id.id), ('state', '=', 'suspend')], limit=1)

            if active_membership_id and not advanced_booked_membership_id:
                if active_membership_id.user_membership_plan_id.reminder_before_range == 'day':
                    reminder_time = datetime.datetime.now() + datetime.timedelta(
                        days=active_membership_id.user_membership_plan_id.reminder_before)
                elif active_membership_id.user_membership_plan_id.reminder_before_range == 'week':
                    reminder_time = datetime.datetime.now() + datetime.timedelta(
                        weeks=active_membership_id.user_membership_plan_id.reminder_before)
                elif active_membership_id.user_membership_plan_id.reminder_before_range == 'month':
                    reminder_time = datetime.datetime.now() + relativedelta(
                        months=active_membership_id.user_membership_plan_id.reminder_before)
                else:
                    reminder_time = datetime.datetime.now() + datetime.timedelta(days=0)
                    self.partner_id.start_new_membership_plan(self.partner_id)
                if active_membership_id.to_date > reminder_time:
                    return {'error': (
                            "Your membership '%s' is already active. Can't order for a new  until you receive a expiry "
                            "reminder for the active membership" % (
                                active_membership_id.name))}

            elif active_membership_id and advanced_booked_membership_id:
                return {'error': (
                        "%s already purchase a membership '%s' and a membership '%s' is active currently." % (
                    self.partner_id.name, advanced_booked_membership_id.name, active_membership_id.name))}
        elif line_count > 1:
            return {'error': "You can't purchase multiple types of membership!"}

    def check_membership_product(self, line_id):
        from_date = datetime.datetime.now()
        if self.partner_id.is_membership_active and self.partner_id.user_membership_id:
            from_date = self.partner_id.user_membership_id.to_date

        try_duration = datetime.timedelta(days=0)
        has_trial = line_id.product_id.product_tmpl_id.user_membership_plan_id.has_trial
        if self.partner_id.user_membership_ids:
            same_plan_ids = self.partner_id.user_membership_ids.filtered(lambda
                                                                             line: line.user_membership_plan_id.id == line_id.product_id.product_tmpl_id.user_membership_plan_id.id)
            if same_plan_ids and any(trial_duration > 0 for trial_duration in same_plan_ids.mapped("duration")):
                has_trial = False
        if has_trial:
            if line_id.product_id.product_tmpl_id.user_membership_plan_id.duration_range == 'day':
                try_duration = datetime.timedelta(
                    days=line_id.product_id.product_tmpl_id.user_membership_plan_id.duration)
                from_date = datetime.datetime.now() + try_duration
            elif line_id.product_id.product_tmpl_id.user_membership_plan_id.duration_range == 'week':
                try_duration = datetime.timedelta(
                    weeks=line_id.product_id.product_tmpl_id.user_membership_plan_id.duration)
                from_date = datetime.datetime.now() + try_duration
            elif line_id.product_id.product_tmpl_id.user_membership_plan_id.duration_range == 'month':
                try_duration = relativedelta(
                    months=line_id.product_id.product_tmpl_id.user_membership_plan_id.duration)
                from_date = datetime.datetime.now() + try_duration

        if line_id.product_id.duration_range == 'day':
            to_date = datetime.datetime.now() + datetime.timedelta(days=line_id.product_id.duration_value)
        elif line_id.product_id.duration_range == 'week':
            to_date = datetime.datetime.now() + datetime.timedelta(weeks=line_id.product_id.duration_value)
        elif line_id.product_id.duration_range == 'month':
            to_date = datetime.datetime.now() + relativedelta(months=line_id.product_id.duration_value)

        to_date += try_duration
        membership_id = self.env['user.membership'].with_user(SUPERUSER_ID).create({
            'from_date': from_date,
            'to_date': to_date,
            'amount': line_id.price_subtotal,
            'currency_id': line_id.currency_id.id,
            'partner_id': self.partner_id.id,
            'sales_user_id': self.user_id.id,
            # 'user_id': self.env['res.users'].search([('partner_id', '=', self.partner_id.id)]).id,
            'product_id': line_id.product_id.id,
            'tax_ids': line_id.tax_id.ids,
            'user_membership_plan_id': line_id.product_id.product_tmpl_id.user_membership_plan_id.id,

            'duration_range': has_trial and line_id.product_id.product_tmpl_id.user_membership_plan_id.duration_range,
            'duration': has_trial and line_id.product_id.product_tmpl_id.user_membership_plan_id.duration,
        })

        reminder_before = line_id.product_id.product_tmpl_id.user_membership_plan_id.reminder_before
        reminder_before_range = line_id.product_id.product_tmpl_id.user_membership_plan_id.reminder_before_range
        membership_id.send_mail()
        line_id.order_id.partner_id.user_membership_ids = [(4, membership_id.id, 0)]

        if reminder_before_range == 'day':
            to_date_cron = to_date - datetime.timedelta(days=reminder_before)
        elif reminder_before_range == 'week':
            to_date_cron = to_date - datetime.timedelta(weeks=reminder_before)
        elif reminder_before_range == 'month':
            to_date_cron = to_date - relativedelta(months=reminder_before)

        numbercall = to_date_cron
        values = {
            'name': 'Cron for ' + membership_id.name,
            'model_id': self.env.ref("base.model_res_partner").id,
            'state': 'code',
            'active': True,
            'code': 'model._remove_membership()',
            'user_id': SUPERUSER_ID,
            'partner_id': self.partner_id.id,
            'interval_number': 1,
            'interval_type': reminder_before_range + 's',
            'nextcall': numbercall,
            'numbercall': reminder_before + 1,
            'doall': False,
            'is_membership': True,
        }
        self.env['ir.cron'].with_user(SUPERUSER_ID).create(values)
        self.partner_id.start_new_membership_plan(self.partner_id)

    def _get_delivery_methods_as_membership(self):
        address = self.partner_shipping_id
        domain = ['&', ('website_published', '=', True), ('user_membership_plan_id', '=', False)]
        if self.partner_id.user_membership_id:
            domain.remove(('user_membership_plan_id', '=', False))
            domain.append('|')
            domain.append(('user_membership_plan_id', '=', False))
            domain.append(
                ('user_membership_plan_id', '=', self.partner_id.user_membership_id.user_membership_plan_id.id))
        return self.env['delivery.carrier'].sudo().search(domain).available_carriers(address)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_membership = fields.Boolean(string='Membership')

    def write(self, vals):
        if self.product_id.product_tmpl_id.is_membership:
            vals.update(is_membership=True)
        return super(SaleOrderLine, self).write(vals)
