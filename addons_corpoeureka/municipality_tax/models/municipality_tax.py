# -*- coding: utf-8 -*-
#programmer
#eliomeza1@gmail.com


import logging
from datetime import datetime, date
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression

_logger = logging.getLogger("__name__")


class PeriodMonth(models.Model):
    _name = 'period.month'
    _rec_name = 'months_number'

    name = fields.Char(string='Months')
    months_number = fields.Char(string='Number')


class PeriodYear(models.Model):
    _name = 'period.year'
    _description="Period year"

    name = fields.Char(string='year')

class MuniWhConceptPartner(models.Model):
    _name = 'muni.wh.concept.partner'
    _description="Concep Municipal Partner"

    muni_concept = fields.Many2one('muni.wh.concept', string="Concepto")
    partner_id   = fields.Many2one('res.partner', string="Proveedor y/o Cliente ")
    company_id = fields.Many2one('res.company', string="Compañia", default=lambda self: self.env.company.id)

    @api.depends('muni_concept')
    def name_get(self):
        result = []
        for muni in self:
            name = muni.muni_concept.code + ' ' + muni.muni_concept.name + ' ' + str(muni.muni_concept.aliquot)
            result.append((muni.id, name))
        return result

class MuniWhConcept(models.Model):
    _name = 'muni.wh.concept'
    _description="Concep Municipal"
    

    name = fields.Char(string="Description", required=True)
    code = fields.Char(string='Activity code', required=True)
    aliquot = fields.Float(string='Aliquot', required=True)
    month_ucim = fields.Char(string='Tributable Mensual en Petros')
    year_ucim = fields.Char(string='UCIM per year')
    company_id = fields.Many2one('res.company', string="Compañia", default=lambda self: self.env.company.id)
  
    
    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code', '=ilike', name.split(' ')[0] + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)

    def name_get(self):
        result = []
        for muni in self:
            name = muni.code + ' ' + muni.name + ' ' + str(muni.aliquot)
            result.append((muni.id, name))
        return result

class MunicipalityTaxLine(models.Model):
    _name = 'municipality.tax.line'
    _description="Tax Municipal line"
    #_inherit= ['mail.thread', 'mail.activity.mixin']
    municipality_tax_id = fields.Many2one('municipality.tax', string='Municipality')
    tipo_factura = fields.Selection(related="municipality_tax_id.move_type",string="Tipo de Factura")
    currency_id = fields.Many2one('res.currency', string="Moneda Principal", default=lambda self: self.env.company.currency_id)
    partner_id = fields.Many2one('res.partner', string='Partner', ondelete='restrict',realated="municipality_tax_id.partner_id")
    invoice_id = fields.Many2one('account.move', related="municipality_tax_id.invoice_id", string='Invoice')
    concept_partner = fields.Many2one('muni.wh.concept.partner',string='Concepto de Retención (Proveedores)',domain="[('partner_id', '=', partner_id)]")
    concept_partner2 = fields.Many2one('muni.wh.concept',string='Concepto de Retención (Clientes)',)
    concept_id = fields.Many2one('muni.wh.concept', string="Retention concept",options='{"no_open": True, "no_create_edit": True, "no_quick_create": True, "no_create": True}', Copy=False)
    code = fields.Char(string='Activity code',related="concept_id.code" ,store=True)
    aliquot = fields.Float(string='Aliquot',compute="_aliq_mun",track_visibility='always', store="True")
    base_tax = fields.Monetary(string='Base Tax')
    wh_amount = fields.Float(compute="_compute_wh_amount", string='Withholding Amount', store=True)
    move_type = fields.Selection(selection=[('purchase', 'Purchase'), ('service', 'Service'), ('dont_apply','Does not apply')],compute="_aliq_mun",string='Type of transaction')
    move_id = fields.Many2one(string='Account entry')
    invoice_date = fields.Date(string="Invoice Date")
    vendor_invoice_number = fields.Char(string="Invoice Number")
    invoice_ctrl_number = fields.Char(string="Invoice Control Number")
    alicuota_normal = fields.Char(string="Alicuota", store=True)

    #partner_id = fields.Many2one('res.partner', string="Contacto")
    #type_partner= fields.Selection(related="partner_id.type_partner",string="Tipo de Proveedor")
    porcentaje_alic= fields.Float(string='Porc.', store=True)
    def float_format(self,valor):
        #valor=self.base_tax
        if valor:
            result = '{:,.2f}'.format(valor)
            result = result.replace(',','*')
            result = result.replace('.',',')
            result = result.replace('*','.')
        else:
            result="0,00"
        return result

    @api.onchange('code', 'concept_partner','concept_partner2')
    def _aliq_mun(self):
        for  x in self:
            if x.code == x.concept_id.code:
                if x.porcentaje_alic == 50:
                    x.aliquot = (x.concept_id.aliquot * 50) / 100
                else: 
                    x.aliquot = x.concept_id.aliquot
            if x.municipality_tax_id.move_type == 'out_invoice' or x.municipality_tax_id.move_type == 'out_refund':
                x.move_type = 'dont_apply'
                if x.concept_partner2:
                    x.concept_id = x.concept_partner2
                else:
                    x.concept_id = False
            if x.municipality_tax_id.move_type == 'in_invoice' or x.municipality_tax_id.move_type == 'in_refund':
                x.move_type = 'purchase'
                x.partner_id =x.municipality_tax_id.partner_id 
                if x.concept_partner:
                    x.concept_id = x.concept_partner.muni_concept.id
                else:
                    x.concept_id = False


    @api.depends('base_tax', 'aliquot')
    def _compute_wh_amount(self):
        withheld_amount=0
        amount=0
        porcentaje_del_base_tax = 0
        for item in self:
            if item.municipality_tax_id.partner_id.partner_type == 'D': 
                item.porcentaje_alic = 50
                porcentaje_del_base_tax = (item.base_tax * 50)/100 
            if item.municipality_tax_id.partner_id.partner_type == 'T': 
                item.porcentaje_alic = 100
                porcentaje_del_base_tax = item.base_tax 

            retention = ((porcentaje_del_base_tax * item.aliquot) / 100)
            #retention = ((item.base_tax * item.aliquot) / 100)

            item.wh_amount = retention
            muni_tax = self.env['municipality.tax'].browse(item.municipality_tax_id.id)
            withheld_amount = item.base_tax # correccion  se transformo en acumulador
            amount = item.wh_amount # correccion  se transformo en acumulador
            if muni_tax:
                muni_tax.write({'withheld_amount': withheld_amount, 'amount': amount})


class MUnicipalityTax(models.Model):
    _name = 'municipality.tax'
    _description="Tax Municipal"
    _inherit= ['mail.thread', 'mail.activity.mixin']


    def float_format2(self,valor):
        #valor=self.base_tax
        if valor:
            result = '{:,.2f}'.format(valor)
            result = result.replace(',','*')
            result = result.replace('.',',')
            result = result.replace('*','.')
        else:
            result="0,00"
        return result

    name = fields.Char(string='Voucher number', default='New')
    state = fields.Selection(selection=[
            ('draft', 'Draft'),
            ('posted', 'Posted'),
            ('declared', 'Declarado'),
            ('done', 'Pagado'),
            ('cancel', 'Cancelled')
        ], string='Status', readonly=True, copy=False, tracking=True,
        default='draft')
    transaction_date = fields.Date(string='Transacción Date', default=datetime.now(),track_visibility='always')
    #period fields
    date_start = fields.Many2one('period.month', string='Date start')
    date_end = fields.Many2one('period.year', string='Date end')
    rif = fields.Char(related="partner_id.rif",string='RIF', readonly=True)
    #rif = fields.Char(related='invoice_id.rif',string='RIF')
    # address
    address = fields.Char(compute="_get_address", string='Address')
    # partner data
    
    invoice_id = fields.Many2one('account.move', string='Invoice', required=True, domain="[('move_type','=',move_type),('wh_muni_id','=',False),('state','=','posted')]")
    partner_id = fields.Many2one('res.partner', related="invoice_id.partner_id" ,string='Partner',store=True)
    act_code_ids = fields.One2many('municipality.tax.line', 'municipality_tax_id', string='Activities code',track_visibility='always')
    # campos de ubicacion politico territorial
    city = fields.Char(string='City')
    state_id = fields.Many2one('res.country.state', string='State', tracking=True)
    municipality_id = fields.Many2one('res.country.state.municipality', string='Municipality')

    asiento_post = fields.Many2one('account.move', string='Asiento Contable de la Retención',track_visibility='always')

    amount = fields.Float(string='Amount',track_visibility='always')
    withheld_amount = fields.Float(string='Withheld Amount',track_visibility='always')

    #aliquot = fields.Float(related="concept_id.aliquot",string='Aliquot')
    move_type = fields.Selection(selection=[
        ('out_invoice', 'Factura de Clientes'),
        ('in_invoice','Factura de Proveedor'),
        ('in_refund','Nota de credito de Proveedor'),
        ('out_refund','Nota de credito de Clientes'),
        ('in_receipt','Nota Debito cliente'),
        ('out_receipt','Nota Debito proveedor'),
        ], string="Type invoice", store=True)
    
    # We need this field for the reports
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company.id)
    move_id = fields.Many2one('account.move', string='Id del movimiento')
    manual_currency_exchange_rate = fields.Float(string='Tasa de la Retención', digits=(20,10),store=True,readonly=True)

    @api.onchange('partner_id')
    def _rif(self):
        if self.partner_id:
            self.rif = self.partner_id.rif
            #self.rif = str(self.partner_id.doc_type)+"-"+str(self.partner_id.vat)


    @api.depends('partner_id')
    def _get_address(self):
        location = ''
        streets = ''
        if self.partner_id:
            location = self._get_state_and_city()
            streets = self._get_streets()
            self.address = streets + " " + location
        else:
            self.address = ''


    def _get_state_and_city(self):
        state = ''
        city = ''
        if self.partner_id.state_id:
            state = "Edo." + " " + str(self.partner_id.state_id.name or '')
        if self.partner_id.city:
            city = str(self.partner_id.city or '')
        result = city + " " + state
        return  result 


    def _get_streets(self):
        street2 = ''
        av = ''
        if self.partner_id.street:
            av = str(self.partner_id.street or '')
        if self.partner_id.street2:
            street2 = str(self.partner_id.street2 or '')
        result = av + " " + street2
        return result


    def get_company_address(self):
        location = ''
        streets = ''
        if self.company_id:
            streets = self._get_company_street()
            location = self._get_company_state_city()
        return  (streets + " " + location)


    def _get_company_street(self):
        street2 = ''
        av = ''
        if self.company_id.street:
            av = str(self.company_id.street or '')
        if self.company_id.street2:
            street2 = str(self.company_id.street2 or '')
        result = av + " " + street2
        return result


    def _get_company_state_city(self):
        state = ''
        city = ''
        if self.company_id.state_id:
            state = "Edo." + " " + str(self.company_id.state_id.name or '')
        if self.company_id.city:
            city = str(self.company_id.city or '')
        result = city + " " + state
        return  result


    def action_post(self):
        """Confirmed the municipal retention voucher."""
        if self.asiento_post:
            self.actualizar_asiento()
            self.asiento_post.post()
            self.state = 'posted'
            self.create_name()

        if not self.asiento_post:
            if not self.transaction_date:
                raise ValidationError("Debe establecer una fecha de Transacción")
            if not self.invoice_id.wh_muni_id:
                self.invoice_id.wh_muni_id = self.id
            if self.invoice_id.wh_muni_id.state == 'posted': 
                raise ValidationError("La factura selecionada ya tiene una Retencion Municipal Aplicada")
            self.state = 'posted'
            self.create_name()
            nombre_ret_municipal = self.get_name()
            id_move=self.registro_movimiento_retencion(nombre_ret_municipal)
            idv_move=id_move.id
            valor=self.registro_movimiento_linea_retencion(idv_move,nombre_ret_municipal)
            moves= self.env['account.move'].search([('id','=',idv_move)])
            moves.post()
            self.asiento_post = idv_move
        

    def action_draft(self):
        if self.asiento_post:
            if self.asiento_post.state == 'posted':
                self.asiento_post.button_draft()
        self.state = 'draft'

    def action_cancel(self):
        if self.asiento_post:
            if self.asiento_post.state == 'posted':
                self.asiento_post.button_draft()
            if self.asiento_post.state == 'draft':
                self.asiento_post.button_cancel()
        self.state = 'cancel'


        #self.retecion_vinculada.funcionquequieres()

    def create_name(self):
        if self.name == 'New':
            for rec in self:
                if rec.invoice_id.move_type == 'in_invoice' or rec.invoice_id.move_type == 'in_refund':
                    rec['name'] = self.env['ir.sequence'].next_by_code('purchase.muni.wh.voucher.number') or '/'
                else:
                    rec['name'] = '/'



    def registro_movimiento_retencion(self,consecutivo_asiento):
        name = consecutivo_asiento
        signed_amount_total=0
        #raise UserError(_('self.move_id.name = %s')%self.invoice_id.name)
        if self.move_type=="in_invoice":
            signed_amount_total=self.amount
        if self.move_type=="out_invoice":
            signed_amount_total=(-1*self.amount)

        if self.move_type=="out_invoice" or self.move_type=="out_refund" or self.move_type=="out_receipt":
            id_journal=self.partner_id.purchase_jrl_id.id
        if self.move_type=="in_invoice" or self.move_type=="in_refund" or self.move_type=="in_receipt":
            id_journal=self.company_id.partner_id.purchase_jrl_id.id

        value = {
            'name': name,
            'date': self.transaction_date,#listo
            #'amount_total':self.vat_retentioned,# LISTO
            'partner_id': self.partner_id.id, #LISTO
            'journal_id':id_journal,
            'ref': "Retencion IAE, Factura %s" % (self.invoice_id.name),
            #'amount_total':self.vat_retentioned,# LISTO
            #'amount_total_signed':signed_amount_total,# LISTO
            'move_type': "entry",# estte campo es el que te deja cambiar y almacenar valores
            'wh_muni_id': self.id,
            'manual_currency_exchange_rate':self.manual_currency_exchange_rate,
            'apply_manual_currency_exchange':True,
        }
        move_obj = self.env['account.move']
        move_id = move_obj.create(value)    
        return move_id


    def registro_movimiento_linea_retencion(self,id_movv,consecutivo_asiento):
        name = consecutivo_asiento
        valores = self.amount #VALIDAR CONDICION
        cero = 0.0
        value = []

        if self.move_type=="out_invoice" or self.move_type=="out_refund" or self.move_type=="out_receipt":
            cuenta_ret_cliente=self.partner_id.account_ret_muni_receivable_id.id# cuenta retencion cliente
            cuenta_ret_proveedor=self.partner_id.account_ret_muni_payable_id.id#cuenta retencion proveedores
            cuenta_clien_cobrar=self.partner_id.property_account_receivable_id.id
            cuenta_prove_pagar = self.partner_id.property_account_payable_id.id

        if self.move_type=="in_invoice" or self.move_type=="in_refund" or self.move_type=="in_receipt":
            cuenta_ret_cliente=self.company_id.partner_id.account_ret_muni_receivable_id.id# cuenta retencion cliente
            cuenta_ret_proveedor=self.company_id.partner_id.account_ret_muni_payable_id.id#cuenta retencion proveedores
            cuenta_clien_cobrar=self.partner_id.property_account_receivable_id.id
            cuenta_prove_pagar = self.partner_id.property_account_payable_id.id

        tipo_empresa=self.move_type
        #raise UserError(_('darrell = %s')%tipo_empresa)
        if tipo_empresa=="in_invoice" or tipo_empresa=="in_receipt":#aqui si la empresa es un proveedor
            cuenta_haber=cuenta_ret_proveedor
            cuenta_debe=cuenta_prove_pagar
            #raise UserError(_(' pantalla 1'))
            #raise UserError(_('cuentas = %s')%cuenta_debe)

        if tipo_empresa=="in_refund":
            cuenta_haber=cuenta_prove_pagar
            cuenta_debe=cuenta_ret_proveedor
            #raise UserError(_(' pantalla 2'))

        if tipo_empresa=="out_invoice" or tipo_empresa=="out_receipt":# aqui si la empresa es cliente
            cuenta_haber=cuenta_clien_cobrar
            cuenta_debe=cuenta_ret_cliente
            #raise UserError(_(' pantalla 3'))

        if tipo_empresa=="out_refund":
            cuenta_haber=cuenta_ret_cliente
            cuenta_debe=cuenta_clien_cobrar
            #raise UserError(_(' pantalla 4'))
        balances=cero-valores
        #raise UserError(_('cuenta = %s')%cuenta_ret_cliente)
        value.append({
             'name': name,
             'ref' : "Retencion IAE, Factura %s" % (self.invoice_id.name),
             'move_id': int(id_movv),
             'date': self.transaction_date,
             'partner_id': self.partner_id.id,
             'account_id': cuenta_haber,
             #'amount_currency': 0.0,
             #'date_maturity': False,
             'credit': valores,
             'debit': 0.0, # aqi va cero   EL DEBITO CUNDO TIENE VALOR, ES QUE EN ACCOUNT_MOVE TOMA UN VALOR
             'balance':-valores, # signo negativo
             'price_unit':balances,
             'price_subtotal':balances,
             'price_total':balances,

        })
        balances=valores-cero
        value.append({
             'name': name,
             'ref' : "Retencion IAE, Factura %s" % (self.invoice_id.name),
             'move_id': int(id_movv),
             'date': self.transaction_date,
             'partner_id': self.partner_id.id,
             'account_id': cuenta_debe,
             #'amount_currency': 0.0,
             #'date_maturity': False,
             'credit': 0.0,
             'debit': valores, # aqi va cero   EL DEBITO CUANDO TIENE VALOR, ES QUE EN ACCOUNT_MOVE TOMA UN VALOR
             'balance':valores, # signo negativo
             'price_unit':balances,
             'price_subtotal':balances,
             'price_total':balances,

        })
        move_line_obj = self.env['account.move.line'].sudo()
        move_line_id2 = move_line_obj.create(value)



    def get_name(self):
        '''metodo que crea el Nombre del asiento contable si la secuencia no esta creada, crea una con el
        nombre: 'l10n_ve_cuenta_retencion_iva'''

        self.ensure_one()
        SEQUENCE_CODE = 'l10n_ve_cuenta_retencion_municipal'
        company_id = self.env.company.id
        IrSequence = self.env['ir.sequence'].with_context(force_company=1)
        name = IrSequence.next_by_code(SEQUENCE_CODE)

        # si aún no existe una secuencia para esta empresa, cree una
        if not name:
            IrSequence.sudo().create({
                'prefix': 'RET_MUN/',
                'name': 'Localización Venezolana Retenciones Municipales %s' % 1,
                'code': SEQUENCE_CODE,
                'implementation': 'no_gap',
                'padding': 8,
                'number_increment': 1,
                'company_id': self.env.company.id,
            })
            name = IrSequence.next_by_code(SEQUENCE_CODE)
        return name

    def actualizar_asiento(self):
        #raise UserError(_('mama = %s')%self)
        account_move = self.env['account.move'].search([('id','=',self.asiento_post.id)])
        account_move_line = self.env['account.move.line'].search([('move_id','=',self.asiento_post.id)])
        #for borrar in account_move_line:
        #    borrar.unlink()
        
        for det in account_move:
            self.env['account.move'].browse(det.id).write({
                'date': self.transaction_date,
                'partner_id': self.partner_id.id, 
                'ref': "Retencion IAE, Factura %s" % (self.invoice_id.name),
                'line_ids': [(5, 0, 0)],
                })
        self.registro_movimiento_linea_retencion(self.asiento_post.id,False)
    # Evita eliminar una retencion confirmada     
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError('!No se puede eliminar una retencion municipal confirmada y/o declarada!') 
        return super(MUnicipalityTax, self).unlink()

    def action_withhold_iae_send(self):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('municipality_tax', 'email_template_muni')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict()
        ctx.update({
            'default_model': 'municipality.tax',
            'active_model': 'municipality.tax',
            'active_id': self.ids[0],
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            #'custom_layout': "municipality_tax.mail_template_data_notification_email_muni",
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

