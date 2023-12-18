# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError

class TaxMunicipalLine(models.Model):
    _name = 'tax.municipal.line'
    _description ="Tax municipal line"

    company_id = fields.Many2one('res.company',string="Compañía", required=True, default=lambda self: self.env.company,track_visibility='always',invisible=True)
    invoice_id_line = fields.Many2one('tax.municipal',string='Impuesto Actividad Economica')

    invoice_id = fields.Many2one('account.move',string='Factura',required=True,readonly=True)
    date_invoice = fields.Date(string="Fecha",readonly=True)
    partner_id = fields.Many2one('res.partner', string="Cliente",readonly=True)
    rif = fields.Char(string="Rif",store=True,required=True,readonly=True)
    #name = fields.Char(string="Factura",store=True, required=True)
    amount_untaxed = fields.Float(string="Base Imponible",store=True,readonly=True)
    amount_tax = fields.Float(string="I.V.A",store=True,readonly=True)
    monto_muni = fields.Float(string="Monto de IAE",store=True,readonly=True)
    amount_total = fields.Float(string="Monto Total",store=True,readonly=True)
    aliquot_municipal = fields.Float(string="% Alicuota ",store=True,readonly=True)
    total_amount_tax_ret = fields.Float(string="Monto Ret. por el Cliente", store=True,readonly=True)
    monto_total_iae = fields.Float(string="Monto de IAE a Pagar",store=True,readonly=True)


    # Evita dejar una Factura en no_declared si se elimina de las lineas de las Facturas estando en to_declared    
    def unlink(self):
        for rec in self:
            if rec.invoice_id:
                for invoice in rec.invoice_id:
                    if invoice.status_account != 'not_declared':
                        invoice.status_account = 'not_declared'
        return super(TaxMunicipalLine, self).unlink()


    




    
