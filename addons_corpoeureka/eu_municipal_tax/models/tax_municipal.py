import logging
from datetime import datetime, date
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, Warning

_logger = logging.getLogger("__name__")



class MunicipalTax(models.Model):
    _name = 'tax.municipal'
    _description ="Impuesto Actividad Economica"
    _order = 'date desc'
    _inherit= ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(string="Nuevo Calculo de Declaración mensual de Ingresos", readonly=True, default='/',track_visibility='always',) 
    company_id = fields.Many2one('res.company',string="Compañía", required=True, default=lambda self: self.env.company,track_visibility='always',invisible=True)
    state = fields.Selection([
        ('draft', 'Borrador'),#no declarado 
        ('confirmed','Confirmado'),#declarado
        ('done', 'Pagado'),#pagado
        ('cancel', 'Cancel'),#cancelado
        ], string='Estatus', readonly=True, copy=False, index=True, track_visibility='always', default='draft')
    date = fields.Date(string="Fecha de Creación",track_visibility='always', default=fields.Date.context_today)
    #Fechas
    date_in  = fields.Date(string="Fecha inicial",track_visibility='always',required=True)
    date_end  = fields.Date(string="Fecha final ",track_visibility='always',required=True) 

    #Diario para las Facturas (tipo Ventas o Compras )
    journal_id = fields.Many2one('account.journal',string="Diario",required=True,store=True,domain=[('type','in',('sale','purchase'))])
    # Líneas de las facturas
    invoice_line = fields.One2many(comodel_name='tax.municipal.line',inverse_name='invoice_id_line',string='Lineas de la Facturas')
    #Porcentaje de impuesto sobre actividades economicas
    aliquot_municipal = fields.Float(string=" % Alicuota ", store=True,size=5, required=True,default="",help="Alicuota correspondiente a la actividad economica del compañía")
    # Total de Productos en las SU
    total_iae = fields.Float(string="Total Declaración  de Ingresos a Pagar",compute="_compute_total_aliquot",store=True,help="Total a pagar por declaración mensual de ingresos")
    #
    total_tax_ret = fields.Float(string="Monto Ret. por el Cliente",compute="_compute_total_aliquot",store=True,readonly=True,help="Monto retenido por el cliente cuando es agente de retención")

    invoice_ids = fields.Many2one('account.move',string="Factura de Pago",readonly=True)

    payment_count = fields.Integer(string="Factura",compute="_compute_payment_count")
    
    @api.depends('invoice_ids')
    def _compute_payment_count(self):
        for rec in self:
            rec.payment_count = 1 if rec.invoice_ids else 0

    def show_payments(self):
        self.ensure_one()
        res = self.env.ref('account.action_move_in_invoice_type')
        res = res.read()[0]
        res['context'] = {'create':False}
        res['domain'] = str([('id', '=', self.invoice_ids.id)])
        return res
    # Traer Facturas Publicadas en el diario seleccionado
    @api.onchange('journal_id')
    def onchange_invoice(self):
        line_dict = {}
        for rec in self:
            partner_id = self.env.company.partner_id.id
            concept_id = self.env['muni.wh.concept.partner'].search([('partner_id','=',partner_id)],limit=1)
            rec.aliquot_municipal = concept_id.muni_concept.aliquot
            if rec.journal_id:
                if rec.invoice_line:
                    for lines in rec.invoice_line:#para garantizar que no los coloque encimas 
                        lines.invoice_id.status_account = 'not_declared'
                        values = [(5, 0, 0)]
                        rec.update({'invoice_line': values})
                orders = [line for line in sorted(rec.env['account.move'].search([
                    ('journal_id', '=', rec.journal_id.id),
                    ('state', '=', 'posted'),
                    ('invoice_date', '>=', rec.date_in),
                    ('invoice_date', '<=', rec.date_end),
                    ('move_type', '=', 'out_invoice'),
                    ('status_account', '=', 'not_declared'),
                    ]),
                    key=lambda x: x.id)]
                for order in orders:
                    line_dict = {
                        'invoice_id':           order.id,
                        'date_invoice':         order.invoice_date,
                        'partner_id':           order.partner_id.id,
                        'rif':                  order.partner_id.rif,
                        #'name':                    order.name,
                        'amount_untaxed':       order.amount_untaxed,
                        'amount_tax':           order.amount_tax,
                        'amount_total':         order.amount_total,
                        'aliquot_municipal':    rec.aliquot_municipal,
                        'total_amount_tax_ret': order.wh_muni_id.amount,
                        'monto_muni':           (order.amount_untaxed*rec.aliquot_municipal)/100,
                    }
                    #order.status_account = 'to_declared'
                    lines = [(0,0,line_dict)]
                    rec.write({'invoice_line':lines})
                if not line_dict:
                    raise Warning(_("¡No hay facturas en este período!"))

    # Función Computada para obtener el Total
    @api.depends('invoice_line')
    def _compute_total_aliquot(self):
        for rec in self:
            rec.total_iae = 0.0
            rec.total_tax_ret = 0.0
            if rec.invoice_line:
                for lines in rec.invoice_line:
                    rec.total_iae += (lines.monto_muni-lines.total_amount_tax_ret)
                    rec.total_tax_ret += lines.total_amount_tax_ret

    # Botón Confirmar IAE y se le asigna su sequence
    def button_confirm(self):
        for rec in self:
            if self.name == '/': #para que no salte la secuencia
                self.name = self.env['ir.sequence'].next_by_code('tax.municipal.seq')
            if not rec.invoice_line:
                raise Warning(_('Por favor, añade una factura'))
            for invoice in rec.invoice_line.invoice_id:
                if invoice.status_account != 'not_declared':
                    raise Warning(_('Alguna Factura ya fue añadida en otra declaracion de I.A.E, %s') % (invoice.name))
                invoice.status_account = 'declared'
            rec.state = 'confirmed'  

    # Pasar a Borrador
    def reset_draft(self):
        for rec in self:
            for invoice in rec.invoice_line.invoice_id:
                invoice.status_account = 'not_declared'
            rec.state = 'draft'

    # Botón para Cancelar
    def button_cancel(self):
        for rec in self:
            for invoice in rec.invoice_line.invoice_id:
                invoice.status_account = 'not_declared'
            if rec.invoice_line:
                for lines in rec.invoice_line:
                    values = [(5, 0, 0)]
                    rec.update({'invoice_line': values})
            rec.state = 'cancel'


    def button_done(self):
        return self.env["account.iae.pay"]\
                    .with_context(active_ids=self.ids, active_model="tax.municipal", active_id=self.id)\
                    .action_pays_iae()

