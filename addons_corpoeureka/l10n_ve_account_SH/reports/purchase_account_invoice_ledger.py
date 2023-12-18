# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.exceptions import UserError
from odoo.tools.misc import formatLang


class ReportPurchaseInvoiceLedger(models.AbstractModel):
    _name = 'report.purchase_invoice_ledger'

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
        }
        return self.env['report'].render('l10n_ve_account_SH.purchase_invoice_ledger', docargs)
