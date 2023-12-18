# -*- coding: utf-8 -*-
#codigo modificado por :
#eliomeza1@gmail.com

import logging
from odoo import api, fields, models, _ 
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger('__name__')




class AccountMoveLine(models.Model):
    _inherit = "account.move.line"


    tipo_factura = fields.Selection(related="move_id.move_type",string="Tipo de Factura")
    partner_id = fields.Many2one('res.partner', string='Partner', ondelete='restrict',store=True)
    partner_id_comany = fields.Many2one(related="move_id.company_id.partner_id",string="Campo Partner")
    concept_id_partner = fields.Many2one('muni.wh.concept.partner',string='Municipal Tax',domain="[('partner_id', '=', partner_id)]")
    concept_id_partner2 = fields.Many2one('muni.wh.concept',string='Municipal Tax')
    concept_id = fields.Many2one('muni.wh.concept',string='Municipal Tax')
    move_type = fields.Selection(related="move_id.move_type",)

    @api.onchange('concept_id_partner')
    def _compute_concept_id_partner(self):
    
        if self.tipo_factura =='in_invoice':
            for rec in self:
                if rec.tipo_factura == 'in_invoice':
                    if rec.concept_id_partner:
                        rec.concept_id = rec.concept_id_partner.muni_concept.id
                    else:
                        rec.concept_id = False

    @api.onchange('concept_id_partner2')
    def _compute_concept_id_partner2(self):
        for rec in self:
            if rec.tipo_factura == 'out_invoice':
                if rec.concept_id_partner2:
                    rec.concept_id = rec.concept_id_partner2
                else:
                    rec.concept_id = False






class AccountMove(models.Model):
    _inherit = 'account.move'


    wh_muni_id = fields.Many2one('municipality.tax', string='Withholding municipal tax', readonly=True, copy=False)


    def _create_muni_wh_voucher(self):

        vals = {}
        values = {}
        muni_wh = self.env['municipality.tax']
        muni_wh_line = self.env['account.move.line']
        _logger.info("""\n\n\n Hola se esta ejecutando el action_post de la retencion municipal\n\n\n""")
        # _logger.info("""\n\n\n\n  invoice %s \n\n\n""", invoice)
        # se crea el registro del modelo municipality.tax.line
        res = []
        aliquot_new = 0
        porcentaje_alic = 0
        for item in self.invoice_line_ids:
            # codigo darrell
            base_impuesto=item.price_subtotal
            impuesto_mun=item.concept_id.aliquot
            if not item.move_id.partner_id.partner_type:
                raise UserError('Debe configurar en el contacto el tipo de Proveedor y/o Cliente')
            if item.move_id.partner_id.partner_type == 'D':
                porcentaje_alic = '50'
                aliquot_new = (impuesto_mun*50)/100
            if item.move_id.partner_id.partner_type == 'T':
                porcentaje_alic = '100'
                aliquot_new = impuesto_mun
            if item.concept_id.aliquot>0:
                res.append((0,0, {
                    'code': item.concept_id.code,
                    'aliquot': aliquot_new,
                    'porcentaje_alic': porcentaje_alic,
                    'concept_id': item.concept_id.id,
                    'alicuota_normal' : item.concept_id.aliquot,
                    #'base_tax': self.amount_untaxed,
                    'base_tax': base_impuesto, # correcion darrell
                    'invoice_id': self.id,
                    'invoice_date' : self.date,
                    'vendor_invoice_number': self.vendor_invoice_number,
                    'invoice_ctrl_number': self.nro_control,
                    #'move_type':self.move_type,  # nuevo darrell
                }))
        _logger.info("\n\n\n res %s \n\n\n\n", res)
        # Se crea el registro de la retencion
        vals = {
           'partner_id': self.partner_id.id,
           'rif': self.partner_id.vat,
           'move_type': self.move_type,
           'invoice_id': self.id,
           'act_code_ids': res,
           'move_type':self.move_type,
           'manual_currency_exchange_rate':self.manual_currency_exchange_rate,
        }
        muni_tax = muni_wh.create(vals)
        self.write({'wh_muni_id': muni_tax.id})
        #raise UserError(_('cuentas = %s')%self.write({'wh_muni_id': muni_tax.id}))

    def actualiza_voucher_wh(self):
        #raise UserError(_('mama = %s')%self)
        cursor_municipality = self.env['municipality.tax'].search([('id','=',self.wh_muni_id.id)])
        cursor_municipality_line = self.env['municipality.tax.line'].search([('municipality_tax_id','=',self.wh_muni_id.id)])
        for borrar in cursor_municipality_line:
            borrar.unlink()
        res = []
        aliquot_new = 0
        porcentaje_alic = 0
        for item in self.invoice_line_ids:
            base_impuesto=item.price_subtotal
            impuesto_mun=item.concept_id.aliquot
            if not item.move_id.partner_id.partner_type:
                raise UserError('Debe configurar en el contacto el tipo de Proveedor y/o Cliente')
            if item.move_id.partner_id.partner_type == 'D':
                porcentaje_alic = '50'
                aliquot_new = (impuesto_mun*50)/100
            if item.move_id.partner_id.partner_type == 'T':
                porcentaje_alic = '100'
                aliquot_new = impuesto_mun
            if item.concept_id.aliquot>0:
                res.append((0,0, {
                    'code': item.concept_id.code,
                    'aliquot': aliquot_new,
                    'alicuota_normal' : item.concept_id.aliquot,
                    'porcentaje_alic': porcentaje_alic,
                    'concept_id': item.concept_id.id,
                    'base_tax': base_impuesto,
                    'invoice_id': self.id,
                    'invoice_date' : self.date,
                    'vendor_invoice_number': self.vendor_invoice_number,
                    'invoice_ctrl_number': self.nro_control,
                    'move_type': 'dont_apply',
                }))
        for det in cursor_municipality:
            self.env['municipality.tax'].browse(det.id).write({
                'move_type': self.move_type,
                'partner_id': self.partner_id.id,
                'rif': self.partner_id.vat,
                'invoice_id': self.id,
                'act_code_ids': res,
                'manual_currency_exchange_rate':self.manual_currency_exchange_rate,
                })


    def action_post(self):
        """This function create municital retention voucher too."""
        invoice = super().action_post()
        # es agente de retencion municipal
        _logger.info("\n\n\n\n action_post de Impuestos municipales \n\n\n\n")
      
        if self.partner_id.muni_wh_agent==True or self.company_id.partner_id.muni_wh_agent==True:
            # si no existe una retencion ya
            bann=0
            bann=self.verifica_exento_muni()
            if bann>0:
                if not self.wh_muni_id:
                    self._create_muni_wh_voucher()
                if self.wh_muni_id:
                    self.actualiza_voucher_wh()
                    self.unifica_alicuota_iguales()
                #   self.update_muni_wh()#actualiza cuando ya existe
        return invoice

    def button_draft(self):
        '''
        Este metodo se usa para pasar las retenciones a borrador cuando se pasa la factura de publicado a borrador (IAE)
        :return:
        '''
        for hw in self:
            if hw.wh_muni_id.state == 'posted':
                hw.wh_muni_id.write({
                'state': 'draft',
                })
            if hw.wh_muni_id.asiento_post:
                hw.wh_muni_id.asiento_post.write({
                'state':'draft',
                })
        return super(AccountMove, self).button_draft()

    def verifica_exento_muni(self):
        acum=0
        #raise UserError(_('self = %s')%self.id)
        puntero_move_line = self.env['account.move.line'].search([('move_id','=',self.id)])
        for det_puntero in puntero_move_line:
            acum=acum+det_puntero.concept_id.aliquot
        return acum


    def unifica_alicuota_iguales(self):
        if self.move_type=='in_invoice' or self.move_type=='in_refund' or self.move_type=='in_receipt':
            type_tax_use='purchase'
        if self.move_type=='out_invoice' or self.move_type=='out_refund' or self.move_type=='out_receipt':
            type_tax_use='sale'
        lista_impuesto = self.env['muni.wh.concept'].search([])
        #raise UserError(_('lista_impuesto = %s')%lista_impuesto)
        for det_tax in lista_impuesto:
            #raise UserError(_('det_tax.id = %s')%det_tax.id)
            lista_mov_line = self.env['municipality.tax.line'].search([('invoice_id','=',self.id),('concept_id','=',det_tax.id)])
            #raise UserError(_('lista_mov_line = %s')%lista_mov_line)
            #amount_untaxed=0
            base_tax=0
            #amount_vat_ret=0
            wh_amount=0
            #retention_amount=0
            if lista_mov_line:
                for det_mov_line in lista_mov_line:                
                    base_tax=base_tax+det_mov_line.base_tax
                    wh_amount=wh_amount+det_mov_line.wh_amount
                    #retention_amount=retention_amount+det_mov_line.retention_amount

                    code=det_mov_line.code
                    #raise UserError(_('nombre1 = %s')%nombre)
                    aliquot=det_mov_line.aliquot
                    invoice_id=det_mov_line.invoice_id.id
                    vendor_invoice_number=det_mov_line.vendor_invoice_number
                    municipality_tax_id=det_mov_line.municipality_tax_id.id
                    invoice_ctrl_number=det_mov_line.invoice_ctrl_number
                    tipe=det_mov_line.move_type
                    concept_id=det_mov_line.concept_id.id
                #raise UserError(_('lista_mov_line = %s')%lista_mov_line)
                lista_mov_line.unlink()
                move_obj = self.env['municipality.tax.line']
                valor={
                'code':code,
                'aliquot':aliquot,
                'invoice_id':invoice_id,
                'vendor_invoice_number':vendor_invoice_number,
                'municipality_tax_id':municipality_tax_id,
                'invoice_ctrl_number':invoice_ctrl_number,
                'base_tax':base_tax,
                'wh_amount':wh_amount,
                'move_type':tipe,
                'concept_id':concept_id,
                }
                move_obj.create(valor)
