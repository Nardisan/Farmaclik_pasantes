# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools, _
from datetime import datetime, timedelta

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def autocancel_draft_sent_orders(self):
        config = self.env['ir.config_parameter'].sudo()
        autocancel_orders = config.get_param('sale.use_quotation_validity_days')
        if autocancel_orders:
            config_obj = self.env['res.config.settings']
            #days_default = config_obj.quotation_validity_days
            days_default = self.env.company.quotation_validity_days
            if not days_default:
                days_default = 5
            limit_date = datetime.now() - timedelta(days=days_default)
            draft_sales = self.env['sale.order'].search(
                [('state', 'in', ['draft', 'sent']), ('date_order', '<=', limit_date)])
            for sale in draft_sales:
                sale.state = 'cancel'
