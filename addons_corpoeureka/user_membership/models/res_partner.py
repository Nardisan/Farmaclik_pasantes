# -*- coding: utf-8 -*-

import datetime
import logging

from odoo import models, fields, api, _, SUPERUSER_ID

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    user_membership_id = fields.Many2one('user.membership', 'Applied Membership')
    user_membership_ids = fields.One2many('user.membership', 'partner_id', string='Memberships')
    is_membership_active = fields.Boolean(compute='compute_is_membership_active', store=True)
    is_membership_suspend = fields.Boolean()

    @api.depends('user_membership_id')
    def compute_is_membership_active(self):
        for rec in self:
            if rec.user_membership_id and rec.user_membership_id.state == 'active':
                rec.is_membership_active = True
            else:
                rec.is_membership_active = False

    def _remove_membership(self):
        cron_id = self.env.context.get('cron_id', False)
        cron_id = self.env['ir.cron'].sudo().search([('id', '=', cron_id)])
        partner_id = cron_id.partner_id
        if partner_id.user_membership_id:
            if partner_id.user_membership_id.to_date.date() <= datetime.datetime.now().date():
                if partner_id.user_membership_id:
                    partner_id.start_new_membership_plan(partner_id=partner_id)
                    # cron_id.active = False
            else:

                partner_id.user_membership_id.send_mail(is_reminder=True)

    def membership_states(self):
        user_membership_ids = self.env['user.membership'].with_user(SUPERUSER_ID).search(
            [('partner_id', '=', self.id), ('to_date', '<', datetime.datetime.now()),
             ('state', 'not in', ['expire', 'cancel'])])
        for user_membership_id in user_membership_ids:
            user_membership_id.state = 'expire'
        user_membership_ids = self.env['user.membership'].with_user(SUPERUSER_ID).search(
            [('partner_id', '=', self.id), ('to_date', '>', datetime.datetime.now()),
             ('state', 'not in', ['expire', 'cancel', 'suspend']), ('from_date', '<', datetime.datetime.now())])
        for user_membership_id in user_membership_ids:
            user_membership_id.state = 'suspend'
        if self.user_membership_id:
            self.user_membership_id.with_user(SUPERUSER_ID).state = 'active'

            if self.user_membership_id.user_membership_plan_id.is_pricelist and self.is_membership_active and not self.is_membership_suspend:
                self.property_product_pricelist = self.user_membership_id.user_membership_plan_id.pricelist_id.id
            else:

                ir_property_id = self.env['ir.property'].sudo().search(
                    [("name", "=", "property_product_pricelist"), ("res_id", "=", "res.partner," + str(self.id)),
                     ("value_reference", "=",
                      "product.pricelist," + str(self.property_product_pricelist.id))])
                if ir_property_id:
                    ir_property_id.sudo().unlink()

                self.property_product_pricelist = False

            if self.user_membership_id.user_membership_plan_id.is_delivery and self.is_membership_active and not self.is_membership_suspend:
                self.property_delivery_carrier_id = self.user_membership_id.user_membership_plan_id.carrier_id.id
            else:
                self.property_delivery_carrier_id = False
        else:
            ir_property_id = self.env['ir.property'].sudo().search(
                [("name", "=", "property_product_pricelist"), ("res_id", "=", "res.partner," + str(self.id)),
                 ("value_reference", "=", "product.pricelist," + str(self.property_product_pricelist.id))])
            if ir_property_id:
                ir_property_id.sudo().unlink()
            self.property_product_pricelist = False
            self.property_delivery_carrier_id = False

    def mem_suspend_remove(self):

        self.start_new_membership_plan()
        if self.user_membership_id and self.user_membership_id.state != 'suspend':
            self.is_membership_suspend = False

    def start_new_membership_plan(self, partner_id=None):
        if not partner_id:
            partner_id = self
        user_membership_id = self.env['user.membership'].search(
            [('partner_id', '=', partner_id.id), ('to_date', '>', datetime.datetime.now()), ('state', '!=', 'cancel')],
            limit=1)

        if user_membership_id:
            if partner_id.user_membership_id:

                if partner_id.user_membership_id.to_date < datetime.datetime.now():
                    partner_id.user_membership_id = user_membership_id.id
            else:
                partner_id.user_membership_id = user_membership_id.id
        else:
            partner_id.user_membership_id = False
        self.membership_states()
        if self.user_membership_id:
            if self.user_membership_id.partner_id not in self.user_membership_id.message_partner_ids:
                self.user_membership_id.message_subscribe([self.user_membership_id.partner_id.id])
            self.user_membership_id.with_user(SUPERUSER_ID).send_mail(
                templateid='user_membership.user_membership_modification_email_template')

    def _unlink_cron(self):
        cron_ids = self.env['ir.cron'].sudo().search(
            [('is_membership', '=', True), ('active', '=', False), ('nextcall', '<', datetime.datetime.now()),
             ('numbercall', '=', 0)])

        for cron_id in cron_ids:
            cron_id.unlink()
