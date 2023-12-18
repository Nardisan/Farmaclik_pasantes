# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    currency_id_dif = fields.Many2one(related="currency_id.parent_id",
        string="Moneda Referencia",store=True)
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company.id,
        )
    tasa_del_dia = fields.Float("Tasa del día", compute="_compute_tasa_del_dia")


    @api.depends('currency_id','currency_id_dif')
    def _compute_tasa_del_dia(self):
        for rec in self:
            rec.tasa_del_dia    =   0.0
            if rec.currency_id_dif:
                if rec.currency_id_dif.name == 'USD': 
                    rec.tasa_del_dia = rec.currency_id_dif._convert(1, rec.currency_id, self.env.company, fields.date.today())
                if rec.currency_id_dif.name == 'VES' or rec.currency_id_dif.name == 'VEF': 
                    rec.tasa_del_dia = rec.currency_id._convert(1, rec.currency_id_dif, self.env.company, fields.date.today())


class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    currency_id_dif = fields.Many2one(related="pricelist_id.currency_id.parent_id",
        string="Moneda Referencia",)
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company.id,
        )

    fixed_price_ref = fields.Float('Precio Referencia', digits='Product Price',compute="_compute_fixed_price_ref")

    @api.depends('fixed_price', 'currency_id','currency_id_dif','company_id')
    def _compute_fixed_price_ref(self):
        for record in self:
            record[("fixed_price_ref")] = record.currency_id._convert(record['fixed_price'], record.currency_id_dif, self.env.company , fields.Date.today())