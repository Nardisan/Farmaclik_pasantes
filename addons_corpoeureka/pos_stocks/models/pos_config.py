# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
# 
#################################################################################
from  odoo import fields,models,api
import logging
_logger = logging.getLogger(__name__)

class PosConfig(models.Model):
    _inherit = 'pos.config'
    
    wk_display_stock =  fields.Boolean('Display stock in POS',default=True)
    wk_stock_type = fields.Selection([('available_qty', 'Available Quantity(On hand)'), ('forecasted_qty', 'Forecasted Quantity'), ('virtual_qty', 'Quantity on Hand - Outgoing Qty')],string='Stock Type',default='available_qty')
    wk_continous_sale = fields.Boolean('Allow Order When Out-of-Stock')
    wk_deny_val = fields.Integer('Deny order when product stock is lower than ')
    wk_error_msg = fields.Char(string='Custom message',default="Product out of stock")
    wk_hide_out_of_stock = fields.Boolean(string="Hide Out of Stock products",default=True)

    @api.model
    def wk_pos_fetch_pos_stock(self,kwargs):
        result = {}
        location_id = False
        wk_stock_type = kwargs['wk_stock_type']
        wk_hide_out_of_stock = kwargs['wk_stock_type']
        config_id = self.browse([kwargs.get('config_id')])
        picking_type = config_id.picking_type_id
        location_id = picking_type.default_location_src_id.id
        product_obj = self.env['product.product']
        pos_products = product_obj.search([('type', '=', 'product'),('sale_ok', '=', True),('available_in_pos', '=', True)])
        pos_products_qtys = pos_products.with_context(location=location_id)._product_available()
        for pos_product in pos_products_qtys:
            if wk_stock_type == 'available_qty':
                result[pos_product] = pos_products_qtys[
                    pos_product]['qty_available']
            elif wk_stock_type == 'forecasted_qty':
                result[pos_product] = pos_products_qtys[
                    pos_product]['virtual_available']
            else:
                result[pos_product] = pos_products_qtys[pos_product][
                    'qty_available'] - pos_products_qtys[pos_product]['outgoing_qty']
        print("PRODUCTOS DE LA BUSQUEDA",len(pos_products_qtys))
        return result