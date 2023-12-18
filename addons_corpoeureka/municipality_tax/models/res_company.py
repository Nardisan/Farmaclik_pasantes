# -*- coding: utf-8 -*-


from odoo import api, fields, models, _ 

class Company(models.Model):
    _inherit = 'res.company'

    nit = fields.Char(string='NIT', help='Old tax identification number replaced by the current RIF')
    econ_act_license = fields.Char(string='License number', help='Economic activity license number', required=True)
    nifg = fields.Char(string='Economic activity code', help='Number assigned by mayoralty')

    purchase_iae_ret_account = fields.Many2one('account.account', string='Cuenta de retención IAE proveedor')
    sale_iae_ret_account = fields.Many2one('account.account', string='Cuenta de declaracion IAE Cliente')
    journal_iae = fields.Many2one('account.journal', string='Diario del IAE')

    #porcentaje_de_retencion_iae = fields.Selection([('100', '100%'), ('50', '50%')], string='Porcentaje de Retención IAE', required=True)
