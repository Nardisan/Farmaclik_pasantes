# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError

class AccountWhIslrDeclaration(models.Model):
    _name = "account.wh.islr.declaration"
    _inherit= ['mail.thread', 'mail.activity.mixin']
    _description = "Declraciones de ISLR"
    
    name = fields.Char(string="Número de Declaración",readonly=True,tracking=True)
    withholding_id = fields.One2many('account.wh.islr','declaration_id', 'Retenciones Asociadas',readonly=True,tracking=True)
    date = fields.Datetime(
        string='Fecha', readonly=True,
        default = fields.Datetime.now(),tracking=True)
    file_xml_id = fields.Many2many('ir.attachment', 'withholding_attachment_rel_two', 'withholding_id', 'attachment_id', string="Archivo XML", copy=False, readonly=True,required=True,tracking=True)
    company_id = fields.Many2one(
        'res.company', string='Compañia', required=True, readonly=True,
        default=lambda self: self.env.company.id,
        help="Company")    
    period = fields.Char(string='Periodo de la Retención', size=64, readonly=True,tracking=True)
    @api.model    
    def create(self, vals):
        name = self.env['ir.sequence'].next_by_code('islr.declaration.seq')
        vals.update({
            'name': name
            })
        res = super(AccountWhIslrDeclaration, self).create(vals)
        return res  