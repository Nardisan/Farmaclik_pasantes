# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################

from odoo import api, fields, models, _


class WebsiteOnpageCheckoutSettings(models.Model):
    _name='onepage.checkout.config'

    name = fields.Char(string="Nombre", translate=True)
    is_active = fields.Boolean(string="Active on website", copy=False)

    wk_billing_panel = fields.Boolean(string="Panel de información de facturación", default=True)
    wk_billing_panel_name = fields.Char(string="Panel Name", default="Datos de facturación")

    wk_shipping_panel = fields.Boolean(string="Panel de información de envío")
    wk_shipping_panel_name = fields.Char(string="Nombre del panel", default="Información de envío")

    wk_delivery_panel = fields.Boolean(string="Opción de entrega")
    wk_delivery_panel_name = fields.Char(string="Nombre del panel", default="Método de entrega", translate=True)

    wk_overview_and_payment_panel = fields.Boolean(string="Vista previa del pedido y método de pago", default=True)
    wk_overview_and_payment_panel_name = fields.Char(string="Nombre del panel", default="Vista previa del pedido y opción de pago", translate=True)
    
    wk_billing_required = fields.Many2many('billing.default.fields')
    wk_shipping_required = fields.Many2many('shipping.default.fields')

    @api.model
    def create_wizard(self):
        wizard_id = self.env['website.message.wizard'].create({'message':_("Currently a configuration setting for 'Website Onepage Checkout' is active. You can not active other configuration setting. So, If you want to deactive the previous active configuration setting and active new configuration then click on 'Deactive Previous And Active New' button else click on 'Cancel'.")})
        return {
            'name': _("Message"),
            'view_mode': 'form',
            'view_id': False,
            'res_model': 'website.message.wizard',
            'res_id': int(wizard_id.id),
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new'
            }

    
    def toggle_is_active(self):
        active_ids = self.search([('is_active', '=', True),('id', 'not in', [self.id])])
        for record in self:
            if active_ids:
                return self.create_wizard()
            record.is_active = not record.is_active

    @api.model
    def get_config_settings_values(self):
        """ this function retrn all configuration value for website onepage checkout module."""
        res = {}
        onepage_config_values = self.search([('is_active', '=', True)], limit=1)
        if onepage_config_values:
            res = {
                'wk_billing_panel': onepage_config_values.wk_billing_panel,
                'wk_billing_panel_name': onepage_config_values.wk_billing_panel_name,
                'wk_shipping_panel_name': onepage_config_values.wk_shipping_panel_name,
                'wk_shipping_panel': onepage_config_values.wk_shipping_panel,
                'wk_delivery_panel': onepage_config_values.wk_delivery_panel,
                'wk_delivery_panel_name': onepage_config_values.wk_delivery_panel_name,
                'wk_overview_and_payment_panel': onepage_config_values.wk_overview_and_payment_panel,
                'wk_overview_and_payment_panel_name': onepage_config_values.wk_overview_and_payment_panel_name
            }
        return res
