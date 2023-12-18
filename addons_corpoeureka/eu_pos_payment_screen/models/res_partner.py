# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    giftcard_ids = fields.One2many("aspl.gift.card", "customer_id")
    giftcard_amount = fields.Float(compute="_compute_giftcard_amount", store=True)
    portal_user_id = fields.Many2one("res.users", compute="_compute_portal_user_id")

    def _compute_portal_user_id(self):
        for rec in self:
            rec.portal_user_id = self.env["res.users"].search([("partner_id", "=", rec.id)])

    @api.depends("giftcard_ids")
    def _compute_giftcard_amount(self):
        for rec in self:
            rec.giftcard_amount = sum(
                rec.env["aspl.gift.card"] \
                    .search([('customer_id', '=', int(rec.id))]) \
                    .mapped("card_value")
            )
        
    def action_apply(self):
        self.env['res.partner'].check_access_rights('write')
        self.sudo().with_company(self.env.company)._create_user()
        self.with_context(active_test=False)._send_email()

    def _create_user(self):
        """ create a new user for wizard_user.partner_id
            :returns record of res.users
        """
        self.ensure_one()

        return self.env['res.users'].with_context(no_reset_password=True)._signup_create_user({
            'email': self.email,
            'login': self.email,
            'partner_id': self.id,
            'company_id': self.env.company.id,
            'company_ids': [(6, 0, self.env.company.ids)],
        })

    def _send_email(self):
        """ send notification email to a new portal user """
        if not self.env.user.email:
            raise UserError(_('You must have an email address in your User Preferences to send emails.'))

        # determine subject and body in the portal user's language
        template = self.env.ref('eu_pos_payment_screen.pos_mail_template')

        lang = self.env.user.lang

        portal_url = self.with_context(signup_force_type_in_url='', lang=lang) \
            ._get_signup_url_for_action()[self.id]

        self.signup_prepare()

        if template:
            template \
                .with_context(dbname=self._cr.dbname, portal_url=portal_url, lang=lang) \
                .send_mail(self.portal_user_id.id, force_send=True)
        else:
            raise UserError("No email template found for sending email to the portal user")

        return True
