# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions,_
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError
from odoo.exceptions import Warning


class AccountAdvancePayment(models.Model):
    _name = 'account.advanced.payment'
    _description = 'Advance payments'

    ADVANCE_PAYMET_STATES = [('draft', 'Sin Publicar'),
                             ('cancel', 'Cancelado'),
                             ('available', 'Disponible'),
                             ('paid', 'Pagado')]

    name = fields.Char(string='Name')
    supplier = fields.Boolean(string='Supplier')
    customer = fields.Boolean(string='Customer')
    partner_id = fields.Many2one('res.partner', string='Socio')
    journal_id = fields.Many2one('account.journal', string='Journal', related='partner_id.journal_advanced_id')
    apply_journal_id = fields.Many2one('account.journal', string='Journal applied', related='partner_id.journal_advanced_id')
    bank_account_id = fields.Many2one('account.journal',string='Bank')
    advance_account_id = fields.Many2one('account.journal',string='Bank')
    payment_id = fields.Char(string='Payment Methods')
    date_advance = fields.Date(string='Advance Date')
    currency_id = fields.Many2one('res.currency', string='Currency')
    amount_advance = fields.Monetary(string="Amount advance")
    ref = fields.Char(string= 'Referencia')
    move_id = fields.Many2one('account.move', 'Asiento contable')
    move_line = fields.One2many('account.move.line',
                                         related='move_id.line_ids',
                                         string='Asientos contables', readonly=True)
    move_apply_id = fields.Many2one('account.move', 'Asiento contable')
    move_apply_line = fields.One2many('account.move.line',
                                related='move_id.line_ids',
                                string='Asientos contables', readonly=True)
    move_refund_id = fields.Many2one('account.move', 'Asiento contable')
    move_refund_line = fields.One2many('account.move.line',
                                      related='move_id.line_ids',
                                      string='Asientos contables', readonly=True)
    state = fields.Selection(ADVANCE_PAYMET_STATES, string='Status',readonly=True, copy=False, default='draft')
    asiento_conciliado = fields.One2many('account.move.line', related='move_id.line_ids', string='Asientos contables', readonly=True)
    asiento_conl_apply = fields.One2many('account.move.line', related='move_apply_id.line_ids', string='Asientos contables',
                                         readonly=True)
    amount_available_conversion = fields.Monetary("Conversión Monto Disponible", currency_field='conversion_currency', store=True)
    amount_available = fields.Monetary("Amount Available", currency_field='currency_id')
    date_apply = fields.Date(string='Date apply')
    invoice_id = fields.Many2one('account.move',string='Invoice')
    amount_invoice = fields.Monetary(string='Amount Invoice',compute='_compute_amount_invoice', currency_field='invoice_currency')
    invoice_currency = fields.Many2one('res.currency', string='Invoice Currency')
    conversion_currency = fields.Many2one('res.currency', string='Conversion Currency')
    amount_currency_apply = fields.Many2one('res.currency', string='Moneda del monto', store=True)
    amount_apply = fields.Monetary(string='Amount Apply', currency_field='amount_currency_apply')
    is_customer = fields.Boolean("Is customer", default= True)
    is_supplier = fields.Boolean("Is Supplier", default=True)
    rate = fields.Float(digits=0, default=1.0, help='Tasa de registro del anticipo')
    type_advance = fields.Boolean(default=False)

    @api.onchange('date_apply')
    def onchange_date_apply(self):
        for i in self:
            if i.currency_id != self.env.company.currency_id:
                i.amount_available_conversion = i.currency_id._convert(i.amount_available, self.env.company.currency_id, i.env.company, i.date_apply)

    def validate_amount_advance(self):
        if self.amount_advance <= 0:
            raise Warning(_('El monto de anticipo debe ser mayor que cero'))

        return True

    def validate_amount_apply(self):
        if self.amount_apply <= 0:
            raise Warning(_('El monto a aplicar debe ser mayor que cero'))

        return True

    @api.depends('invoice_id')
    def _compute_amount_invoice(self):
        '''Actualiza el campo de monto de la faltura con el saldo de la factura'''
        for rec in self:
            rec.invoice_currency = rec.invoice_id.currency_id
            rec.amount_invoice = rec.invoice_id.amount_residual
            if rec.invoice_id:
                if not rec.date_apply:
                    raise exceptions.Warning(_('Selecciona una fecha de aplicación'))
                rec.invoice_currency = rec.invoice_id.currency_id

    def unlink(self):
        '''convierte a borrador la vista para ser editada'''
        for move_id in self:
            if move_id.state not in ('draft','cancel'):
                raise Warning (_('You cannot delete an advance payment is not draft or cancelled'))
        return models.Model.unlink(self)

    def copy(self, default=None):
        '''Duplica un nuevo anticipo con estado disponible si el monto disponible es diferente de cero'''
        if default is None:
            default = {}
        default = default.copy()
        #local_amount_available = self.amount_available-self.amount_apply
        if self.amount_available > 0:
            default.update({
                'name': self.name,
                'partner_id': self.partner_id.id,
                'invoice_id': None,
                'amount_advance': self.amount_advance,
                'amount_available': self.amount_available,
                'amount_apply': 0.0,
                'state':'available',
            })
        # Se crea una copia del anticipo cuando se cancela un anticipo que fue procesado completamente
        elif self.amount_available == 0 and self.state == 'paid':
            default.update({
                'name': self.name,
                'partner_id': self.partner_id.id,
                'invoice_id': None,
                'amount_advance': self.amount_advance,
                'amount_available': self.amount_available + self.amount_apply,
                'amount_apply': 0.0,
                'state': 'available',
            })

            #raise Warning(_('El monto a aplicar (%s) no puede ser mayor al monto disponible'))

        return super(AccountAdvancePayment, self).copy(default)

    def validate_amount(self, vals):
        '''Se validan el monto a aplicar, ya que no puede ser mayor al disponible, ni mayor al monto de la factura'''
        adv_obj = self.env['account.advanced.payment']
        amount_apply = float(vals.get('amount_apply')) if vals.get('amount_apply',False) else 0.00
        amount_invoice = float(vals.get('amount_invoice')) if vals.get('amount_invoice', False) else 0.00
        date_apply = vals.get('date_apply')
        invoice_currency = vals.get('invoice_currency')
        amount_available = vals.get('amount_available')
        amount_currency_apply = vals.get('amount_currency_apply')
        amount_available_conversion = vals.get('amount_available_conversion')

        if amount_currency_apply == self.currency_id.id:
            if amount_apply > amount_available:
                raise Warning(_('El monto a aplicar (%s) no puede ser mayor al monto disponible (%s)') % (amount_apply, self.amount_available))

        else:
            if amount_apply > amount_available_conversion:
                raise Warning(_('El monto a aplicar (%s) no puede ser mayor al monto disponible (%s)') % (
                amount_apply, amount_available_conversion))
        if amount_currency_apply == invoice_currency:
            if amount_apply > amount_invoice:
                continue
                #raise Warning(_('El monto a aplicar (%s) no puede ser mayor al monto de la factura (%s)') % (
                #amount_apply, amount_invoice))
        else:
            currency_rate = self.env['res.currency.rate'].search([
                ('currency_id', '=', self.env.company.currency_id.id),
                ('name', '=',date_apply),
            ]).rate
            if amount_currency_apply == self.env.company.currency_id.id:
                if self.currency_id.id == self.env.company.currency_id.id:
                    if not currency_rate:
                        raise Warning(_('Registre una tasa de cambio para la fecha de aplicación'))
                    conversion = amount_apply / currency_rate
                    if conversion > amount_invoice:
                        raise Warning(_('El monto a aplicar (%s) no puede ser mayor al monto de la factura (%s)') % (
                            conversion, amount_invoice))
                else:
                    conversion = amount_apply / self.rate
                    if conversion > amount_invoice:
                        raise Warning(_('El monto a aplicar (%s) no puede ser mayor al monto de la factura (%s)') % (
                            conversion, amount_invoice))
            else:
                if self.currency_id == self.env.company.currency_id.id:
                    if not currency_rate:
                        raise Warning(_('Registre una tasa de cambio para la fecha de aplicación'))
                    conversion = amount_apply * currency_rate
                    if conversion > amount_invoice:
                        raise Warning(_('El monto a aplicar (%s) no puede ser mayor al monto de la factura (%s)') % (
                            conversion, amount_invoice))
                else:
                    conversion = amount_apply * self.rate
                    if conversion > amount_invoice:
                        raise Warning(_('El monto a aplicar (%s) no puede ser mayor al monto de la factura (%s)') % (
                            conversion, amount_invoice))
        return True

    @api.depends('partner_id', 'journal_id', 'partner_id', 'date_advance')
    def action_register_advance(self):
        '''funcionalidad del boton validate este hace llamada a las fucniones que realizan los asientos contables'''
        if self.state == 'draft':
            self.validate_amount_advance()
            self.get_move_register()

        elif self.state == 'posted' or 'available':
            self.validate_amount_apply()
            self.get_move_apply()

            if self.amount_available > 0:
                self.copy()
                self.state = 'paid'
                


    def write(self, vals):
        '''sobreescritura del boton editar '''
        if vals.get('amount_apply') or vals.get('amount_invoice'):
            if self.state == 'available':
                local_invoice_id = vals.get('invoice_id', False) or self.invoice_id
                #isisntance es una funcion que pregunta si es una instancia y la convierte a intero
                if isinstance(local_invoice_id, int):
                    local_invoice_id = self.env['account.move'].browse(local_invoice_id)
                if not vals.get('amount_apply', False):
                    vals.update({'amount_apply':self.amount_apply})
                if not vals.get('amount_available', False):
                    vals.update({'amount_available':self.amount_available})
                if not vals.get('amount_invoice', False):
                    vals.update({'amount_invoice':local_invoice_id.amount_residual})
                if not vals.get('amount_currency_apply', False):
                    vals.update({'amount_currency_apply':self.amount_currency_apply.id})
                if not vals.get('amount_available_conversion', False):
                    vals.update({'amount_available_conversion':self.amount_available_conversion})
                if not vals.get('date_apply', False):
                    vals.update({'date_apply':self.date_apply})
                if self.validate_amount(vals):
                    amount_apply = vals.get('amount_apply')
                    amount_currency_apply = vals.get('amount_currency_apply')
                    if amount_currency_apply == self.currency_id.id:
                        self.amount_available = self.amount_available - amount_apply
                        vals.update({'amount_available': self.amount_available})
                    else:
                        date_apply = vals.get('date_apply') if vals.get('date_apply', False) else self.date_apply
                        if amount_currency_apply == self.env.company.currency_id.id:
                            self.amount_available = self.amount_available - self.amount_apply
                            vals.update({'amount_available': self.amount_available})
                        else:
                            conversion = amount_apply * currency_rate
                            self.amount_available = self.amount_available - self.currency_id._convert(self.amount_apply, self.env.company.currency_id, self.env.company, rec.date_advance)
                            self.amount_available = self.amount_available - conversion
                            vals.update({'amount_available': self.amount_available})

                else:
                    self.state = 'paid'

        if vals.get('amount_advance'):
            if self.state == 'draft':
                if vals.get('amount_currency_apply') == self.currency_id.id:
                    self.amount_available = self.amount_advance - self.amount_apply
                else:
                    currency_rate = self.env['res.currency.rate'].search([
                        ('currency_id', '=', self.env.company.currency_id.id),
                        ('name', '=', vals.get('date_apply')),
                    ]).rate
                    if vals.get('amount_currency_apply') == self.env.company.currency_id.id:
                        conversion = self.amount_apply / currency_rate
                        self.amount_available = self.amount_advance - conversion
                    else:
                        conversion = self.amount_apply * currency_rate
                        self.amount_available = self.amount_advance - conversion
                vals.update({'amount_available': self.amount_available,
                             'is_supplier':self.partner_id.es_proveedor,
                             'is_customer':self.partner_id.es_cliente})

        return super(AccountAdvancePayment, self).write(vals)

    @api.model
    def create(self, vals):
        if vals.get('is_supplier') == True and self.partner_id.es_cliente == False:
            vals.update({'supplier': ((self.env['res.partner'].browse(vals['partner_id']).es_cliente) == False), 'is_customer': False})
            self.is_customer = False
        else:
            vals.update({'customer': self.env['res.partner'].browse(vals['partner_id']).es_cliente, 'is_supplier': False})
            self.is_supplier = False
        res = super(AccountAdvancePayment, self).create(vals)
        return res

    @api.model
    def get_account_advance(self):
        '''obtiene la cuentas contables segun el proveedor o cliente, para el registro de los anticipos'''
        cuenta_acreedora = None
        cuenta_deudora = None
        partner_id = None
        sequence_code = None
        is_customer = None
        is_supplier = None

        # if self.is_customer and self.state == 'draft':
        if self.partner_id.es_cliente and self.state == 'draft' and self.type_advance == False:
            cuenta_deudora = self.bank_account_id.default_debit_account_id.id
            cuenta_acreedora = self.partner_id.account_advance_payment_sales_id.id
            partner_id = self.partner_id.id
            sequence_code = 'register.receivable.advance.customer'
            self.is_customer = True
            self.is_supplier = False

        # elif self.is_supplier and self.state == 'draft':
        elif self.partner_id.es_proveedor and self.state == 'draft' and self.type_advance:
            cuenta_deudora = self.partner_id.account_advance_payment_purchase_id.id
            cuenta_acreedora = self.bank_account_id.default_debit_account_id.id
            partner_id = self.partner_id.id
            sequence_code = 'register.payment.advance.supplier'
            self.is_supplier = True
            self.is_customer = False

        return cuenta_deudora,cuenta_acreedora,partner_id,sequence_code,is_supplier,is_customer

    def get_account_apply(self):
        '''obtiene la cuentas contables segun el proveedor o cliente, para la aplicacion de los anticipos'''
        cuenta_acreedora = None
        cuenta_deudora = None

        if self.partner_id.es_cliente and self.state in ['posted', 'available', 'paid'] and self.type_advance == False:
            cuenta_deudora = self.partner_id.property_account_receivable_id.id
            cuenta_acreedora = self.partner_id.account_advance_payment_sales_id.id


        elif self.partner_id.es_proveedor and self.state in ['posted', 'available', 'paid'] and self.type_advance:
            cuenta_deudora = self.partner_id.account_advance_payment_purchase_id.id
            cuenta_acreedora = self.partner_id.property_account_payable_id.id

        return cuenta_acreedora,cuenta_deudora

    def get_account_refund(self):
        '''obtiene la cuentas contables segun el proveedor o cliente, para el reintegro de monto residual de los anticipos'''
        cuenta_acreedora = None
        cuenta_deudora = None
        partner_id = None
        #sequence_code = None

        if self.partner_id.es_cliente and self.state == 'available' and self.type_advance == False:
            cuenta_deudora = self.partner_id.account_advance_payment_sales_id.id
            cuenta_acreedora = self.bank_account_id.default_debit_account_id.id
            partner_id = self.partner_id.id
            #sequence_code = 'register.receivable.advance.customer'

        elif self.partner_id.es_proveedor and self.state == 'available' and self.type_advance:
            cuenta_deudora = self.bank_account_id.default_debit_account_id.id
            cuenta_acreedora = self.partner_id.account_advance_payment_purchase_id.id
            partner_id = self.partner_id.id
            #sequence_code = 'register.payment.advance.supplier'

        return cuenta_deudora,cuenta_acreedora,partner_id

    def get_move_register(self):
        '''se crea el asiento contable para el registro'''
        for rec in self:
            name = None

            cuenta_deudora, cuenta_acreedora,partner_id,sequence_code,is_supplier,is_customer = rec.get_account_advance()
            #busca la secuencia del diario y se lo asigno a name
            if rec.partner_id.es_cliente and not cuenta_acreedora and rec.type_advance == False:
                    raise exceptions.Warning(_('El cliente no tiene configurado la cuenta contable de anticipo'))
            elif rec.partner_id.es_proveedor and not cuenta_deudora and rec.type_advance:
                    raise exceptions.Warning(_('El proveedor no tiene configurado la cuenta contable de anticipo'))

            else:
                name = self.env['ir.sequence'].with_context(ir_sequence_date=self.date_advance).next_by_code(sequence_code)
                vals = {
                    # 'name': name,
                    'date': rec.date_advance,
                    'journal_id': rec.journal_id.id,
                    'line_ids': False,
                    'state': 'draft',
                }
                move_obj = self.env['account.move']
                move_id = move_obj.create(vals)
                #Si el pago es en moneda extranjera $
                if rec.currency_id.id != self.env.company.currency_id.id:
                    # modificar
                    #if not currency_rate:
                    #    raise exceptions.Warning(_('Asegurese de tener la multimoneda configurada y registrar la tasa de la fecha del anticipo'))
                    money = rec.currency_id._convert(rec.amount_advance, self.env.company.currency_id, self.env.company, rec.date_advance)
                    rec.move_advance_ = {
                        'account_id': cuenta_acreedora,
                        'company_id': rec.partner_id.company_id.id,
                        'currency_id': rec.currency_id.id,
                        'date_maturity': False,
                        'ref': rec.ref,
                        'date': rec.date_advance,
                        'partner_id': rec.partner_id.id,
                        'move_id': move_id.id,
                        'name': name,
                        'journal_id': rec.journal_id.id,
                        'credit':  money,
                        'debit': 0.0,
                        'amount_currency': -rec.amount_advance,
                    }
                    asiento = rec.move_advance_
                    move_line_obj = self.env['account.move.line']
                    move_line_id1 = move_line_obj.with_context(check_move_validity=False).create(asiento)
                    asiento['amount_currency'] = rec.amount_advance
                    asiento['account_id'] = cuenta_deudora
                    asiento['credit'] = 0.0
                    asiento['debit'] = money
                    move_line_id2 = move_line_obj.create(asiento)
                    move_id.action_post()

                    if move_line_id1 and move_line_id2:
                        if rec.partner_id.es_proveedor and rec.type_advance:
                            res = {'state': 'available', 'move_id': move_id.id, 'supplier': True,
                                   'amount_available': rec.amount_advance, 'name': name, 'is_supplier': True}
                        else:
                            res = {'state': 'available', 'move_id': move_id.id, 'customer': True,
                                   'amount_available': rec.amount_advance, 'name': name, 'is_customer': True}
                        return super(AccountAdvancePayment, self).write(res)
                else:
                    rec.amount_currency_apply = self.env.company.currency_id
                    rec.move_advance_ = {
                        'account_id': cuenta_acreedora,
                        'company_id': rec.partner_id.company_id.id,
                        'date_maturity': False,
                        'ref': rec.ref,
                        'date': rec.date_advance,
                        'partner_id': rec.partner_id.id,
                        'move_id': move_id.id,
                        'name': name,
                        'journal_id': rec.journal_id.id,
                        'credit': rec.amount_advance,
                        'debit': 0.0,
                    }
                    asiento = rec.move_advance_
                    move_line_obj = self.env['account.move.line']
                    move_line_id1 = move_line_obj.with_context(check_move_validity=False).create(asiento)

                    asiento['account_id'] = cuenta_deudora
                    asiento['credit'] = 0.0
                    asiento['debit'] = rec.amount_advance

                    move_line_id2 = move_line_obj.create(asiento)
                    move_id.action_post()

                    if move_line_id1 and move_line_id2:
                        if rec.partner_id.es_proveedor and rec.type_advance:
                            res = {'state': 'available', 'move_id': move_id.id, 'supplier':True, 'amount_available':rec.amount_advance,'name':name, 'is_supplier':True}
                        else:
                            res = {'state': 'available', 'move_id': move_id.id, 'customer':True, 'amount_available':rec.amount_advance,'name':name, 'is_customer':True}
                        return super(AccountAdvancePayment, self).write(res)
            return True

    def get_move_apply(self):
        '''se crea el asiento contable para el resgitro de la aplicacion del anticipo'''

        cuenta_deudora, cuenta_acreedora = self.get_account_apply()

        vals = {
            'date': self.date_apply,
            'journal_id': self.journal_id.id,
            'line_ids': False,
            'state': 'draft',
        }
        move_apply_obj = self.env['account.move']
        move_apply_id = move_apply_obj.create(vals)
        if self.amount_currency_apply != self.env.company.currency_id:
                self.move_advance_ = {
                    'account_id': cuenta_acreedora,
                    'company_id': self.partner_id.company_id.id,
                    'currency_id': self.currency_id.id,
                    'date_maturity': False,
                    'ref': self.ref,
                    'date': self.date_apply,
                    'partner_id': self.partner_id.id,
                    'move_id': move_apply_id.id,
                    'name': self.name,
                    'journal_id': self.journal_id.id,
                    'credit': self.amount_currency_apply._convert(self.amount_apply, self.env.company.currency_id, self.env.company, self.date_apply),
                    'debit': 0.0,
                    'amount_currency': -(self.amount_apply),
                }

                asiento_apply = self.move_advance_
                move_line_obj = self.env['account.move.line']
                move_line_id1 = move_line_obj.with_context(check_move_validity=False).create(asiento_apply)

                asiento_apply['amount_currency'] = self.amount_apply
                asiento_apply['account_id'] = cuenta_deudora
                asiento_apply['credit'] = 0.0
                asiento_apply['debit'] = self.amount_currency_apply._convert(self.amount_apply, self.env.company.currency_id, self.env.company, self.date_apply)

        else:
                self.move_advance_ = {
                    'account_id': cuenta_acreedora,
                    'company_id': self.partner_id.company_id.id,
                    'date_maturity': False,
                    'ref': self.ref,
                    'date': self.date_apply,
                    'partner_id': self.partner_id.id,
                    'move_id': move_apply_id.id,
                    'name': self.name,
                    'journal_id': self.journal_id.id,
                    'credit': self.amount_apply,
                    'debit': 0.0,
                }

                asiento_apply = self.move_advance_
                move_line_obj = self.env['account.move.line']
                move_line_id1 = move_line_obj.with_context(check_move_validity=False).create(asiento_apply)

                asiento_apply['account_id'] = cuenta_deudora
                asiento_apply['credit'] = 0.0
                asiento_apply['debit'] = self.amount_apply

        move_line_id2 = move_line_obj.create(asiento_apply)
        move_apply_id.action_post()
        res = {'state': 'paid', 'move_apply_id': move_apply_id.id, 'amount_available': self.amount_available}
        self.write(res)
        if self.currency_id.name != self.env.company.currency_id.name:
            self.amount_available_conversion = self.currency_id._convert(self.amount_available, self.env.company.currency_id, self.env.company, self.date_apply)

        return True

    def action_refund_amount_available(self):
        '''Crea un asiento contable con el monto residual disponible que queda de una aplicacion de anticipo'''
        if self.state == 'available':

            cuenta_deudora, cuenta_acreedora, partner_id = self.get_account_refund()

            vals = {
                # 'name': self.name,
                'date': self.date_apply,
                'journal_id': self.journal_id.id,
                'line_ids': False,
                'state': 'draft',
            }
            move_obj = self.env['account.move']
            move_refund_id = move_obj.create(vals)
            if self.currency_id == self.env.company.currency_id:
                self.move_advance_ = {
                    'account_id': cuenta_acreedora,
                    'company_id': self.partner_id.company_id.id,
                    'date_maturity': False,
                    'ref': self.ref,
                    'date': self.date_apply,
                    'partner_id': self.partner_id.id,
                    'move_id': move_refund_id.id,
                    'name': self.name,
                    'journal_id': self.journal_id.id,
                    'credit': self.amount_available,
                    'debit': 0.0,
                }

                asiento = self.move_advance_
                move_line_obj = self.env['account.move.line']
                move_line_id1 = move_line_obj.with_context(check_move_validity=False).create(asiento)

                asiento['account_id'] = cuenta_deudora
                asiento['credit'] = 0.0
                asiento['debit'] = self.amount_available
            else:
                self.move_advance_ = {
                    'account_id': cuenta_acreedora,
                    'company_id': self.partner_id.company_id.id,
                    'currency_id': self.currency_id.id,
                    'date_maturity': False,
                    'ref': self.ref,
                    'date': self.date_apply,
                    'partner_id': self.partner_id.id,
                    'move_id': move_refund_id.id,
                    'name': self.name,
                    'journal_id': self.journal_id.id,
                    'credit': self.amount_available * self.rate,
                    'debit': 0.0,
                    'amount_currency': -(self.amount_available),
                }

                asiento = self.move_advance_
                move_line_obj = self.env['account.move.line']
                move_line_id1 = move_line_obj.with_context(check_move_validity=False).create(asiento)

                asiento['amount_currency'] = self.amount_available
                asiento['account_id'] = cuenta_deudora
                asiento['credit'] = 0.0
                asiento['debit'] = self.amount_available * self.rate

            move_line_id2 = move_line_obj.create(asiento)
            move_refund_id.action_post()

            if move_line_id1 and move_line_id2:
                res = {'state': 'cancel',
                       'move_refund_id': move_refund_id.id,
                       'amount_invoice':0,
                       'amount_apply':0,
                       'invoice_id':None}
                self.write(res)
            return True

    def action_cancel(self):
        '''accion del boton cancelar para el resgitro cuando esta available o cancelar la
        aplicacion con esta es estado paid'''
        if self.state == 'available':
            if not self.move_apply_id:
                for advance in self:
                    for move in advance.move_id:
                        move_reverse = move._reverse_moves(cancel=True)
                        if len(move_reverse)==0:
                            raise UserError(_('No se reversaron los asientos asociados'))
                        res = {'state': 'cancel'}
                        return super(AccountAdvancePayment, self).write(res)
            else:
                raise exceptions.ValidationError('El anticipo ya tiene una aplicacion')

        elif self.state == 'paid':
            dominio = [('name', '=', self.name),
                       ('move_id','=',self.move_apply_id.id),
                       ('reconciled','=',True)]
            obj_move_line = self.env['account.move.line'].search(dominio)
            if obj_move_line:
                raise exceptions.ValidationError(('El anticipo ya tiene una aplicacion en la factura %s') % self.invoice_id.name)
            else:
                for advance in self:
                    for move in advance.move_apply_id:
                        move_reverse = move._reverse_moves(cancel=True)
                        if len(move_reverse)== 0:
                            raise UserError(_('No se reversaron los asientos asociados'))

                    dominio_new = [('name','=',self.name),('state','=','available')]
                    reg_new = self.search(dominio_new)

                    if reg_new:
                        result= super(AccountAdvancePayment,reg_new).write({'amount_available':self.amount_available + self.amount_apply})
                    else:
                        self.copy()

            res = {'state':'cancel'}
            return super(AccountAdvancePayment, self).write(res)
        return True

    def set_to_draft(self):
        '''convierte a borrador el regsitro de anticipo'''
        res = {'state': 'draft'}
        return super(AccountAdvancePayment, self).write(res)

class account_move(models.Model):
    _inherit = 'account.move'


    def assert_balanced(self):
        if not self.ids:
            return True
        mlo = self.env['account.move.line'].search([('move_id', '=',self.ids[0])])
        if not mlo.reconcile:
            super(account_move, self).assert_balanced(fields)
        return True

