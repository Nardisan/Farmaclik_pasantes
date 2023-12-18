# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError

class AccountPaymentMotivo(models.Model):
    _name = 'account.payment.motivo'
    _description = 'Motivo de Pagos'
    _order = 'id desc'

    name = fields.Char(
        string='Nombre',
        index=True,
    )   
class AccountPayments(models.Model):
    _inherit = 'account.payment'

    payment_two = fields.Boolean(string="Pago asociado a la farmacia interna")
    payment_reg = fields.Date(string='Fecha de Registro',readonly=True, states={'draft': [('readonly', False)]}, track_visibility='always',default=fields.Date.context_today)
    payment_date_collection = fields.Date(default=fields.Date.context_today, required=True, readonly=True, states={'draft': [('readonly', False)]}, copy=False, tracking=True, track_visibility='onchange' )
    gestores = fields.Many2one('res.partner',string="Gestor / Tercero", track_visibility='always',)
    motivo = fields.Many2one('account.payment.motivo', track_visibility='always', string="Motivo de la Transferencia")

    @api.model
    def default_get(self, fields):
        result = super(AccountPayments, self).default_get(fields)
        active_ids = self._context.get('active_ids') or self._context.get('active_id')
        active_model = self._context.get('active_model')
        # Check for selected invoices ids
        if not active_ids or active_model != 'account.move':
            return result
        else:
            move_id = self.env['account.move'].browse(self._context.get('active_ids')).filtered(lambda move: move.is_invoice(include_receipts=True))
            for move in move_id:
                result.update({
                    'date':move.invoice_date,
                    })
            return result

    def _get_invoice_payment_amount(self, inv):
        """
        Computes the amount covered by the current payment in the given invoice.
        :param inv: an invoice object
        :returns: the amount covered by the payment in the invoice
        """
        self.ensure_one()
        return sum([
            data['amount']
            for data in inv._get_reconciled_info_JSON_values()
            if data['account_payment_id'] == self.id
        ])
    
    def create_payment_two(self,journal_id,account, pay,payment_t,partner_t,company_id):
        if journal_id:
            vals={
                'name':'/',
                'payment_type':payment_t,
                'partner_type':partner_t,
                'partner_id':self.env.company.partner_id.id,
                'destination_account_id':account.id,
                'journal_id': journal_id.id,
                'is_internal_transfer':False,
                'company_id':company_id.id,
                'manual_currency_exchange_rate':pay.manual_currency_exchange_rate,
                'currency_id':pay.currency_id.id,
                'payment_reg':pay.payment_reg,
                'payment_date_collection':pay.payment_date_collection,
                'date':pay.date ,
                'partner_bank_id': journal_id.bank_account_id.id if pay.currency_id.name != 'USD' else False, 
                'amount':abs(pay.amount),
                'amount_ref':abs(pay.amount_ref),
                'ref':pay.ref,
                'payment_two': True,
                }
            payment_two = self.env['account.payment'].sudo().create(vals)
            payment_two.payment_type = payment_t
            payment_two.partner_type = partner_t
            payment_two.action_post()
            # print(payment_two)

    @api.model_create_multi
    def create(self, vals_list):

        payments = super(AccountPayments, self).create(vals_list)

        if payments.payment_type == 'outbound' and payments.partner_type == 'supplier':
        
                company = self.env['res.company'].search([('partner_id','=',payments.partner_id.id)],limit=1)
                
                if payments.journal_id.code != 'INTER':

                    if len(company) > 0:

                        if payments.env.company != company:

                            account_dest = self.env['account.account'].sudo().search([('code','=','01.1.2.2'),('company_id','=',company.id)],limit=1)

                            domain = [('default_account_id.code','=','01.1.1.2.009'),('company_id','=',company.id)] if payments.currency_id.name != 'USD' else [('default_account_id.code','=','01.1.1.1.003'),('company_id','=',company.id)]
                            journal = self.env['account.journal'].sudo().search(domain,limit=1) 

                            self.create_payment_two(journal,account_dest,payments,'inbound','customer',company)


        if payments.journal_id.code == 'INTER' and not payments.payment_two:
            
            company = self.env['res.company'].search([('partner_id','=',payments.partner_id.id)],limit=1)

            if len(company) > 0:
                values = [('code','=','01.1.2.2.001 '),('company_id','=',company.id)] if payments.payment_type == 'supplier' else [('code','=','02.1.2.1.001'),('company_id','=',company.id)]
                account_dest = self.env['account.account'].sudo().search(values,limit=1)

                domain = [('default_account_id.code','=','01.1.2.2.005'),('company_id','=',company.id),('code','=','INTER')] 
                journal = self.env['account.journal'].sudo().search(domain,limit=1) 

                pay_t ='inbound' if payments.payment_type == 'outbound' else 'outbound'
                part_t ='customer' if payments.partner_type == 'supplier' else 'supplier'

                self.create_payment_two(journal,account_dest,payments,pay_t,part_t, company)

        return payments


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

   
    payment_reg = fields.Date(string='Fecha de Registro',readonly=False,default=fields.Date.context_today)
    payment_date_collection = fields.Date(default=fields.Date.context_today, required=True,  track_visibility='onchange' )
    gestores = fields.Many2one('res.partner',string="Gestor / Tercero", track_visibility='always',)
    motivo = fields.Many2one('account.payment.motivo', track_visibility='always', string="Motivo de la Transferencia")

    def _create_payment_vals_from_wizard(self):
        result = super(AccountPaymentRegister, self)._create_payment_vals_from_wizard()
        result.update({
            'payment_reg': self.payment_reg,
            'payment_date_collection': self.payment_date_collection,
            'gestores': self.gestores,
            'motivo': self.motivo,
        })
        return result