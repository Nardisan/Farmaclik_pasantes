# coding: utf-8
#eliomeza1@gmail.com
###########################################################################

from odoo import fields, models, api,_
from odoo.exceptions import UserError

        
class AccountPaymentInnerit(models.Model):
    # _name = 'account.payment'
    _inherit = 'account.payment'

    move_itf_id = fields.Many2one('account.move', 'Asiento contable IGTF')



    def action_post(self):
        """Genera la retencion del 2% después que realiza el pago"""

        res = super(AccountPaymentInnerit, self).action_post()
        for pago in self:
            idem = pago.check_partner()
            itf_bool = pago._get_company_itf()
            type_bool = pago.check_payment_type()
            #raise UserError(('Puede ser que aquí no %s %s %s')%(idem,itf_bool,type_bool))
            if idem and itf_bool and type_bool and pago.journal_id.apply_igft and (pago.journal_id.tipo_bank == "na" or pago.journal_id.tipo_bank == False):
                #raise UserError(_('Puede ser que aquí'))
                pago.register_account_move_payment()
                #raise UserError(('idem %s, itf_bool %s, type_bool %s')%(idem,itf_bool,type_bool))
        return res


    def register_account_move_payment(self):
        '''Este método realiza el asiento contable de la comisión según el porcentaje que indica la compañia'''
        #raise UserError(('idem %s, itf_bool %s, type_bool %s')%(idem,itf_bool,type_bool))
        #raise UserError(_('Hola'))
        #name = self.get_name_igtf()
        #self.env['ir.sequence'].with_context(ir_sequence_date=self.date_advance).next_by_code(sequence_code)
        lines_vals_list_2 = []
        #name_line = self.get_name_igtf()
        vals = {
            #'name': name_line,
            'date': self.date,
            'journal_id': self.journal_id.id,
            'line_ids': False,
            'state': 'draft',
            'move_type': 'entry',
            'manual_currency_exchange_rate':self.manual_currency_exchange_rate,
            'apply_manual_currency_exchange':True,
        }
        move_obj = self.env['account.move'].sudo()
        move_id = move_obj.create(vals)

        porcentage_itf= self._get_company().wh_porcentage
        #calculo del 2% del pago

        #amount_itf = self.compute_itf()
        if self.currency_id.id == self.env.company.currency_id.id:
            currency = False
            amount_currency = round(float(self.amount) * float((porcentage_itf / 100.00)), 2)
            amount_itf = round(float(self.amount) * float((porcentage_itf / 100.00)), 2)
        else:
            currency = self.currency_id.id
            amount_currency = round(float(self.amount) * float((porcentage_itf / 100.00)), 2)
            if self.manual_currency_exchange_rate > 0:
                amount_itf = round(float(self.amount*self.manual_currency_exchange_rate) * float((porcentage_itf / 100.00)), 2)
            else:
                raise UserError(_('Por favor Registrar la tasa para poder hacer la respectiva conversion y poder continuar'))
        lines_vals_list_2.append({
            'account_id': self.journal_id.payment_credit_account_id.id,#V14
            'company_id': self._get_company().id,
            'currency_id': currency,
            'date_maturity': False,
            'ref': "Comisión del %s %% del pago %s por IGTF" % (porcentage_itf,self.name),
            'date': self.date,
            'partner_id': self.partner_id.id,
            'move_id': move_id.id,
            'name': "Comisión del %s %% del pago %s por IGTF" % (porcentage_itf, self.name),
            'journal_id': self.journal_id.id,
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
            'date': self.date,
            'partner_id': self.partner_id.id,
            'move_id': move_id.id,
            'name': "Comisión del %s %% del pago %s por IGTF" % (porcentage_itf, self.name),
            'journal_id': self.journal_id.id,
            'credit': 0.0,
            'debit': float(amount_itf),
            'amount_currency': amount_currency,
        })
        move_line_obj = self.env['account.move.line'].sudo()
        move_line_id1 = move_line_obj.create(lines_vals_list_2)
        #move_line_id2 = move_line_obj.create()
        #raise UserError(('las líneas son: %s y ')%(move_line_id1))
        if move_line_id1:
            #res = {'move_itf_id': move_id.id}
            self.move_itf_id = move_id.id
            #move_id.name = name_line
            move_id.action_post()
        return True

    @api.model
    def _get_company(self):
        '''Método que busca el id de la compañia'''
        company_id = self.env.company
        return company_id

    def _get_company_itf(self):
        '''Método que retorna verdadero si la compañia debe retener el impuesto ITF'''
        company_id = self._get_company()
        if company_id.calculate_wh_itf:
            return True
        return False

    @api.model
    def check_payment_type(self):
        '''metodo que chequea que el tipo de pago si pertenece al tipo outbound'''
        type_bool = False
        for pago in self:
            type_payment = pago.payment_type
            if type_payment == 'outbound' and pago.partner_type == 'supplier':
                type_bool = True
        return type_bool


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


    # def get_name_igtf(self):
    #     '''metodo que crea el name del asiento contable si la secuencia no esta creada crea una con el
    #     nombre: 'l10n_account_withholding_itf'''
    #     self.ensure_one()
    #     SEQUENCE_CODE = 'l10n_account_withholding_itf'
    #     company_id = self._get_company()
    #     IrSequence = self.env['ir.sequence'].with_context(force_company=company_id.id)
    #     name_line = IrSequence.next_by_code(SEQUENCE_CODE)
    #     # if a sequence does not yet exist for this company create one
    #     if not name_line:
    #         IrSequence.sudo().create({
    #             'prefix': 'IGTF',
    #             'name': 'Localización Venezolana impuesto IGTF %s' % company_id.id,
    #             'code': SEQUENCE_CODE,
    #             'implementation': 'no_gap',
    #             'padding': 8,
    #             'number_increment': 1,
    #             'company_id': company_id.id,
    #         })
    #         name_line = IrSequence.next_by_code(SEQUENCE_CODE)
    #     return name_line


    def action_cancel(self):
        """Calcela el movimiento contable si se cancela el pago de las facturas"""
        res = super(AccountPaymentInnerit, self).action_cancel()
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