# -*- coding: utf-8 -*-

import time
from datetime import timedelta, datetime
from odoo import models, api,fields, _
from odoo.exceptions import UserError
import pytz
import datetime

class ReportAccountHashIntegrity(models.AbstractModel):
    _name = 'report.l10n_ve_accountant.report_sales_book'
    _description = 'Libro de Ventas'

    def _get_account_move_entry(self, accounts, form_data, sortby, pass_date, display_account):
        cr = self.env.cr
        move_line = self.env['account.move.line']

        tables, where_clause, where_params = move_line._query_get()
        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        if form_data['target_move'] == 'posted':
            target_move = "AND m.state = 'posted'"
        else:
            target_move = ''
        sql = ('''
                SELECT l.id AS lid, acc.name as accname, l.account_id AS account_id, l.date AS ldate, j.code AS lcode, l.currency_id, 
                l.amount_currency, l.ref AS lref, l.name AS lname, COALESCE(l.debit,0) AS debit, COALESCE(l.credit,0) AS credit, 
                COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) AS balance,
                m.name AS move_name, c.symbol AS currency_code, p.name AS partner_name
                FROM account_move_line l
                JOIN account_move m ON (l.move_id=m.id)
                LEFT JOIN res_currency c ON (l.currency_id=c.id)
                LEFT JOIN res_partner p ON (l.partner_id=p.id)
                JOIN account_journal j ON (l.journal_id=j.id)
                JOIN account_account acc ON (l.account_id = acc.id) 
                WHERE l.account_id IN %s AND l.journal_id IN %s ''' + target_move + ''' AND l.date = %s
                GROUP BY l.id, l.account_id, l.date,
                     j.code, l.currency_id, l.amount_currency, l.ref, l.name, m.name, c.symbol, p.name , acc.name
                     ORDER BY l.date DESC
        ''')
        params = (
            tuple(accounts.ids), tuple(form_data['journal_ids']), pass_date)
        cr.execute(sql, params)
        data = cr.dictfetchall()
        res = {}
        debit = credit = balance = 0.00
        for line in data:
            debit += line['debit']
            credit += line['credit']
            balance += line['balance']
        res['debit'] = debit
        res['credit'] = credit
        res['balance'] = balance
        res['lines'] = data
        return res

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form') or not self.env.context.get('active_model'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        sortby = data['form'].get('sortby')
        in_bs = data['form'].get('in_bs')
        form_data = data['form']
        #branch_ids = data['form'].get('branch_ids',False)
        target_mov = ('posted','cancel') if form_data['target_move'] =='posted' else ('draft','cancel','posted')
        currency_id = self.env['res.currency'].browse([form_data['currency_id'][0]])
        company_id = self.env.company
        active_acc = data['form']['account_ids']
        accounts = self.env['account.account'].search(
            [('id', 'in', active_acc)]) if data['form']['account_ids'] else \
            self.env['account.account'].search([])
        date_start = datetime.datetime.strptime(form_data['date_from'],'%Y-%m-%d')
        date_end = datetime.datetime.strptime(form_data['date_to'], '%Y-%m-%d')
        docs_ret = self.env['account.wh.iva'].search([('move_type', 'in', ('out_invoice', 'out_refund'))])
        docs_fac = self.env['account.move'].search([('move_type', 'in', ('out_refund', 'out_invoice')),
                                                     ('date', '<=', date_end),
                                                     ('date', '>=', date_start),
                                                     #('currency_id', '=', currency_id.id),
                                                     ('state', 'in', target_mov),
                                                     #('branch_id', 'in', (branch_ids)),
                                                     ('journal_id', 'in', form_data['journal_ids'])]).sorted(key=lambda x: x.journal_id.id and x.partner_id.name if sortby == 'sort_journal_partner' else x.date).filtered(lambda c: c.line_ids.mapped('account_id') & accounts != self.env['account.account'])
        rete = self.env['account.wh.iva.line'].search([
                                        ('retention_id.date', '>=', date_start),
                                        ('retention_id.date', '<=', date_end),
                                        ('retention_id.move_type', 'in', ('out_invoice','out_refund')),
                                        ('state', 'not in', ('draft','anulled')),
                                        ('retention_id.company_id','=',self.env.company.id),
                                        ])
        con_documento = True
        model = self.env.context.get('active_model')
        codes = []
        if data['form'].get('journal_ids', False):
            codes = [journal.code for journal in
                     self.env['account.journal'].search(
                         [('id', 'in', data['form']['journal_ids'])])]
        #branch = []
        #if branch_ids:
        #    branch = [branch.name for branch in
        #             self.env['res.branch'].search(
        #                 [('id', 'in', branch_ids)])]
        if not docs_fac:
            con_documento = False
            return {
                'doc_ids': docids,
                'doc_model': model,
                'data': data['form'],
                'docs': docs_ret,
                'rete': rete,
                'fact': False,
                'Accounts': False,
                'print_journal': codes,
                #'branch': branch,
                'currency_id': currency_id,
                'company_id': company_id,
                'company_vat':  company_id.vat[:10]+'-'+company_id.vat[10:] if company_id.vat else False,
                'in_bs':in_bs,
                'con_documento': con_documento,
            }
        
        display_account = 'movement'
        dates = []
        record = []
        for head in dates:
            pass_date = str(head)
            accounts_res = self.with_context(
                data['form'].get('used_context', {}))._get_account_move_entry(
                accounts, form_data, sortby,pass_date, display_account)
            if accounts_res['lines']:
                record.append({
                    'date': head,
                    'debit': accounts_res['debit'],
                    'credit': accounts_res['credit'],
                    'balance': accounts_res['balance'],
                    'child_lines': accounts_res['lines']
                })
        hora_printer = (datetime.datetime.now()).astimezone(pytz.timezone(self.env.user.tz)).strftime('%I:%M:%S %p')
        return {
            'doc_ids': docids,
            'doc_model': model,
            'data': data['form'],
            'docs': docs_ret,
            'rete': rete,
            'fact': docs_fac,
            'time': time,
            'hora_printer': hora_printer,
            'Accounts': record,
            'print_journal': codes,
            #'branch': branch,
            'currency_id': currency_id,
            'company_id': company_id,
            'company_vat':  company_id.vat[:10]+'-'+company_id.vat[10:] if company_id.vat else False,
            'in_bs':in_bs,
            'con_documento': con_documento,
        }