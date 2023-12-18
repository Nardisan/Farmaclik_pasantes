# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.exceptions import UserError
from odoo.tools.misc import formatLang


class ReportAccountSaleJournal(models.AbstractModel):
    _name = 'report.sale_invoice_ledger2'

    @api.model
    def render_html(self, docids, data=None):
        docs = self.env[data['model']].browse(data['docs_ids'])
        docargs = {
            'doc_ids': data['docs_ids'],
            'doc_model': data['model'],
            'data': data['form'],
            'docs': docs,
            'time': time,
            'formatlang': formatLang,
            'self': self,
            'get_withheld_tax': self.get_withheld_tax,
        }
        return self.env['report'].render('l10n_ve_account_SH.sale_invoice_ledger2', docargs)


    @api.model
    def get_withheld_tax(self,wh_lines):
        return sum(wh_lines.mapped('ret_amount'))

    @api.model
    def get_tax(self,tax_ids):
        print (tax_ids)

        return '16 %'
