# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"
    
    os_currency_rate = fields.Float(string='Tipo de Cambio', default=1 ,digits=(12, 2))
    
    def _check_balanced(self):
        ''' Assert the move is fully balanced debit = credit.
        An error is raised if it's not the case.
        '''
        moves = self.filtered(lambda move: move.line_ids)
        if not moves:
            return
        debit = 0 
        credit = 0 
        for line in moves.line_ids:
            debit  = debit  + round(line.debit,moves[0].company_currency_id.decimal_places)  
            credit = credit + round(line.credit,moves[0].company_currency_id.decimal_places)

        self.env['account.move.line'].flush(self.env['account.move.line']._fields)
        self.env['account.move'].flush(['journal_id'])
        self._cr.execute('''
            SELECT line.move_id, ROUND(SUM(line.debit - line.credit), currency.decimal_places)
            FROM account_move_line line
            JOIN account_move move ON move.id = line.move_id
            JOIN account_journal journal ON journal.id = move.journal_id
            JOIN res_company company ON company.id = journal.company_id
            JOIN res_currency currency ON currency.id = company.currency_id
            WHERE line.move_id IN %s
            GROUP BY line.move_id, currency.decimal_places
            HAVING ROUND(SUM(line.debit - line.credit), currency.decimal_places) != 0.0;
        ''', [tuple(self.ids)])

        query_res = self._cr.fetchall()
        sums = 0 
        if query_res:
            sums = query_res[0][1]

        diff = self.env['account.move.line']
        if int(sums) > 1:
            return super(AccountMove, self)._check_balanced()
        
        if sums != 0:
            if debit > credit:
                diff = self.env['account.move.line'].search([('move_id','=',self.id), ('credit','>','0')],limit=1)
                amount = round(diff.credit,moves[0].company_currency_id.decimal_places) + sums
                sql = "UPDATE account_move_line SET credit = " + str(amount ) + " WHERE id = " + str(diff.id)
                self._cr.execute(sql)

            else :
                diff = self.env['account.move.line'].search([('move_id','=',self.id), ('debit','>','0')],limit=1)
                amount = round(diff.debit,moves[0].company_currency_id.decimal_places) + sums
                sql = "UPDATE account_move_line SET debit = " + str(amount ) + " WHERE id = " + str(diff.id)
                self._cr.execute(sql)
        return super(AccountMove, self)._check_balanced()
        
    def set_os_currency_rate(self):
        if self.invoice_date: 
            rate = self.env['res.currency.rate'].search([('currency_id', '=', self.currency_id.id),('name','=',self.invoice_date)], limit=1).sorted(lambda x: x.name)

            if self.currency_id.id != self.company_currency_id.id:
                #if rate:
                pass
                #else :
                #    raise UserError(_("No existe tasa de cambio para  " + str(self.invoice_date) + " registre el la siguiente ruta Contabilidad/Configuracion/Contabilidad/Monedas" ))

            if rate :
                exchange_rate =  1 / rate.rate
                self.os_currency_rate = exchange_rate
    
    @api.constrains('invoice_date','currency_id')
    def _check_os_currency_rate(self):
        self.set_os_currency_rate()
    
    @api.onchange('invoice_date','currency_id')
    def _onchange_os_currency_rate(self):
        self.set_os_currency_rate()