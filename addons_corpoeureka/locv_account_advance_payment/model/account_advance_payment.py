# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions,_
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError
from odoo.exceptions import Warning


class AccountAdvancePayment(models.Model):
    _name = 'account.advanced.payment'
    _description = 'Advance payments'
    _inherit= ['mail.thread', 'mail.activity.mixin']
    _order = 'id asc'

    ADVANCE_PAYMET_STATES = [('draft', 'Sin Publicar'),
                             ('cancel', 'Cancelado'),
                             ('available', 'Disponible'),
                             ('paid', 'Pagado')]
    # Datos no numéricos
    name                = fields.Char(string='Name')
    payment_id          = fields.Char(string='Motivo del Anticipo')
    ref                 = fields.Char(string= 'Referencia')
    partner_id          = fields.Many2one('res.partner', string='Contacto')
    journal_id          = fields.Many2one('account.journal', string='Journal', related='partner_id.journal_advanced_id',readonly=True)
    apply_journal_id    = fields.Many2one('account.journal', string='Journal applied', related='partner_id.journal_advanced_id')
    bank_account_id     = fields.Many2one('account.journal',string='Bank', domain="[('type','in',['bank','cash'])]",)
    advance_account_id  = fields.Many2one('account.journal',string='Bank')
    invoice_id          = fields.Many2one('account.move',string='Factura a Asociar',domain=[('amount_residual', '>', 0)])
    company_id          = fields.Many2one('res.company', string='Compañia', required=True, readonly=True,default=lambda self: self.env.company.id,help="Compañía")
    date_advance        = fields.Date(string='Fecha del anticipo')
    date_contable       = fields.Date(string='Fecha Contable')
    date_apply          = fields.Date(string='Fecha Efectiva')
    date                = fields.Datetime(string="Fecha de Creación",track_visibility='always',default=lambda self: fields.Datetime.now(),readonly=True)
    es_cliente         = fields.Boolean("Cliente", default= True)
    supplier            = fields.Boolean(string='Supplier')
    customer            = fields.Boolean(string='Customer')
    es_proveedor         = fields.Boolean(string="Proveedor", default=True)
    type_advance        = fields.Boolean(default=False)
    state               = fields.Selection(ADVANCE_PAYMET_STATES, string='Estatus',readonly=True, copy=False, default='draft')
    
    # Relación con factura y líneas contables
    move_id     = fields.Many2one('account.move', 'Asiento contable')
    move_line   = fields.One2many('account.move.line',
                                         related='move_id.line_ids',
                                         string='Asientos contables', readonly=True)
    move_apply_id   = fields.Many2one('account.move', 'Asiento contable')
    move_apply_line = fields.One2many('account.move.line',
                                related='move_id.line_ids',
                                string='Asientos contables', readonly=True)
    move_refund_id   = fields.Many2one('account.move', 'Asiento contable')
    move_refund_line = fields.One2many('account.move.line',
                                      related='move_id.line_ids',
                                      string='Asientos contables', readonly=True)
    asiento_conciliado = fields.One2many('account.move.line', related='move_id.line_ids', string='Asientos contables', readonly=True)
    asiento_conl_apply = fields.One2many('account.move.line', related='move_apply_id.line_ids', string='Asientos contables',
                                         readonly=True)

    # Campos moneda - currency
    currency_id      = fields.Many2one('res.currency', string='Moneda del Anticipo')
    currency_id_usd  = fields.Many2one('res.currency', string='Moneda del Anticipo $')
    invoice_currency = fields.Many2one('res.currency', string='Moneda de la Factura')
    company_currency = fields.Many2one("res.currency", string="Moneda de la compañía", default=lambda self: self.env.company.currency_id.id)

    # Datos numéricos
    amount_advance              = fields.Monetary(string="Monto del Anticipo", currency_field='currency_id')
    amount_advance_usd          = fields.Monetary(string="Monto del Anticipo $", currency_field='currency_id_usd',compute="_compute_amount_advance_usd",readonly=True)
    amount_advance_bs           = fields.Monetary(string="Monto del Anticipo $", currency_field='company_currency',compute="_compute_amount_advance_bs",readonly=True)
    
    amount_available            = fields.Monetary(string="Monto Disponible", currency_field='currency_id')
    amount_available_conversion = fields.Monetary(string="Monto Disponible (Company Currency)", currency_field='company_currency', store=True)
    
    amount_apply                = fields.Monetary(string='Monto a Aplicar', currency_field='currency_id')
    amount_apply_conversion     = fields.Monetary(string='Monto a Aplicar (Company Currency)', currency_field='company_currency')
    
    amount_invoice              = fields.Monetary(string='Monto de la Factura',compute='_compute_amount_invoice', currency_field='invoice_currency')
    amount_invoice_in_company   = fields.Monetary(string="Monto Factura (Company Currency)", currency_field='company_currency')

    apply_manual_currency_exchange = fields.Boolean(string='Aplicar cambio de tasa manual')
    manual_currency_exchange_rate = fields.Float(string='Tipo de tasa manual', digits=(20,16),default=lambda self: self.env.company.currency_id.parent_id.rate)
    manual_currency_exchange_rate_ref = fields.Float(string='Tasa', digits=(20,16),compute="_compute_ref")

    @api.onchange('currency_id')
    def onchange_manual_currency_exchange(self):
        for rec in self:
            if rec.currency_id == self.env.company.currency_id:
                rec.manual_currency_exchange_rate = self.env.company.currency_id.parent_id.rate
            else:
                rec.manual_currency_exchange_rate = 1 / self.env.company.currency_id.parent_id.rate


    @api.depends('manual_currency_exchange_rate')
    def _compute_ref(self):
        for rec in self:
            rec.manual_currency_exchange_rate_ref = 1 / rec.manual_currency_exchange_rate
      
    @api.depends('amount_advance','manual_currency_exchange_rate','currency_id')
    def _compute_amount_advance_usd(self):
        for rec in self:
            if rec.currency_id == rec.env.company.currency_id:
                rec.amount_advance_usd = rec.amount_advance * rec.manual_currency_exchange_rate
            else:
                rec.amount_advance_usd = rec.amount_advance

    @api.depends('amount_advance','manual_currency_exchange_rate','currency_id')
    def _compute_amount_advance_bs(self):
        for rec in self:
            if rec.currency_id != rec.env.company.currency_id:
                rec.amount_advance_bs = rec.amount_advance * rec.manual_currency_exchange_rate
            else:
                rec.amount_advance_bs = rec.amount_advance

    @api.onchange('date_apply')
    def onchange_date_apply(self):
        for i in self:
            if i.currency_id != self.env.company.currency_id:
                #i.amount_available_conversion = i.currency_id._convert(i.amount_available, self.env.company.currency_id, i.env.company, i.date_apply or fields.date.today())
                i.amount_available_conversion = i['amount_available']*i.manual_currency_exchange_rate
            else:
                i.amount_available_conversion = i.amount_available

    @api.onchange('amount_apply')
    def onchange_amount_apply(self):
        for i in self:
            if i.currency_id != self.env.company.currency_id:
                #i.amount_apply_conversion = i.currency_id._convert(i.amount_apply, self.env.company.currency_id, i.env.company, i.date_apply or fields.date.today())
                i.amount_apply_conversion = i['amount_apply'] * i.manual_currency_exchange_rate
            else:
                i.amount_apply_conversion = i.amount_apply

    def validate_amount_advance(self):
        if self.amount_advance <= 0:
            raise Warning(_('El monto del anticipo debe ser mayor que cero'))

        return True

    def validate_amount_apply(self):
        if self.amount_apply <= 0:
            raise Warning(_('El monto a aplicar debe ser mayor que cero'))

        return True

    @api.depends('invoice_id')
    def _compute_amount_invoice(self):
        for rec in self:
            rec.amount_invoice = 0
            if rec.invoice_id:
                if not rec.date_apply:
                    raise exceptions.Warning(_('Selecciona una fecha de aplicación'))
                rec.invoice_currency = rec.invoice_id.currency_id
                rec.amount_invoice   = rec.invoice_id.amount_residual
                rec.invoice_currency = rec.invoice_id.currency_id
                if rec.invoice_currency != self.env.company.currency_id:
                    rec.amount_invoice_in_company = rec.invoice_currency._convert(rec.amount_invoice, self.env.company.currency_id, rec.invoice_id.company_id, rec.date_apply or fields.date.today())
                else:
                    rec.amount_invoice_in_company = rec.amount_invoice

    def unlink(self):
        for move_id in self:
            if move_id.state not in ('draft','cancel'):
                raise Warning (_('No puedes borrar un anticipo que esté en borrador o en cancelado'))
        return models.Model.unlink(self)

    def copy(self, default=None):
        '''Duplica un nuevo anticipo con estado disponible si el monto disponible es diferente de cero'''
        if default is None:
            default = {}
        default = default.copy()
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
        return super(AccountAdvancePayment, self).copy(default)

    def validate_amount(self, vals):
        
        for rec in self:
            '''Se validan el monto a aplicar, ya que no puede ser mayor al disponible, ni mayor al monto de la factura'''
            adv_obj                     = self.env['account.advanced.payment']
            amount_apply                = float(vals.get('amount_apply')) if vals.get('amount_apply',False) else 0.00
            amount_invoice              = float(vals.get('amount_invoice')) if vals.get('amount_invoice', False) else 0.00
            date_apply                  = vals.get('date_apply')
            invoice_currency            = vals.get('invoice_currency')
            amount_available            = vals.get('amount_available')
            invoice_currency            = vals.get('invoice_currency')
            amount_available_conversion = float(vals.get('amount_available_conversion')) if vals.get('amount_available_conversion',False) else 0.00
            amount_invoice_in_company   = float(vals.get('amount_invoice_in_company')) if vals.get('amount_invoice_in_company',False) else 0.00
            amount_apply_conversion     = float(vals.get('amount_apply_conversion')) if vals.get('amount_apply_conversion',False) else 0.00

            if amount_apply_conversion > rec.amount_available_conversion:
                raise Warning(_('El monto a aplicar (%s) no puede ser mayor al monto disponible (%s)') % (rec.amount_apply_conversion, rec.amount_available_conversion))
            if amount_apply_conversion > rec.amount_invoice_in_company :
                raise Warning(_('El monto a aplicar (%s) no puede ser mayor al monto de la factura (%s)') % (rec.amount_apply_conversion, rec.amount_invoice_in_company))
            return True

    @api.depends('partner_id', 'journal_id', 'partner_id', 'date_advance')
    def action_register_advance(self):
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
                if not vals.get('invoice_currency', False):
                    vals.update({'invoice_currency':self.invoice_currency.id})
                if not vals.get('currency_id', False):
                    vals.update({'currency_id':self.currency_id.id})
                if not vals.get('amount_available_conversion', False):
                    vals.update({'amount_available_conversion':self.amount_available_conversion})
                if not vals.get('date_apply', False):
                    vals.update({'date_apply':self.date_apply})
                if self.validate_amount(vals):
                    self.amount_available = self.amount_available - vals.get('amount_apply')
                    vals.update({'amount_available': self.amount_available})
                    

                else:
                    self.state = 'paid'

        if vals.get('amount_advance'):
            if self.state == 'draft':
                if vals.get('invoice_currency') == self.env.company.currency_id:
                    self.amount_available = self.amount_advance - self.amount_apply
                else:
                    #self.amount_available = self.amount_advance - self.invoice_currency._convert(self.amount_apply, self.env.company.currency_id, self.env.company, self.date_advance)
                    self.amount_available = self.amount_advance - (self.amount_apply * self.manual_currency_exchange_rate)
                vals.update({'amount_available': self.amount_available,
                             'es_proveedor':self.partner_id.es_proveedor,
                             'es_cliente':self.partner_id.es_cliente})

        return super(AccountAdvancePayment, self).write(vals)

    @api.model
    def create(self, vals):
        if vals.get('es_proveedor') == True and self.partner_id.es_cliente == False:
            vals.update({'supplier': ((self.env['res.partner'].browse(vals['partner_id']).es_cliente) == False), 'es_cliente': False})
            self.es_cliente = False
        else:
            vals.update({'customer': self.env['res.partner'].browse(vals['partner_id']).es_cliente, 'es_proveedor': False})
            self.es_proveedor = False
        res = super(AccountAdvancePayment, self).create(vals)
        return res    

    @api.model
    def get_account_advance(self):
        '''obtiene la cuentas contables segun el proveedor o cliente, para el registro de los anticipos'''
        cuenta_acreedora = None
        cuenta_deudora = None
        partner_id = None
        sequence_code = None
        es_cliente = None
        es_proveedor = None

        if self.partner_id.es_cliente and self.state == 'draft' and self.type_advance == False:
            cuenta_deudora = self.bank_account_id.payment_debit_account_id.id
            cuenta_acreedora = self.partner_id.account_advance_payment_sales_id.id
            partner_id = self.partner_id.id
            sequence_code = 'register.receivable.advance.customer'
            self.es_cliente = True
            self.es_proveedor = False

        elif self.partner_id.es_proveedor and self.state == 'draft' and self.type_advance:
            cuenta_deudora = self.partner_id.account_advance_payment_purchase_id.id
            cuenta_acreedora = self.bank_account_id.payment_debit_account_id.id
            partner_id = self.partner_id.id
            sequence_code = 'register.payment.advance.supplier'
            self.es_proveedor = True
            self.es_cliente = False

        return cuenta_deudora,cuenta_acreedora,partner_id,sequence_code,es_proveedor,es_cliente

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

        if self.partner_id.es_cliente and self.state == 'available' and self.type_advance == False:
            cuenta_deudora = self.partner_id.account_advance_payment_sales_id.id
            cuenta_acreedora = self.bank_account_id.payment_debit_account_id.id
            partner_id = self.partner_id.id

        elif self.partner_id.es_proveedor and self.state == 'available' and self.type_advance:
            cuenta_deudora = self.bank_account_id.payment_debit_account_id.id
            cuenta_acreedora = self.partner_id.account_advance_payment_purchase_id.id
            partner_id = self.partner_id.id

        return cuenta_deudora,cuenta_acreedora,partner_id

    def get_move_register(self):
        '''se crea el asiento contable para el registro'''
        for rec in self:
            name = None
            manual_rate = rec.manual_currency_exchange_rate
            cuenta_deudora, cuenta_acreedora,partner_id,sequence_code,es_proveedor,es_cliente = rec.get_account_advance()
            #busca la secuencia del diario y se lo asigno a name
            if rec.partner_id.es_cliente and not cuenta_acreedora and rec.type_advance == False:
                    raise exceptions.Warning(_('El cliente no tiene configurado la cuenta contable de anticipo'))
            elif rec.partner_id.es_proveedor and not cuenta_deudora and rec.type_advance:
                    raise exceptions.Warning(_('El proveedor no tiene configurado la cuenta contable de anticipo'))
            else:
                name = self.env['ir.sequence'].with_context(ir_sequence_date=self.date_contable).next_by_code(sequence_code)
                if rec.currency_id != rec.env.company.currency_id:
                    manual_rate = 1 / rec.manual_currency_exchange_rate
                else:
                    manual_rate = rec.manual_currency_exchange_rate
                vals = {
                    # 'name': name,
                    'date': rec.date_contable,
                    'journal_id': rec.journal_id.id,
                    'line_ids': False,
                    'state': 'draft',
                    'partner_id': rec.partner_id.id,
                    'manual_currency_exchange_rate': manual_rate,
                    'apply_manual_currency_exchange': True,
                }
                move_obj = self.env['account.move']
                move_id = move_obj.create(vals)
                #Si el pago es en moneda extranjera $
                if rec.currency_id.id != self.env.company.currency_id.id:
                    # modificar
                    #if not currency_rate:
                    #    raise exceptions.Warning(_('Asegurese de tener la multimoneda configurada y registrar la tasa de la fecha del anticipo'))
                    #money = rec.currency_id._convert(rec.amount_advance, self.env.company.currency_id, self.env.company, rec.date_advance)
                    money = rec.amount_advance * rec.manual_currency_exchange_rate
                    move_advance_ = {
                        'account_id': cuenta_acreedora,
                        'company_id': self.env.company.id,
                        'currency_id': rec.currency_id.id,
                        'date_maturity': False,
                        'ref': rec.ref,
                        'date': rec.date_contable,
                        'partner_id': rec.partner_id.id,
                        'move_id': move_id.id,
                        'name': name,
                        'journal_id': rec.journal_id.id,
                        'credit':  money,
                        'debit': 0.0,
                        'amount_currency': -rec.amount_advance,
                    }
                    asiento = move_advance_
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
                                   'amount_available': rec.amount_advance, 'name': name, 'es_proveedor': True}
                        else:
                            res = {'state': 'available', 'move_id': move_id.id, 'customer': True,
                                   'amount_available': rec.amount_advance, 'name': name, 'es_cliente': True}
                        return super(AccountAdvancePayment, self).write(res)
                else:
                    rec.invoice_currency = self.env.company.currency_id
                    move_advance_ = {
                        'account_id': cuenta_acreedora,
                        'company_id': self.env.company.id,
                        'date_maturity': False,
                        'ref': rec.ref,
                        'date': rec.date_contable,
                        'partner_id': rec.partner_id.id,
                        'move_id': move_id.id,
                        'name': name,
                        'journal_id': rec.journal_id.id,
                        'credit': rec.amount_advance,
                        'debit': 0.0,
                    }
                    asiento = move_advance_
                    move_line_obj = self.env['account.move.line']
                    move_line_id1 = move_line_obj.with_context(check_move_validity=False).create(asiento)

                    asiento['account_id'] = cuenta_deudora
                    asiento['credit'] = 0.0
                    asiento['debit'] = rec.amount_advance

                    move_line_id2 = move_line_obj.create(asiento)
                    for lin in move_id.line_ids:
                        lin.partner_id = rec.partner_id.id
                    move_id.action_post()

                    if move_line_id1 and move_line_id2:
                        if rec.partner_id.es_proveedor and rec.type_advance:
                            res = {'state': 'available', 'move_id': move_id.id, 'supplier':True, 'amount_available':rec.amount_advance,'name':name, 'es_proveedor':True}
                        else:
                            res = {'state': 'available', 'move_id': move_id.id, 'customer':True, 'amount_available':rec.amount_advance,'name':name, 'es_cliente':True}
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
            'partner_id': self.partner_id.id,
        }
        move_apply_obj = self.env['account.move']
        move_apply_id = move_apply_obj.create(vals)
        if  self.currency_id != self.env.company.currency_id:
            move_advance_ = {
                'account_id': cuenta_acreedora,
                'company_id': self.env.company.id,
                'currency_id': self.currency_id.id,
                'date_maturity': False,
                'ref': self.ref,
                'date': self.date_apply,
                'partner_id': self.partner_id.id,
                'move_id': move_apply_id.id,
                'name': self.name,
                'journal_id': self.journal_id.id,
                'credit': self.amount_apply * self.manual_currency_exchange_rate,
                'debit': 0.0,
                'amount_currency': -(self.amount_apply),
            }

            asiento_apply = move_advance_
            move_line_obj = self.env['account.move.line']
            move_line_id1 = move_line_obj.with_context(check_move_validity=False).create(asiento_apply)

            asiento_apply['amount_currency'] = self.amount_apply
            asiento_apply['account_id'] = cuenta_deudora
            asiento_apply['credit'] = 0.0
            asiento_apply['debit'] = self.amount_apply* self.manual_currency_exchange_rate

        else:
            move_advance_ = {
                'account_id': cuenta_acreedora,
                'company_id': self.env.company.id,
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

            asiento_apply = move_advance_
            move_line_obj = self.env['account.move.line']
            move_line_id1 = move_line_obj.with_context(check_move_validity=False).create(asiento_apply)

            asiento_apply['account_id'] = cuenta_deudora
            asiento_apply['credit'] = 0.0
            asiento_apply['debit'] = self.amount_apply

        move_line_id2 = move_line_obj.create(asiento_apply)
        move_apply_id.action_post()
        res = {'state': 'paid', 'move_apply_id': move_apply_id.id, 'amount_available': self.amount_available}
        self.write(res)
        if self.currency_id != self.env.company.currency_id:
            #self.amount_available_conversion = self.currency_id._convert(self.amount_available, self.env.company.currency_id, self.env.company, self.date_apply)
            self.amount_available_conversion = self.amount_available * self.manual_currency_exchange_rate

        else:
            self.amount_available_conversion = self.amount_available
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
                'partner_id': self.partner_id.id,
            }
            move_obj = self.env['account.move']
            move_refund_id = move_obj.create(vals)
            if self.currency_id == self.env.company.currency_id:
                move_advance_ = {
                    'account_id': cuenta_acreedora,
                    'company_id': self.env.company.id,
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

                asiento = move_advance_
                move_line_obj = self.env['account.move.line']
                move_line_id1 = move_line_obj.with_context(check_move_validity=False).create(asiento)

                asiento['account_id'] = cuenta_deudora
                asiento['credit'] = 0.0
                asiento['debit'] = self.amount_available
            else:
                move_advance_ = {
                    'account_id': cuenta_acreedora,
                    'company_id': self.env.company.id,
                    'currency_id': self.currency_id.id,
                    'date_maturity': False,
                    'ref': self.ref,
                    'date': self.date_apply,
                    'partner_id': self.partner_id.id,
                    'move_id': move_refund_id.id,
                    'name': self.name,
                    'journal_id': self.journal_id.id,
                    'credit': self.amount_available * self.manual_currency_exchange_rate,
                    'debit': 0.0,
                    'amount_currency': -(self.amount_available),
                }

                asiento = move_advance_
                move_line_obj = self.env['account.move.line']
                move_line_id1 = move_line_obj.with_context(check_move_validity=False).create(asiento)

                asiento['amount_currency'] = self.amount_available
                asiento['account_id'] = cuenta_deudora
                asiento['credit'] = 0.0
                asiento['debit'] = self.amount_available * self.manual_currency_exchange_rate

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



    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        """ This override is done in order for the grouped list view to display the total value of
        the quants inside a location. This doesn't work out of the box because `value` is a computed
        field.
        """
        if 'amount_advance_bs' not in fields or 'amount_advance_usd' not in fields:
            return super(AccountAdvancePayment, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        res = super(AccountAdvancePayment, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        for group in res:
            if group.get('__domain'):
                quants = self.search(group['__domain'])
                group['amount_advance_bs'] = sum(quant.amount_advance_bs for quant in quants)
                group['amount_advance_usd'] = sum(quant.amount_advance_usd for quant in quants)
        return res
        
class account_move(models.Model):
    _inherit = 'account.move'


    def assert_balanced(self):
        if not self.ids:
            return True
        mlo = self.env['account.move.line'].search([('move_id', '=',self.ids[0])])
        if not mlo.reconcile:
            super(account_move, self).assert_balanced(fields)
        return True