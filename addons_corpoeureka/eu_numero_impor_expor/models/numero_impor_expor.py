from dataclasses import field
import string
from tabnanny import check
from odoo import models, fields, api

class NumeroEimporExpor(models.Model):
    _inherit = 'account.move'

    @api.onchange('doc_impor_export')
    def _onchange_doc_impor_export(self):
        for rec in self:

            rec.num_export = False
            rec.num_import = False
        

    doc_impor_export= fields.Boolean(string="Doc. impor/export")

    num_import= fields.Char(string="Num.Planilla de Importacion")  
    num_export= fields.Char(string="Num.Expediente Importacion")

    