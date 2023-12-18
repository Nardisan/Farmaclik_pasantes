# -*- coding: utf-8 -*-

#from datetime import date, datetime, time
#from pytz import timezone

from dateutil.relativedelta import relativedelta
import math
import operator

import time
from datetime import timedelta, datetime, date

from odoo import models, api, fields, _
from odoo.exceptions import ValidationError, UserError
import xlsxwriter
import base64
from io import BytesIO
import pytz

class AccountReportLegalXls(models.TransientModel):
    _name = 'account.report.legal.xls'
    _description = "Legal Daily Report Excel"

    company_id = fields.Many2one('res.company', string='Compañia', required=True,
                                 default=lambda self: self.env.company)
    fiscalyear_id = fields.Many2one('account.fiscal.year', string='Año fiscal')
    date_from = fields.Date(string='Fecha inicio')
    date_to = fields.Date(string='Fecha fin')
    target_move = fields.Selection([('posted', 'Entradas publicadas'),
                                    ('all', 'Todas las entradas'),
                                    ], string='Movimientos', required=True,
                                    default='posted')
    display_account = fields.Selection([('all', 'Todas'),
                                        ('movement', 'Con movimientos'),
                                        ],
                                        string='Mostrar cuentas', required=True, 
                                        default='all')
    show_initial_balance = fields.Boolean(string='Mostrar saldo inicial (Libro Mayor)')

    parent_1 = fields.Many2one('account.account', string='Grupo desde',)
    parent_2 = fields.Many2one('account.account', string='Grupo hasta',)

    name = fields.Char(string='Nombre del Archivo', readonly=True)
    data = fields.Binary(string='Archivo', readonly=True)
    states = fields.Selection([
        ('choose', 'choose'), 
        ('get', 'get')], 
        default='choose')

    @api.model
    def default_get(self, default_fields):
        vals = super(AccountReportLegalXls, self).default_get(default_fields)
        vals['states'] = 'choose'
        return vals

    def go_back(self):
        self.states = 'choose'
        return {
            'name': 'Diario Legal Excel',
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new'
        }

    @api.onchange('date_to')
    def onchange_date_to(self):
        if self.date_from and self.date_to and self.date_to < self.date_from:
            raise UserError(_('La fecha de finalización debe ser mayor que la fecha de inicio.'))

    @api.onchange('parent_1')
    def onchange_parent_1(self):
        if self.parent_2.code and self.parent_1.code > self.parent_2.code:
            raise UserError(_('La cuenta de incio debe ser menor a la de finalización.'))

    @api.onchange('parent_2')
    def onchange_parent_2(self):
        if self.parent_1.code and self.parent_2.code < self.parent_1.code:
            raise UserError(_('La cuenta de finalización debe ser mayor a la de inicio.'))

    def print_xls_report(self):

        datas = []

        domain =  [('company_id', '=', self.company_id.id)]

        if self.parent_1:
            domain.append(('code', '>=', self.parent_1.code))
        if self.parent_2:
            domain.append(('code', '<=', self.parent_2.code))
        
        account = self.env["account.account"].search(domain)

        if not account:
            raise UserError('No se encontraron registros durante el periodo seleccionado.')
        for acc in account:
            debit_final = 0
            credit_final = 0
            balance_final = 0
            balance_final_total = 0

            debit_initial = 0
            credit_initial = 0
            balance_initial = 0

            account_code = acc.code
            account_name = acc.name
            parent = acc.parent_path            

            child = self.env["account.account"].search([('id','child_of',[acc.id])])

            for chi in child:
                for child_line in chi.move_line_ids:

                    #SI HAY FECHAS
                    if self.date_from:

                        if self.show_initial_balance == True:
                            if child_line.date < self.date_from:
                                debit_initial   += child_line.debit
                                credit_initial  += child_line.credit
                                balance_initial += (child_line.debit - child_line.credit)

                        if child_line.date >= self.date_from and child_line.date <= self.date_to:
                            
                            if self.target_move == 'all':
                                debit_final += child_line.debit
                                credit_final += child_line.credit
                                balance_final = (debit_final - credit_final)

                            if self.target_move == 'posted':
                                if child_line.parent_state == 'posted':
                                    debit_final += child_line.debit
                                    credit_final += child_line.credit
                                    balance_final = (debit_final - credit_final)

                    #SI NO HAY FECHAS
                    elif not self.date_from:
                        if self.target_move == 'posted':
                           if child_line.parent_state == 'posted':
                               debit_final += child_line.debit
                               credit_final += child_line.credit
                               balance_final += (child_line.debit - child_line.credit)

                        if self.target_move == 'all':
                            debit_final += child_line.debit
                            credit_final += child_line.credit
                            balance_final += (child_line.debit - child_line.credit)

            balance_final_total += (balance_initial+balance_final)

            if self.display_account == 'movement':
                if balance_initial !=0 or balance_final != 0:

                    datas.append({
                        'account_code':             account_code,
                        'account_name':             account_name,
                        'debit_final':              debit_final,
                        'credit_final':             credit_final,
                        'balance_final':            balance_final,
                        'balance_final_total':      balance_final_total,
                        'debit_initial' :           debit_initial,
                        'credit_initial' :          credit_initial,
                        'balance_initial' :         balance_initial,
                        'parent' :                  parent,
                        })
            else:
                datas.append({
                    'account_code':             account_code,
                    'account_name':             account_name,
                    'debit_final':              debit_final,
                    'credit_final':             credit_final,
                    'balance_final':            balance_final,
                    'balance_final_total':      balance_final_total,
                    'debit_initial' :           debit_initial,
                    'credit_initial' :          credit_initial,
                    'balance_initial' :         balance_initial,
                    'parent' :                  parent,
                    })

        xls_filename = 'diario_legal.xlsx'
        fp = BytesIO()
        workbook = xlsxwriter.Workbook(fp)

        header_merge_format = workbook.add_format({'bold':True, 'align':'center', 'valign':'vcenter', \
                                            'font_size':10, 'bg_color':'#D3D3D3', 'border':1})

        header_merge_format_titulo = workbook.add_format({'bold':True, 'align':'center', 'valign':'vcenter', \
                                            'font_size':16, 'bg_color':'#D3D3D3', 'border':1})

        header_data_format = workbook.add_format({'align':'center', 'valign':'vcenter', 'font_size':10, 'border':1})
        header_data_format2 = workbook.add_format({'align':'left', 'valign':'vcenter', 'font_size':10, 'border':1})
        header_data_format3 = workbook.add_format({'align':'left', 'valign':'vcenter', 'font_size':10, 'border':1, 'bg_color':'#E9EFB5'})
        concepto_header = workbook.add_format({'bold':True,'align':'center', 'valign':'vcenter', 'font_size':10, 'bg_color':'#E9EFB5', 'border':1})
        currency_format = workbook.add_format({'align':'right', 'valign':'vcenter', 'font_size':10, 'border':1})

        header_data_format_titulo = workbook.add_format({'align':'center', 'valign':'vcenter', \
                                                   'font_size':12, 'border':1})

        currency_format = workbook.add_format({'num_format': '#,##0.00', 'font_size':10, 'border':1})

        fecha = workbook.add_format({'num_format': 'dd/mm/YYYY', 'border':1})

        worksheet = workbook.add_worksheet('Diario Legal Excel')

        worksheet.merge_range(0, 1, 1, 4, self.company_id.name, header_data_format_titulo)
        worksheet.merge_range(0, 6, 0, 7, 'Fecha de Impresión:', header_merge_format)
        worksheet.write_datetime(0,8, fields.Datetime.now(), fecha)

        worksheet.set_column('A:B', 18)
        worksheet.set_column('C:I', 12)

        worksheet.merge_range(4, 2, 5, 5,  '** CONTABILIDAD GENERAL **', header_merge_format)
        
        row = 8

        if self.show_initial_balance:
            worksheet.merge_range(row, 3, row, 4,  "LIBRO MAYOR", header_merge_format)
            row += 1
        else:
            worksheet.merge_range(row, 3, row, 4,  "DIARIO LEGAL", header_merge_format)
            row += 1
        
        if self.date_from:
            worksheet.write(row, 3, "Desde:", header_merge_format)
            worksheet.write(row, 4, self.date_from, fecha)
            row += 1
        if self.date_to:
            worksheet.write(row, 3, "Hasta:", header_merge_format)
            worksheet.write(row, 4, self.date_to, fecha)
            row += 1
        
        if self.target_move:
            worksheet.merge_range(row, 3, row, 4,  "Estado: Todas" if self.target_move == 'all' else "Estado: Publicadas", header_merge_format)
            row += 1
            
        if self.display_account:
            worksheet.merge_range(row, 3, row, 4,  "Mostrar Cuenta: Todas" if self.display_account == 'all' else "Mostrar Cuenta: Con movimientos", header_merge_format)
            row += 1

        row+=2
        col=1
        worksheet.write(row, 0, "Código Cuenta", header_merge_format)#1
        worksheet.write(row, col, "Descripción", header_merge_format)#2
        if self.show_initial_balance:
            col+=1
            worksheet.write(row, col, "Saldo Anterior", header_merge_format)#3
        worksheet.write(row, col+1, "Debe", header_merge_format)#4
        worksheet.write(row, col+2, "Haber", header_merge_format)#5
        if self.show_initial_balance:
            worksheet.write(row, col+3, "Balance", header_merge_format)#6

        Tdebe = 0.0
        Thaber = 0.0
        Tbalance = 0.0
        Tbalance_inicial = 0.0

        for l in datas:
            row += 1
            sub = 0
            col = 1
            myvar2 = l['parent'].split('/')
            if len(myvar2) <= 3:
                sub = 1
            if len(myvar2)==2:
                Tbalance_inicial += l['balance_initial']
                Tdebe += l['debit_final']
                Thaber += l['credit_final']
                Tbalance += l['balance_final_total']
            else:
                sub = 0
            
            if sub==1:
                worksheet.write(row, 0, l['account_code'], header_data_format3)#1 debe ir subrayada
            else:
                worksheet.write(row, 0, l['account_code'], header_data_format2)#1 esta no
            if sub==1:
                worksheet.write(row, 1, l['account_name'], header_data_format3)#2 debe ir subrayada
            else:
                worksheet.write(row, 1, l['account_name'], header_data_format2)#2 esta no
            if self.show_initial_balance:
                col += 1
                if sub==1:
                    worksheet.write(row, col, l['balance_initial'], currency_format)#3 debe ir subrayada
                else:
                    worksheet.write(row, col, l['balance_initial'], currency_format)#3 esta no
            if sub==1:
                worksheet.write(row, col+1, l['debit_final'], currency_format)#4 debe ir subrayada
            else:
                worksheet.write(row, col+1, l['debit_final'], currency_format)#4 esta no
            if sub==1:
                worksheet.write(row, col+2, l['credit_final'], currency_format)#5 debe ir subrayada
            else:
                worksheet.write(row, col+2, l['credit_final'], currency_format)#5 esta no
            if self.show_initial_balance:
                if sub==1:
                    worksheet.write(row, col+3, l['balance_final_total'], currency_format)#6 debe ir subrayada
                else:
                    worksheet.write(row, col+3, l['balance_final_total'], currency_format)#6 esta no

        col = 1
        row += 1
        worksheet.write(row, col, 'Total General', header_data_format)#1
        if self.show_initial_balance:
            col += 1
            worksheet.write(row, col, Tbalance_inicial, currency_format)#2
        worksheet.write(row, col+1, Tdebe, currency_format)#2
        worksheet.write(row, col+2, Thaber, currency_format)#2
        
        if self.show_initial_balance:
            worksheet.write(row, col+3, Tbalance, currency_format)#2

        workbook.close()
        out=base64.encodestring(fp.getvalue())
        
        self.write({
            'states': 'get',
            'data': out,
            'name': xls_filename
        })

        return {
            'name': 'Diario Legal Excel',
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new'
        }