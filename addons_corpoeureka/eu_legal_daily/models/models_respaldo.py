# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
from pytz import timezone
import math
from odoo.exceptions import UserError
import operator



class AccountReportLegal(models.TransientModel):
    _name = 'account.report.legal'
    _description = "Legal Daily Report"

    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.company)
    fiscalyear_id = fields.Many2one('account.fiscal.year', string='Fiscal Year')
    date_from = fields.Date(string='Start Date')
    date_to = fields.Date(string='End Date')
    target_move = fields.Selection([('posted', 'All Posted Entries'),
                                    ('all', 'All Entries'),
                                    ], string='Target Moves', required=True,
                                    default='posted')
    display_account = fields.Selection([('all', 'All'),
                                        ('movement', 'With movements'),
#                                     ('not_zero', 'With balance is not equal to 0'), 
                                        ],
                                        string='Display Accounts', required=True, 
                                        default='all')
    unfold = fields.Boolean('Auto Unfold')
    report_type = fields.Selection([('account','Accounts'),
                                    ('account_type','Account Type'),
                                     ],'Hierarchy based on', default = 'account',
        help="If you haven't configured parent accounts, then use 'Account Type'")
    #show_initial_balance = fields.Boolean(string='Show Initial Balance')

    @api.onchange('fiscalyear_id')
    def onchange_fiscalyear(self):
        self.date_from = self.fiscalyear_id.date_from
        self.date_to = self.fiscalyear_id.date_to

    @api.onchange('date_to')
    def onchange_date_to(self):
        if self.date_from and self.date_to and self.date_to < self.date_from:
            raise UserError(_('End date must be greater than start date!'))


    def print_report(self):
        domain = []
        datas = []
        arreglo = []
        num         = 0
        total       = 0
        iva         = 0
        basei       = 0
        amount_tax  = 0
        basegravada = 0

        
        invoice = self.env["account.move.line"].search(
        [
        ('parent_state', '=', 'posted'), 
        ('date', '>=', self.date_from),
        ('company_id', '=', self.company_id.id),
        ('date', '<=', self.date_to),
        ],
        order='account_id asc')
        if not invoice:
            raise UserError('No se encontraron registros durante el periodo seleccionado.')
        for invoices in invoice:
            if invoices.account_id.code not in arreglo:
                arreglo.append(invoices.account_id.code)
        for id in arreglo:
            account_code = 0
            debit = 0
            credit = 0
            account_name = 0
            balance = 0
            for invoices in invoice:
                if id==invoices.account_id.code:
                    account_code = invoices.account_id.code
                    account_name = invoices.account_id.name
                    debit += invoices.debit
                    credit += invoices.credit
                    balance += (invoices.debit - invoices.credit)
            datas.append({
                        'account_code':     account_code,
                        'debit':            debit,
                        'credit':           credit,
                        'account_name':     account_name,
                        'balance':          balance,
                        })

        datas = sorted(datas, key= operator.itemgetter('account_code'), reverse=False)       
        res = {
            'start_date':           self.date_from,
            'end_date':             self.date_to,
            'company_name':         self.company_id.name,
            'company_vat':          self.company_id.vat[:10] if self.company_id.vat else ''+'-'+self.company_id.vat[10:] if self.company_id.vat else '',
            'invoices':             datas,
        }
        data = {
            'form': res,
        }
        return self.env.ref('eu_legal_daily.eu_legal_daily').report_action([],data=data)
