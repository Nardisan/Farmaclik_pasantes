# -*- coding: utf-8 -*-

from functools import partial
from odoo.tools import formatLang
from odoo import api, models, fields


class PurchaseLine(models.Model):
    _inherit = 'purchase.order.line'

   
    def formatted_price(self):
        """
        Return unit price in decimal accuracy formatted 
        """
        self.ensure_one()
        format_price = partial(formatLang, self.env,
                               digits=self.order_id.currency_id.decimal_places)
        price = self.price_unit
        return format_price(price)
