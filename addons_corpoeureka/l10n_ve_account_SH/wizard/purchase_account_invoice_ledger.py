# -*- coding: utf-8 -*-

from odoo import fields, models, _
from odoo.exceptions import UserError


class AccountReportGeneralLedger(models.TransientModel):
    _inherit = "account.common.report"
    _name = "purchase.account.invoice.ledger"
    _description = "General Purchase Invoice Ledger Report"


    def _print_report(self, data):
        data = data
        records = self.env['account.move'].search([('type','in',('in_invoice','in_refund')),
                                                      ('state', 'in', ('paid','open')),
                                                      ('invoice_date', '<=',data['form'].get('date_to')),
                                                      ('invoice_date', '>=',data['form'].get('date_from')),
                                                      ('transaction_type', 'not in',['04-ajuste','05-donacion']),
                                                      ],order='invoice_date ASC')
        records_adj = self.env['account.move'].search([('type','in',('in_invoice','in_refund')),
                                                      ('state', 'in', ('paid','open')),
                                                      ('ajust_date', '<=',data['form'].get('date_to')),
                                                      ('ajust_date', '>=',data['form'].get('date_from')),
                                                      ('transaction_type', 'in', ['04-ajuste']),],order='invoice_date ASC')
        data['model']= records._name
        data['docs_ids']= (records | records_adj).ids
        return self.env.ref('l10n_ve_account_SH.purchase_invoice_ledger').report_action(self, data=data)
