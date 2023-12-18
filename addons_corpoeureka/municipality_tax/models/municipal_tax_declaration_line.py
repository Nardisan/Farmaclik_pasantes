# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError

class TaxMunicipalLine(models.Model):
    _name = 'tax.municipal.declaration.line'
    _description ="Lineas de retenciones"

    company_id = fields.Many2one('res.company',string="Compañía", required=True, default=lambda self: self.env.company,track_visibility='always',invisible=True)
    tax_municipal_id = fields.Many2one('tax.municipal.declaration',string='Retencion de Impuesto municipal')
    comprobante = fields.Char(string='N° de Comprobante',required=True,readonly=True)
    municipal_tax_id = fields.Many2one('municipality.tax',string='Retencion',required=True,readonly=True)
    transaction_date = fields.Date(string="Fecha",readonly=True)
    partner_id = fields.Many2one('res.partner', string="Empresa",readonly=True)
    rif = fields.Char(string="Rif",store=True,required=True,readonly=True)
    #name = fields.Char(string="Factura",store=True, required=True)
    invoice_id = fields.Many2one('account.move',string='Factura',required=True,readonly=True)
    base_imponible = fields.Float(string="Base Imponible",store=True,readonly=True)
    amount_total_invoice = fields.Float(string="Monto Total",store=True,readonly=True)
    aliquot = fields.Float(string="% Alicuota",store=True,readonly=True)
    amount_total_ret = fields.Float(string="Monto de Retenido",store=True,readonly=True)


    # Evita dejar una Factura en no_declared si se elimina de las lineas de las Facturas estando en to_declared    
    # def unlink(self):
    #     for rec in self:
    #         if rec.municipal_tax_id:
    #             for invoice in rec.municipal_tax_id:
    #                 if invoice.state != 'not_declared':
    #                     invoice.status_account = 'not_declared'
    #     return super(TaxMunicipalLine, self).unlink()


    




    
