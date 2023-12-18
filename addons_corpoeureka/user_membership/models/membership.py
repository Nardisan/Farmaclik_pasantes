# -*- coding: utf-8 -*-

import logging

import pytz

from odoo import models, fields, api
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class UserMembership(models.Model):
    _name = 'user.membership'
    _order = 'id desc'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = "User Website Membership"

    name = fields.Char(default=lambda self: self.env['ir.sequence'].sudo().next_by_code('ums.sequence'), readonly=True,
                       states={'draft': [('readonly', False)]}, )
    counts_of_plan = fields.Integer(default=1)
    duration_report = fields.Float(compute='_compute_duration', string='Duration in Months', store=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('active', 'Active'), ('cancel', 'Cancel'), ('expire', 'Expire'), ('suspend', 'Suspend')],
        default='draft', track_visibility="onchange")
    from_date = fields.Datetime(states={'draft': [('readonly', False)]}, readonly=True, )
    to_date = fields.Datetime(states={'draft': [('readonly', False)]}, readonly=True, )
    amount = fields.Monetary(states={'draft': [('readonly', False)]}, readonly=True, )
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    partner_id = fields.Many2one('res.partner', states={'draft': [('readonly', False)]}, readonly=True, )
    user_id = fields.Many2one('res.users', states={'draft': [('readonly', False)]}, readonly=True, )
    sales_user_id = fields.Many2one('res.users', states={'draft': [('readonly', False)]}, readonly=True, )
    product_id = fields.Many2one('product.product', states={'draft': [('readonly', False)]}, readonly=True, )
    tax_ids = fields.Many2many('account.tax', states={'draft': [('readonly', False)]}, readonly=True, )
    user_membership_plan_id = fields.Many2one('user.membership.plan', states={'draft': [('readonly', False)]},
                                              readonly=True, )
    duration_range = fields.Selection([('day', 'Day'), ('week', 'Week'), ('month', 'Month')],
                                      states={'draft': [('readonly', False)]}, readonly=True, )
    duration = fields.Integer(states={'draft': [('readonly', False)]}, readonly=True, )
    cancel_reason = fields.Text("Reason for Cancellation", states={'cancel': [('readonly', False)]}, readonly=True, )

    def unlink(self):
        for order in self:
            if order.state not in ['cancel', 'expire']:
                raise ValidationError("You can delete membership after cancel or expire.")
        return super(UserMembership, self).unlink()

    def _compute_access_url(self):
        super(UserMembership, self)._compute_access_url()
        for membership in self:
            membership.access_url = '/my/membership/%s' % membership.id

    @api.depends('from_date', 'to_date')
    def _compute_duration(self):
        for rec in self:
            if rec.to_date - rec.from_date:
                duration = round((rec.to_date - rec.from_date).total_seconds())
                duration = round((((duration / 60) / 60) / 24) / 30, )

                rec.duration_report = duration
            else:
                rec.duration_report = False

    def format_date_only(self, date=None):
        user_time_zone = self.env.user.tz or 'UTC'
        user_time_zone = pytz.timezone(user_time_zone)
        utc_time_zone = pytz.timezone('UTC')
        utc_datetime = utc_time_zone.localize(date)
        user_datetime = utc_datetime.astimezone(user_time_zone).replace(tzinfo=None)

        date_format = self.env['res.lang']._lang_get(self.env.user.lang).date_format
        time_format = self.env['res.lang']._lang_get(self.env.user.lang).time_format
        date_start = user_datetime.strftime(date_format or
                                            "%Y/%m/%d")
        return date_start

    def format_date(self, date=None):
        user_time_zone = self.env.user.tz or 'UTC'
        user_time_zone = pytz.timezone(user_time_zone)
        utc_time_zone = pytz.timezone('UTC')
        utc_datetime = utc_time_zone.localize(date)
        user_datetime = utc_datetime.astimezone(user_time_zone).replace(tzinfo=None)
        date_format = self.env['res.lang']._lang_get(self.env.user.lang).date_format
        time_format = self.env['res.lang']._lang_get(self.env.user.lang).time_format
        date_start = user_datetime.strftime(date_format + " " + time_format or
                                            "%Y/%m/%d_%H:%M:%S")
        return date_start

    def mem_suspend(self):
        self.state = 'suspend'
        self.partner_id.user_membership_id = False
        self.partner_id.is_membership_suspend = True

        ir_property_id = self.env['ir.property'].sudo().search(
            [("name", "=", "property_product_pricelist"), ("res_id", "=", "res.partner," + str(self.partner_id.id)),
             ("value_reference", "=", "product.pricelist," + str(self.partner_id.property_product_pricelist.id))])
        if ir_property_id:
            ir_property_id.sudo().unlink()

        self.partner_id.property_product_pricelist = False
        self.partner_id.property_delivery_carrier_id = False

        self.send_mail(templateid='user_membership.user_membership_modification_email_template')

    def mem_cancel(self):
        self.state = 'cancel'
        self.partner_id.user_membership_id = False

        ir_property_id = self.env['ir.property'].sudo().search(
            [("name", "=", "property_product_pricelist"), ("res_id", "=", "res.partner," + str(self.partner_id.id)),
             ("value_reference", "=", "product.pricelist," + str(self.partner_id.property_product_pricelist.id))])
        if ir_property_id:
            ir_property_id.sudo().unlink()

        self.partner_id.property_product_pricelist = False
        self.partner_id.property_delivery_carrier_id = False

    def send_mail(self, is_reminder=False, templateid=None):
        if templateid:
            template_id = self.env.ref(templateid).id
        elif is_reminder:
            template_id = self.env.ref('user_membership.user_membership_reminder_email_template').id
        else:
            template_id = self.env.ref('user_membership.user_membership_email_template').id
        template = self.env['mail.template'].sudo().browse(template_id)
        partners = [self.partner_id.id]
        email_values = {'recipient_ids': partners}
        template.browse(template_id).send_mail(self.id, force_send=True, email_values=email_values)


class UserMembershipPlan(models.Model):
    _name = 'user.membership.plan'
    _inherit = ['website.published.multi.mixin']
    _description = "Membership Plan"
    _order = 'sequence'

    sequence = fields.Integer(copy=False)
    name = fields.Char()
    carrier_id = fields.Many2one('delivery.carrier', 'Membership Delivery Carrier',
                                 domain="[('user_membership_plan_id','=',False)]", ondelete='cascade')

    product_template_id = fields.Many2one('product.template', copy=False)
    user_membership_plan_service_ids = fields.One2many('user.membership.plan.service', 'user_membership_plan_id')
    is_pricelist = fields.Boolean(string='Discounted Price', copy=False)
    is_exclusive_product = fields.Boolean(string='Exclusive Products', copy=False)
    is_delivery = fields.Boolean(string='Offer on Deliveries', copy=False)
    pricelist_id = fields.Many2one(
        'product.pricelist', string='Membership Pricelist', required=True,
        help="If you change the pricelist, only newly added lines will be affected.", copy=False)
    has_trial = fields.Boolean(copy=False)
    duration_range = fields.Selection([('day', 'Day'), ('week', 'Week'), ('month', 'Month')], default='day', copy=False)
    duration = fields.Integer(help="Set duration 0 when no trial.", copy=False)

    reminder_before = fields.Integer(help="Expire reminder before", copy=False)
    reminder_before_range = fields.Selection([('day', 'Day'), ('week', 'Week'), ('month', 'Month')], default='day',
                                             copy=False)

    @api.onchange("has_trial")
    def set_trial(self):
        if not self.has_trial:
            self.duration = 0

    def website_publish_button(self):
        self.ensure_one()
        res = super(UserMembershipPlan, self).website_publish_button()
        if self.website_published:
            self.product_template_id.write({'website_published': True})
        else:
            self.product_template_id.write({'website_published': False})
        return res

    @api.onchange('carrier_id')
    def onchange_carrier_id(self):

        if self.carrier_id:
            self.carrier_id.is_published = True
            carrier_ids = self.env['delivery.carrier'].sudo().search(
                [('user_membership_plan_id', '=', self._origin.id)])
            for carrier_id in carrier_ids:
                carrier_id.user_membership_plan_id = False
            self.carrier_id.user_membership_plan_id = self._origin.id
        else:
            carrier_ids = self.env['delivery.carrier'].sudo().search(
                [('user_membership_plan_id', '=', self._origin.id)])
            for carrier_id in carrier_ids:
                carrier_id.user_membership_plan_id = False


class UserMembershipService(models.Model):
    _name = 'user.membership.plan.service'
    _description = "Membership Plan Services"

    name = fields.Char(required=1)
    desc = fields.Text()
    user_membership_plan_id = fields.Many2one('user.membership.plan')


class InheritDeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    user_membership_plan_id = fields.Many2one('user.membership.plan')


class IrCron(models.Model):
    _inherit = "ir.cron"

    is_membership = fields.Boolean(string='Membership')
    user_membership_plan_ids = fields.Many2many('user.membership.plan', string='Membership Plan')
    partner_id = fields.Many2one('res.partner')
    product_template_ids = fields.Many2many('product.template')

    def _callback(self, cron_name, server_action_id, job_id):
        """ to handle cron thread executed by Odoo."""
        self = self.with_context(cron_id=job_id)
        return super(IrCron, self)._callback(cron_name, server_action_id, job_id)

    def method_direct_trigger(self):
        """ to handle manual execution using the button."""
        for rec in self:
            rec = rec.with_context(cron_id=rec.id)
            super(IrCron, rec).method_direct_trigger()
        return True
