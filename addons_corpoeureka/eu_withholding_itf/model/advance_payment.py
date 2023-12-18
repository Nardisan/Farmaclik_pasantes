# coding: utf-8
#eliomeza1@gmail.com
###########################################################################

from odoo import fields, models, api,_
from odoo.exceptions import UserError

class AdvancePaymentInnerit(models.Model):
    _inherit = 'account.advanced.payment'

    move_itf_id = fields.Many2one('account.move', 'Asiento contable IGTF')
    move_itf_id_lines = fields.One2many('account.move.line',related='move_itf_id.line_ids',string='Apuntes contable IGTF')

    def action_register_advance(self):
        """Genera la retencion del 2% después que realiza el pago em el anticipo"""
        res = super(AdvancePaymentInnerit, self).action_register_advance()
        for pago in self:
            idem = pago.check_partner()
            itf_bool = pago._get_company_itf()
            #raise UserError(('idem %s, itf_bool %s, pago.es_proveedor %s, pago.bank_account_id.apply_igft %s, pago.state %s, pago.bank_account_id.tipo_bank %s')%(idem,itf_bool,pago.es_proveedor,pago.bank_account_id.apply_igft,pago.state,pago.bank_account_id.tipo_bank))
            if idem and itf_bool and pago.es_proveedor and pago.bank_account_id.apply_igft and not pago.move_itf_id and (pago.bank_account_id.tipo_bank == "na" or pago.bank_account_id.tipo_bank == False):
                pago.register_account_move_payment_advance()  
        #res = super(AdvancePaymentInnerit, self).action_register_advance()
        return res

    def register_account_move_payment_advance(self):
            lines_vals_list_2 = []
            vals = {
                #'name': name_line,
                'date': self.date_advance,
                'journal_id': self.bank_account_id.id,
                'line_ids': False,
                'state': 'draft',
                'move_type': 'entry',
            }
            move_obj = self.env['account.move'].sudo()
            move_id = move_obj.create(vals)
            
            porcentage_itf= self._get_company().wh_porcentage
            #calculo del 2% del pago

            #amount_itf = self.compute_itf()
            if self.currency_id.id == self.env.company.currency_id.id:
                currency = False
                amount_currency = round(float(self.amount_advance) * float((porcentage_itf / 100.00)), 2)
                amount_itf = round(float(self.amount_advance) * float((porcentage_itf / 100.00)), 2)
            else:
                currency = self.currency_id.id
                amount_currency = round(float(self.amount_advance) * float((porcentage_itf / 100.00)), 2)
                if self.manual_currency_exchange_rate > 0:
                    amount_itf = round(float(self.amount_advance*self.manual_currency_exchange_rate) * float((porcentage_itf / 100.00)), 2)
                else:
                    raise UserError(_('Por favor Registrar la tasa para poder hacer la respectiva conversion y poder continuar'))
            lines_vals_list_2.append({
                'account_id': self.bank_account_id.payment_debit_account_id.id,#V14
                'company_id': self._get_company().id,
                'currency_id': currency,
                'date_maturity': False,
                'ref': "Comisión del %s %% del pago %s por IGTF" % (porcentage_itf,self.name),
                'date': self.date_advance,
                'partner_id': self.partner_id.id,
                'move_id': move_id.id,
                'name': "Comisión del %s %% del pago %s por IGTF" % (porcentage_itf, self.name),
                'journal_id': self.bank_account_id.id,
                'credit': float(amount_itf),
                'debit': 0.0,
                'amount_currency': -amount_currency,
            })
            lines_vals_list_2.append({
                'account_id': self._get_company().account_wh_itf_id.id,#V14
                'company_id': self._get_company().id,
                'currency_id': currency,
                'date_maturity': False,
                'ref': "Comisión del %s %% del pago %s por IGTF" % (porcentage_itf,self.name),
                'date': self.date_advance,
                'partner_id': self.partner_id.id,
                'move_id': move_id.id,
                'name': "Comisión del %s %% del pago %s por IGTF" % (porcentage_itf, self.name),
                'journal_id': self.bank_account_id.id,
                'credit': 0.0,
                'debit': float(amount_itf),
                'amount_currency': amount_currency,
            })
            move_line_obj = self.env['account.move.line'].sudo()
            move_line_id1 = move_line_obj.create(lines_vals_list_2)
            
            if move_line_id1:
                #res = {'move_itf_id': move_id.id}
                self.move_itf_id = move_id.id
                #move_id.name = name_line
                move_id.action_post()

    @api.model
    def _get_company(self):
        '''Método que busca el id de la compañia'''
        company_id = self.env['res.users'].browse(self.env.uid).company_id
        return company_id

    def _get_company_itf(self):
        '''Método que retorna verdadero si la compañia debe retener el impuesto ITF'''
        company_id = self._get_company()
        if company_id.calculate_wh_itf:
            return True
        return False


    

    @api.model
    def check_partner(self):
        '''metodo que chequea el rif de la empresa y la compañia si son diferentes
        retorna True y si son iguales retorna False'''
        idem = False
        company_id = self._get_company()
        for pago in self:
            if (pago.partner_id.rif != company_id.partner_id.rif) and pago.partner_id.company_type == 'company' :
                idem = True
                return idem
            elif (pago.partner_id.rif != company_id.partner_id.rif) and pago.partner_id.company_type == 'person':
                idem = True
                return idem
        return idem

    def action_cancel(self):
        """Cancela el movimiento contable si se cancela el pago de las facturas"""
        res = super(AdvancePaymentInnerit, self).action_cancel()
        date = fields.Datetime.now()
        for pago in self:
            if pago.state == 'cancel':
                for move in pago.move_itf_id:
                    move_reverse = move._reverse_moves([{'date': date, 'ref': _('Reversal of %s') % move.name}],
                                   cancel=True)
                    if len(move_reverse) == 0:
                        raise UserError(_('No se reversaron los asientos asociados'))
        return res



class AccountMoveInnerit(models.Model):
    _inherit = 'account.move'


    def assert_balanced(self):
        if not self.ids:
            return True
        mlo = self.env['account.move.line'].search([('move_id', '=',self.ids[0])])
        if not mlo.reconcile:
            super(AccountMoveInnerit, self).assert_balanced(fields)
        return True