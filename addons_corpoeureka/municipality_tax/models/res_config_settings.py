# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    account_ret_muni_payable_id = fields.Many2one('account.account',
                                               related='company_id.purchase_iae_ret_account',
                                               help="Cuenta por defecto de retención de IAE a Proveedores (Compra)",
                                               readonly=False)
    account_ret_muni_receivable_id = fields.Many2one('account.account',
                                              related='company_id.sale_iae_ret_account',
                                              help="Cuenta por defecto de retencion de IAE en Clientes (Venta)",
                                              readonly=False)
    purchase_jrl_id = fields.Many2one('account.journal',related='company_id.journal_iae', string='Diario de Retenciones de IAE',readonly=False)