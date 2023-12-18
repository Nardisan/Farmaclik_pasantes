# -*- coding: utf-8 -*-
from odoo import models, fields, api
from bs4 import BeautifulSoup
from datetime import date
from datetime import datetime
import requests

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    def _set_currency_usd_id(self):
        usd = self.env.ref('base.USD')
        return usd

    list_price_usd = fields.Float('Sale Price USD', digits='Product Price', required=True, default=0.0)
    currency_usd_id = fields.Many2one('res.currency', 'USD',default=_set_currency_usd_id)
    
class ProductTemplateAttributeValue(models.Model):
    _inherit = 'product.template.attribute.value'

    def _set_currency_usd_id(self):
        usd = self.env.ref('base.USD')
        return usd

    list_price_usd = fields.Float('Valor Precio Extra $', digits='Product Price', required=True, default=0.0)
    currency_usd_id = fields.Many2one('res.currency', 'USD',default=_set_currency_usd_id)
