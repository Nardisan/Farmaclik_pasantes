# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    type_name = fields.Char('Type Name', compute='_compute_type_name')
    signature = fields.Image('Signature', copy=False, attachment=True,
                             max_width=1024, max_height=1024,
                              help='Signature received through the portal.')
    signed_by = fields.Char('Signed By', copy=False,
                            help='Name of the person that signed the SO.')
    signed_on = fields.Datetime('Signed On', help='Date of the signature.',
                                copy=False)

    def preview_purchase_order(self):
        """
        Preview the request for quotation directly on a web interface
        """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': self.get_portal_url(),
        }
    def _get_portal_return_action(self):
        """ Return the action used to display orders when returning from supplier portal. """
        self.ensure_one()
        return self.env.ref('purchase.purchase_rfq')

    @api.depends('state')
    def _compute_type_name(self):
        for record in self:
            record.type_name = _('Quotation') if record.state in (
                'draft', 'sent', 'cancel') else _('Purchase Order')

    def _get_report_base_filename(self):
        self.ensure_one()
        return '%s %s' % (self.type_name, self.name)
