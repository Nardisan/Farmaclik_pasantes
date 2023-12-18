import logging
from odoo.tools import email_split
from datetime import datetime, date
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, Warning
import collections
import base64

_logger = logging.getLogger("__name__")



class MunicipalTaxDeclaration(models.Model):
    _name = 'tax.municipal.declaration'
    _description ="Declaracion de Retencion Municipal"
    _order = 'date desc'
    _inherit= ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(string="Declaración de Retencion Municipal", readonly=True, default='/',track_visibility='always',) 
    company_id = fields.Many2one('res.company',string="Compañía", required=True, default=lambda self: self.env.company,track_visibility='always',invisible=True)
    state = fields.Selection([
        ('draft', 'Borrador'),#no declarado 
        ('declared','Declarado'),#declarado
        ('done', 'Pagado'),#pagado
        ('cancel', 'Cancelado'),#cancelado
        ], string='Estatus', readonly=True, copy=False, index=True, track_visibility='always', default='draft')
    date = fields.Date(string="Fecha de Declaración",track_visibility='always', default=fields.Date.context_today,required=True)
    #Fechas
    date_in  = fields.Date(string="Fecha inicial",track_visibility='always',required=True)
    date_end  = fields.Date(string="Fecha final ",track_visibility='always',required=True,)
    description_decl_reten = fields.Char(string='Descripción',track_visibility='always',help="Descripción breve de la declaración de retenciones IAE")  
    report_historical = fields.Char(string="Historico", track_visibility="always", invisible=True)
    #Diario para las Facturas (tipo Ventas o Compras )
    #journal_id = fields.Many2one('account.journal',string="Diario",required=True,store=True,domain=[('type','in',('sale','purchase'))])
 	# Líneas de la retencion
    tax_municipal_line = fields.One2many(comodel_name='tax.municipal.declaration.line',inverse_name='tax_municipal_id',string='Lineas de las Retenciones')
    
    # Total 
    total_retenido = fields.Float(string="Monto total retenido",compute="_compute_total_aliquot",store=True)
    


    # Traer Facturas Publicadas en el diario seleccionado
    @api.onchange('date_in','date_end')
    def onchange_retention(self):
        line_dict = {}
        for rec in self:
            if rec.date_in and rec.date_end:
                if rec.tax_municipal_line:
                    for lines in rec.tax_municipal_line:#para garantizar que no los coloque encima 
                        lines.state = 'posted'
                        values = [(5, 0, 0)]
                        rec.update({'tax_municipal_line': values})
                orders = [line for line in sorted(rec.env['municipality.tax.line'].search([
                    ('municipality_tax_id.state', '=', 'posted'),
                	('municipality_tax_id.transaction_date', '>=', rec.date_in),
                	('municipality_tax_id.transaction_date', '<=', rec.date_end),
                    ('municipality_tax_id.invoice_id.move_type', '=', 'in_invoice'),
                	]),
                    key=lambda x: x.id)]
                for order in orders:
                    line_dict = {
                        'municipal_tax_id':     order.municipality_tax_id,
                        'comprobante':          order.municipality_tax_id.name,
                        'partner_id':           order.municipality_tax_id.partner_id.id,
                        'rif': 		            order.municipality_tax_id.partner_id.rif,
                        'transaction_date':     order.municipality_tax_id.transaction_date,
                        'invoice_id':           order.invoice_id.id,
                        'base_imponible':   	order.base_tax,
                        'amount_total_invoice': order.invoice_id.amount_total,
                        'aliquot':   	        order.aliquot,
                        'amount_total_ret':     order.wh_amount
                    }
                    #order.status_account = 'to_declared'
                    lines = [(0,0,line_dict)]
                    rec.write({'tax_municipal_line':lines})
                if not line_dict:
                    raise Warning(_("¡No hay retenciones en el perdiodo que indicó!"))

    # Función Computada para obtener el Total
    @api.depends('tax_municipal_line')
    def _compute_total_aliquot(self):
        for rec in self:
            rec.total_retenido = 0.0
            if rec.tax_municipal_line:
                for lines in rec.tax_municipal_line:
                    rec.total_retenido += lines.amount_total_ret
                    
    # Botón Confirmar declaracion de retencion y se le asigna su sequence
    def button_confirm(self):
        for rec in self:
            if self.name == '/': #para que no salte la secuencia
                self.name = self.env['ir.sequence'].next_by_code('tax.muni.wh.retention.declared')
            if not rec.tax_municipal_line:
                raise Warning('Por favor, añade una retención')
            for retention in rec.tax_municipal_line.municipal_tax_id:
                if retention.state != 'posted':
                    raise Warning('Alguna retención ya fue añadida en otra declaración de I.A.E')
                retention.state = 'declared'
            rec.state = 'declared'

    # Pasar a Borrador
    def button_draft(self):
        for rec in self:
            for retention in rec.tax_municipal_line.municipal_tax_id:
                retention.state = 'posted'
            rec.state = 'draft'

    def txt_declaration(self):
        self.ensure_one()
        for rec in self:
            rec.report_historical = ('Ha generado el TXT de Declaración')         
        return {
            'type': 'ir.actions.act_url',
            'url': '/declaredTXTreport/%s' % self.id,
            'target': 'new',
            'res_id': self.id,
                }

     # txt 
    def act_getfile(self,declaration):
        r=''
        rs=''
        zero = 0
        content = ''
        if not self.env.user.company_id.rif:
            raise UserError('El RIF para la compañía no ha sido establecido.')
        for wh in declaration.tax_municipal_line:
               
                #amount_cal = rs.join(amount_cal.split('-'))
                if not wh.partner_id.partner_type:
                     raise UserError('Debe establecer el tipo de Proveedor/Cliente de alguna de las retenciones .')
                content += '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n'%(
                    wh.company_id.nifg,
                    wh.company_id.rif[:10]+'-'+wh.company_id.rif[10:],
                    wh.partner_id.partner_type,
                    wh.municipal_tax_id.date_end.name,
                    wh.municipal_tax_id.date_start.months_number,
                    r.join(wh.partner_id.econ_act_license or '00000'),
                    wh.partner_id.rif[:10]+'-'+wh.partner_id.rif[10:],
                    wh.partner_id.name,
                    datetime.strftime(wh.invoice_id.invoice_date,'%d/%m/%Y'),
                    wh.invoice_id.vendor_invoice_number,
                    wh.invoice_id.nro_control,
                    wh.comprobante,
                    datetime.strftime(wh.transaction_date,'%d/%m/%Y'),
                    str(round(wh.base_imponible,2)).replace(".",","),
                    str(round(wh.aliquot,2)).replace(".",",")+'0'+'%',
                    str(round(wh.amount_total_ret,2)).replace(".",","),
                    )
        return base64.encodebytes(bytes(content, 'utf-8'))

    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError('!No se puede eliminar una declaración de retencion municipal confirmada!') 
        return super(MunicipalTaxDeclaration, self).unlink() 

    def button_done(self):
        return self.env["account.retention.pay"]\
                    .with_context(active_ids=self.ids, active_model="tax.municipal.declaration", active_id=self.id)\
                    .action_pays_retention_iae()

