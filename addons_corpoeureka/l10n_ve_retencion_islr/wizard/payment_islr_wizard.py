# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class AccountConfirmedIslr(models.TransientModel):
    _name = "account.confirmed.islr"
    _description = "Payment ISLR report"
    
    def _default_withholding(self):
        withholding=self.env['account.wh.islr'].search([('id','in',self.env.context.get('active_ids', [])),('state','=','draft')])
        return list(map(lambda x: x.id, withholding))
    
    withholding_ids = fields.Many2many("account.wh.islr", string='Withholding', default=_default_withholding, readonly=False, copy=False, required=True)

                
    def confirm_withholding(self):
        for wh in self.withholding_ids:
            wh.action_confirm()
        return True
        
class AccountWithholdIslr(models.TransientModel):
    _name = "account.withhold.islr"
    _description = "Withhold ISLR report"

    def _default_withholding(self):
        withholding=self.env['account.wh.islr'].search([('id','in',self.env.context.get('active_ids', [])),('state','=','confirmed')])
        return list(map(lambda x: x.id, withholding))

    withholding_ids = fields.Many2many("account.wh.islr", string='Withholding', default=_default_withholding, readonly=False, copy=False, required=True)

    def withhold_withholding(self):
        for wh in self.withholding_ids:
            wh.action_withold()
        return True

        
class AccountdeclarateIslr(models.TransientModel):
    _name = "account.declarate.islr"
    _description = "Declarate ISLR report"
    
    def _default_withholding(self):
        withholding=self.env['account.wh.islr'].search([('id','in',self.env.context.get('active_ids', [])),('state','in',('confirmed','cancel'))])
        return list(map(lambda x: x.id, withholding))
        
    #def selection_period(self):
    #    fecha   = fields.Date.context_today(self)
    #    anio    = fecha.year
    #    mes     = fecha.month
    #    mes1     = fecha.month
    #    mes2     = fecha.month
    #    if len(str(mes)) == 1:
    #        mes1 = '0' + str(mes)
    #    period1 = str(anio) + str(mes1)
    #    if mes == 1:
    #        mes2 = 12
    #        anio = anio - 1
    #    else:
    #        mes2 = mes - 1
    #    if len(str(mes2)) == 1:
    #        mes2 = '0' + str(mes2)
    #    period2 = str(anio) + str(mes2)
    #    return [(period1, period1), (period2, period2)]
    
    def selection_period(self):
        fecha   = fields.Date.context_today(self)
        anio    = fecha.year
        mes     = fecha.month
        mes1     = fecha.month
        mes2     = fecha.month
        mes3     = fecha.month
        mes4     = fecha.month
        if len(str(mes)) == 1:
            mes1 = '0' + str(mes)
        period1 = str(anio) + str(mes1)
        if mes == 1:
            mes2 = 12
            mes3 = 11
            mes4 = 10
            anio = anio - 1
            if len(str(mes2)) == 1:
                mes2 = '0' + str(mes2)
            period2 = str(anio) + str(mes2)
            if len(str(mes3)) == 1:
                mes3 = '0' + str(mes3)
            period3 = str(anio) + str(mes3)
            if len(str(mes4)) == 1:
                mes4 = '0' + str(mes4)
            period4 = str(anio) + str(mes4)
        elif mes == 2:
            mes2 = mes - 1
            if len(str(mes2)) == 1:
                mes2 = '0' + str(mes2)
            period2 = str(anio) + str(mes2)
            anio = anio - 1
            mes3 = 12
            mes4 = 11            
            if len(str(mes3)) == 1:
                mes3 = '0' + str(mes3)
            period3 = str(anio) + str(mes3)
            if len(str(mes4)) == 1:
                mes4 = '0' + str(mes4)
            period4 = str(anio) + str(mes4)
        elif mes == 3 :
            mes2 = mes - 1
            mes3 = mes - 2
            if len(str(mes2)) == 1:
                mes2 = '0' + str(mes2)
            period2 = str(anio) + str(mes2)
            if len(str(mes3)) == 1:
                mes3 = '0' + str(mes3)
            period3 = str(anio) + str(mes3)
            anio = anio - 1
            mes4 == 12
            if len(str(mes4)) == 1:
                mes4 = '0' + str(mes4)
            period4 = str(anio) + str(mes4)            
        else:
            mes2 = mes - 1
            mes3 = mes - 2
            mes4 = mes - 3
            if len(str(mes2)) == 1:
                mes2 = '0' + str(mes2)
            period2 = str(anio) + str(mes2)
            if len(str(mes3)) == 1:
                mes3 = '0' + str(mes3)
            period3 = str(anio) + str(mes3)
            if len(str(mes4)) == 1:
                mes4 = '0' + str(mes4)
            period4 = str(anio) + str(mes4)
        return [(period1, period1), (period2, period2), (period3, period3), (period4, period4)]
    withholding_ids = fields.Many2many("account.wh.islr", string='Withholding', default=_default_withholding, readonly=False, copy=False, required=True)
    period = fields.Selection(selection_period, string='Period', readonly=False, required=True, help="")
    state = fields.Selection([('draft', 'Draft'), ('declared', 'Declared')], 
                             default='draft')         
    def print_report_islr_xml(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/printReportIslrMassive/%s' % self.id,
            'target': 'self',
            'res_id': self.id,
                }
                
    def print_declare_report_islr_xml(self):
        this = self[0]
        this.write({'state': 'declared'})
        company_id = self.env.user.company_id
        withholding=self.env['account.wh.islr']
        for wh in  self:
            wh.withholding_ids.action_declaration({},True)
        arbol=withholding.generate_file_xml(self.withholding_ids,self.period)
        file_xml_id=withholding.create_attachment(arbol,company_id)
        declaration = {
            'file_xml_id': [[6, False, [file_xml_id.id]]],
            'period': self.period,
        }
        declaration_obj = self.env['account.wh.islr.declaration'].sudo().create(declaration)
        self.withholding_ids.write({'declaration_id':declaration_obj.id,'period':self.period })
        return {
            'type': 'ir.actions.act_url',
            'url': '/printReportIslrMassive/%s' % self.id,
            'target': 'new',
            'res_id': self.id,
                }

class AccountPrintPdfIslr(models.TransientModel):
    _name = "account.print.pdf.wislr"
    _description = "Print Pdf Islr"
    
    def _default_withholding(self):
        return self.env.context.get('active_ids', [])
    
    withholding_ids = fields.Many2many("account.wh.islr", string='Withholding', default=_default_withholding, readonly=False, copy=False, required=True)

    @api.model
    def print_reports_islr_pdf(self):
        return self.withholding_ids.print_report_islr_pdf()
        

class AccountPayIslr(models.Model):
    _name = "account.pays.islr"
    _order = 'payment_date desc, id desc'
    _description = "Pay Islr"
    
    def _default_withholding(self):
        withholding=self.env['account.wh.islr'].search([('id','in',self.env.context.get('active_ids', [])),('state','=','declared')])
        return list(map(lambda x: x.id, withholding))
        
    name = fields.Char(readonly=True, copy=False, default="payment of the withheld ISLR")
    account_id = fields.Many2one('account.account',  string='Account', required=True ,help="")
    withholding_ids = fields.Many2many("account.wh.islr", string='Withholding', default=_default_withholding, readonly=True, copy=False, required=True)
    move_id = fields.Many2one('account.move', 'Accounting Entry', readonly=True, copy=False, help="",store=True)
    amount = fields.Monetary(string='Payment Amount', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)
    payment_date = fields.Date(string='Payment Date', default=fields.Date.context_today, required=True, copy=False)
    communication = fields.Char(string='Memo')
    journal_id = fields.Many2one('account.journal', string='Payment Journal', required=True, domain=[('type', 'in', ('bank', 'cash'))])
    company_id = fields.Many2one('res.company', related='journal_id.company_id', string='Company', readonly=True)

    @api.model
    def default_get(self, fields):
        rec = super(AccountPayIslr, self).default_get(fields)
        context = dict(self._context or {})
        active_ids = context.get('active_ids')
        total_amount=0
        list_account=[]
        if active_ids:
            withholding=self.env['account.wh.islr'].search([('id','in',active_ids),('state','=','declared')])
            for wh in withholding:
                if not wh.account_id.id in list_account:
                    list_account.append(wh.account_id.id)
                for whl in wh.withholding_line:
                    if whl.state == 'declared':
                        total_amount+=whl.ret_amount
            if len(list_account)>1:
                raise UserError(_("Only withholdings assigned to the same account can be paid together.."))
            if withholding:
                rec.update({
                    'amount': abs(total_amount),
                    'account_id': withholding[0].account_id.id,
                })
        return rec
    
    def pay_islr_withholding(self):
        line_ids = []
        credit_account_id = False
        debit_account_id = False
        payment_dict = {}
        self.name=self.env['ir.sequence'].next_by_code('account.payment.islr.in_invoice')
        for pay in self:
            tasa = sum(pay.withholding_ids.mapped('withholding_line').mapped('invoice_id').mapped('manual_currency_exchange_rate')) / len(pay.withholding_ids)
            payment_dict = {
                'payment_type':'outbound',
                'partner_type':'supplier',
                #'destination_account_id':credit_account_id,
                'amount':0,
                'payment_reg':pay.payment_date,
                'journal_id':pay.journal_id.id,
                'ref':'Pago del ISLR Retenido',
                'active_manual_currency_rate':True,
                'manual_currency_exchange_rate': tasa,
            }
            #raise UserError(sum(pay.withholding_ids.mapped('withholding_line').mapped('invoice_id').mapped('manual_currency_exchange_rate')) / len(pay.withholding_ids))
            payment = self.env['account.payment'].create(payment_dict)

            move_dict = {
                    'ref': pay.name,
                    'narration': pay.name,
                    'journal_id': pay.journal_id.id,
                    'date': pay.payment_date,
                    'pay_withholding_id': pay.id,
                    'move_type':'entry',
                    'payment_id':payment.id,
                    'currency_id': self.env.company.currency_id.parent_id.id,
                    'active_manual_currency_rate':True,
                    'manual_currency_exchange_rate': tasa,
                }
            amount_currency = pay.amount * tasa
            if pay.withholding_ids[0].move_type == 'in_invoice' or pay.withholding_ids[0].move_type == 'entry':
                 debit_account_id = pay.account_id.id
                 credit_account_id = pay.journal_id.payment_credit_account_id.id
            if credit_account_id:
                credit_line = (0, 0, {
                    'name': 'Pago del ISLR retenido',
                    'currency_id': self.env.company.currency_id.parent_id.id,
                    'account_id': credit_account_id,
                    'journal_id': pay.journal_id.id,
                    'date': pay.payment_date,
                    'debit': False,
                    'credit': pay.amount,
                    'payment_id':payment.id,
                    'amount_currency':-amount_currency,
                })
                line_ids.append(credit_line)
            if debit_account_id:
                debit_line = (0, 0, {
                    'name': 'Pago del ISLR retenido',
                    'currency_id': self.env.company.currency_id.parent_id.id,
                    'account_id': debit_account_id,
                    'journal_id': pay.journal_id.id,
                    'date': pay.payment_date,
                    'debit': pay.amount,
                    'credit': False,
                    'payment_id':payment.id,
                    'amount_currency':amount_currency,
                })
                line_ids.append(debit_line)
            move_dict['line_ids'] = line_ids
            move = self.env['account.move'].create(move_dict)
            move.post()
            self.move_id=move.id
            payment.write({'islr_entry':move.id})
            #move = payment.move_id.id
            list_line=[]
            for wh in pay.withholding_ids:
                for whl in wh.withholding_line:
                    if whl.state not in ['annulled','cancel']:
                        list_line.append(whl.id)
            pay.withholding_ids.write({'state':'done','move_paid_id':move,'payment_id':payment.id})
            self.env['account.wh.islr.line'].search([('id','in',list_line)]).write({'state':'done'})
        return True