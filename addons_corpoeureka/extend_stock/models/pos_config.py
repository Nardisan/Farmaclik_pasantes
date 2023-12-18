# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models

#SOLUCION DE ERROR QUE SE MOSTRA EN EL LOG DE PRODUCCION 
#EL CAMPO CURRENCY_ID AUNQUE ERA COMPUTADO NO ERA ALMACENABLE
class PosConfig(models.Model):
    _inherit = "pos.config"

    currency_id = fields.Many2one('res.currency', compute='_compute_currency', string="Currency", store=True)

    @api.depends('journal_id.currency_id', 'journal_id.company_id.currency_id', 'company_id', 'company_id.currency_id')
    def _compute_currency(self):
        for pos_config in self:
            if pos_config.journal_id:
                pos_config.currency_id = pos_config.journal_id.currency_id.id or pos_config.journal_id.company_id.currency_id.id
            else:
                pos_config.currency_id = pos_config.company_id.currency_id.id


    