# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class AccountConfirmedIva(models.TransientModel):
    _name = "account.wh.iva.confirmed"
    _description = "Confirmed IVA Withholding"
    
    def _default_withholding_iva(self):
        wh_iva = self.env['account.wh.iva'].search([('id','in',self.env.context.get('active_ids', [])),('state','=','draft')])
        return list(map(lambda x: x.id, wh_iva))
    
    wh_ids = fields.Many2many("account.wh.iva", string='Withholding IVA', default=_default_withholding_iva, readonly=False, copy=False, required=True)

    def action_confirm(self):
        for wh in self.wh_ids:
            wh.action_confirm()
        return True


class AccountWithholdIva(models.TransientModel):
    _name = "account.wh.iva.withold"
    _description = "Withhold IVA report"

    def _default_withholding(self):
        wh_iva = self.env['account.wh.iva'].search([('id','in',self.env.context.get('active_ids', [])),('state','=','confirmed')])
        return list(map(lambda x: x.id, wh_iva))

    wh_ids = fields.Many2many("account.wh.iva", string='Withholding', default=_default_withholding, readonly=False, copy=False, required=True)

    def withhold_withholding(self):
        for wh in self.wh_ids:
            wh.action_withhold()
        return True

        
class AccountDeclaredIva(models.TransientModel):
    _name = "account.wh.iva.declared"
    _description = "Declared IVA Withholding"
    
    def _default_withholding_iva(self):
        wh_iva = self.env['account.wh.iva'].search([('id','in',self.env.context.get('active_ids', [])),('state','=','confirmed')])
        return list(map(lambda x: x.id, wh_iva))
        
    def selection_period(self):
        fecha=fields.Date.context_today(self)
        anio=fecha.year
        mes=fecha.month
        mes1=fecha.month
        mes2=fecha.month
        if len(str(mes))==1:
            mes1='0'+str(mes)
        period1=str(anio)+str(mes1)
        if mes==1:
            mes2=12
            anio=anio-1
        else:
            mes2=mes-1
        if len(str(mes2))==1:
            mes2='0'+str(mes2)
        period2=str(anio)+str(mes2)
        return [(period1,period1),(period2,period2)]
    
    wh_ids = fields.Many2many("account.wh.iva", string='Withholding IVA', default=_default_withholding_iva, readonly=False, copy=False, required=True,store=True)
    period = fields.Selection(selection_period, string='Period', readonly=False, required=True, help="")
    state = fields.Selection([('draft', 'Draft'), ('declared', 'Declared')], 
                             default='draft')
             
    def print_report_iva_txt(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/IvaTXTreports/%s' % self.id,
            'target': 'new',
            'res_id': self.id,
                }

    def to_declare_report_iva_txt(self):
        this = self[0]
        this.write({'state': 'declared'})
        return {
            'type': 'ir.actions.act_url',
            'url': '/reportTxtDeclarate/%s' % self.id,
            'target': 'new',
            'res_id': self.id,
                }
                

class AccountWhIvaPay(models.Model):
    _name = "account.wh.iva.pay"
    _order = 'payment_date desc, id desc'
    _description = "Pay IVA"
    
    def _default_withholding(self):
        wh_id = self.env['account.wh.iva'].search([('id','in',self.env.context.get('active_ids', [])),('state','=','declared')])
        return list(map(lambda x: x.id, wh_id))
    
    name = fields.Char(readonly=True, copy=False, default="payment of the withheld IVA")
    account_id = fields.Many2one('account.account',  string='Account', required=True ,help="")
    wh_ids = fields.Many2many("account.wh.iva", string='Withholding', default=_default_withholding, domain=[('state', '=', 'declared')], readonly=True, copy=False, required=True)
    move_id = fields.Many2one('account.move', 'Accounting Entry', readonly=True, copy=False, help="",)
    amount = fields.Monetary(string='Payment Amount', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)
    payment_date = fields.Date(string='Payment Date', default=fields.Date.context_today, required=True, copy=False)
    communication = fields.Char(string='Memo')
    journal_id = fields.Many2one('account.journal', string='Payment Journal', required=True, domain=[('type', 'in', ('bank', 'cash'))])
    company_id = fields.Many2one('res.company', related='journal_id.company_id', string='Company', readonly=True)

    @api.model
    def default_get(self, fields):
        rec = super(AccountWhIvaPay, self).default_get(fields)
        context = dict(self._context or {})
        active_ids = context.get('active_ids')
        total_amount=0
        list_account=[]
        if active_ids:
            wh_iva = self.env['account.wh.iva'].search([('id','in',active_ids)])
            for wh in wh_iva:
                if not wh.account_id.id in list_account:
                    list_account.append(wh.account_id.id)
                for whl in wh.wh_lines:
                    if whl.state == 'declared':
                        total_amount += whl.ret_amount
            if len(list_account)>1:
                raise UserError(_("Only withholdings assigned to the same account can be paid together.."))
            rec.update({
                'amount': abs(total_amount),
                'account_id': wh_iva[0].account_id.id,
            })
        return rec

    # def pay_iva_withhold(self):
    #     line_ids = []
    #     self.name=self.env['ir.sequence'].next_by_code('account.payment.iva.in_invoice')
    #     for pay in self:
    #         move_dict = {
    #                 'ref': pay.name,
    #                 'narration': pay.name,
    #                 'journal_id': pay.journal_id.id,
    #                 'date': pay.payment_date,
    #             }
    #         if pay.wh_ids[0].move_type == 'in_invoice':
    #             debit_account_id = pay.account_id.id
    #             credit_account_id = pay.journal_id.payment_debit_account_id.id
    #         if credit_account_id:
    #             credit_line = (0, 0, {
    #                 'name': 'Pago del IVA retenido',
    #                 'account_id': credit_account_id,
    #                 'journal_id': pay.journal_id.id,
    #                 'date': pay.payment_date,
    #                 'debit': False,
    #                 'credit': pay.amount,
    #             })
    #             line_ids.append(credit_line)
    #         if debit_account_id:
    #             debit_line = (0, 0, {
    #                 'name': 'Pago del IVA retenido',
    #                 'account_id': debit_account_id,
    #                 'journal_id': pay.journal_id.id,
    #                 'date': pay.payment_date,
    #                 'debit': pay.amount,
    #                 'credit': False,
    #             })
    #             line_ids.append(debit_line)
    #         move_dict['line_ids'] = line_ids
    #         move = self.env['account.move'].create(move_dict)
    #         move.post()
    #         self.move_id = move.id
    #         list_line=[]
    #         for wh in pay.wh_ids:
    #             for whl in wh.wh_lines: 
    #                 if whl.state != 'annulled':
    #                     list_line.append(whl.id)
    #         pay.wh_ids.write({'state':'done','move_paid_id':move.id})
    #         self.env['account.wh.iva.line'].search([('id','in',list_line)]).write({'state':'done'})
    #     return True
        
        

    def pay_iva_withhold(self):
        line_ids = []
        credit_account_id = False
        debit_account_id = False
        payment_dict = {}
        self.name=self.env['ir.sequence'].next_by_code('account.payment.iva.in_invoice')
        for pay in self:
            payment_dict = {
                'payment_type':'outbound',
                'partner_type':'supplier',
                #'destination_account_id':credit_account_id,
                'amount':0,
                'payment_reg':pay.payment_date,
                'journal_id':pay.journal_id.id,
                'ref':'Pago del IVA Retenido',
                'active_manual_currency_rate':True,
                'manual_currency_exchange_rate': sum(pay.wh_ids.mapped('manual_currency_exchange_rate')) / len(pay.wh_ids),
            }
            payment = self.env['account.payment'].create(payment_dict)
            move_dict = {
                    'ref': pay.name,
                    'narration': pay.name,
                    'journal_id': pay.journal_id.id,
                    'date': pay.payment_date,
                    'pay_withholding_id_iva': pay.id,
                    'move_type':'entry',
                    'payment_id':payment.id,
                    'active_manual_currency_rate':True,
                    'manual_currency_exchange_rate': sum(pay.wh_ids.mapped('manual_currency_exchange_rate')) / len(pay.wh_ids),
                }
            if pay.wh_ids[0].move_type == 'in_invoice' or pay.wh_ids[0].move_type == 'entry':
                 debit_account_id = pay.account_id.id
                 credit_account_id = pay.journal_id.payment_credit_account_id.id
            if credit_account_id:
                credit_line = (0, 0, {
                    'name': 'Pago del IVA retenido',
                    'account_id': credit_account_id,
                    'journal_id': pay.journal_id.id,
                    'date': pay.payment_date,
                    'debit': False,
                    'credit': pay.amount,
                    'payment_id':payment.id,
                })
                line_ids.append(credit_line)
            if debit_account_id:
                debit_line = (0, 0, {
                    'name': 'Pago del IVA retenido',
                    'account_id': debit_account_id,
                    'journal_id': pay.journal_id.id,
                    'date': pay.payment_date,
                    'debit': pay.amount,
                    'credit': False,
                    'payment_id':payment.id,
                })
                line_ids.append(debit_line)
            move_dict['line_ids'] = line_ids
            move = self.env['account.move'].create(move_dict)
            move.post()
            self.move_id=move.id
            payment.write({'iva_entry':move.id})
            #move = payment.move_id.id
            list_line=[]
            for wh in pay.wh_ids:
                for whl in wh.wh_lines: 
                    if whl.state != 'annulled':
                        list_line.append(whl.id)
            pay.wh_ids.write({'state':'done','move_paid_id':move.id,'payment_id':payment.id})
            self.env['account.wh.iva.line'].search([('id','in',list_line)]).write({'state':'done'})
        return True