# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    retention_iva_account_id = fields.Many2one('account.account',
                                               related='company_id.purchase_iva_ret_account',
                                               help="Account for defects for the retention of the IVA Suplier",
                                               readonly=False)
    sale_iva_ret_account_id = fields.Many2one('account.account',
                                              related='company_id.sale_iva_ret_account',
                                              help="Account for defects for the retention of the IVA Customer",
                                              readonly=False)
    journal_iva = fields.Many2one('account.journal',related='company_id.journal_iva', string='Diario del IVA',readonly=False)