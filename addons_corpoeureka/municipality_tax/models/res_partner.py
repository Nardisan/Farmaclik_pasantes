# -*- coding: utf -*-


from odoo import api, fields, models, _

class Partners(models.Model):
    _inherit = 'res.partner'


    muni_wh_agent = fields.Boolean(string='Retention agent', help='True if your partner is a municipal retention agent')
    purchase_jrl_id = fields.Many2one('account.journal', string='Purchase journal', company_dependent=True)
    sale_jrl_id = fields.Many2one('account.journal', string='Sales journal')
    account_ret_muni_receivable_id = fields.Many2one('account.account', company_dependent=True, string='Cuenta Retencion Clientes')
    account_ret_muni_payable_id = fields.Many2one('account.account', company_dependent=True, string='Cuenta Retencion Proveedores')
    econ_act_license = fields.Char(string='License number', help='Economic activity license number',track_visibility='always')
    ids_concept_muni = fields.One2many(comodel_name="muni.wh.concept.partner",inverse_name='partner_id',track_visibility='always',string='Codigo de Actividad Economica', help='Actividad(s) económica asignado por la alcaldía')
    partner_type = fields.Selection(selection=[('D', 'Domiciliado en el municipio'),('T', 'Transeúnte')],string='Tipo de Cliente/Proveedor',required=True,default="T")

