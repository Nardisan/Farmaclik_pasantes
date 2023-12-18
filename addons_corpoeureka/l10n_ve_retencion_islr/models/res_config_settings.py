# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    retention_islr_account_id = fields.Many2one('account.account',
                                               related='company_id.purchase_islr_ret_account_id',
                                               help="Account for defects for the retention of the ISLR Supplier",
                                               readonly=False)
    sale_islr_ret_account_id = fields.Many2one('account.account',
                                              related='company_id.sale_islr_ret_account_id',
                                              help="Account for defects for the retention of the ISLR Customer",
                                              readonly=False)
    journal_islr = fields.Many2one('account.journal',related='company_id.journal_islr', string='Diario del ISLR',readonly=False)
