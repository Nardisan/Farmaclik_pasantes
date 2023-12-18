# coding: utf-8
###########################################################################

from odoo import fields, models, api


class ResCompany(models.Model):
    _inherit = 'res.company'


    calculate_wh_itf= fields.Boolean(
            'Retención automática de IGTF',
            help='Cuando sea Verdadero, la Retención de la IGTF del Proveedor se comprobará y'
                 'se validará automáticamente', default=False)
    wh_porcentage = fields.Float('Porcentaje IGTF', help="El porcentaje a aplicar para retener")

    account_wh_itf_id = fields.Many2one('account.account', string="Cuenta IGTF", help="Esta cuenta se utilizará en lugar de la predeterminada"
                                                       "para generar el asiento del IGTF", company_dependent=True)

    @api.onchange('calculate_wh_itf')
    def _onchange_check_itf(self):

        if not self.calculate_wh_itf:
            self.write({'wh_porcentage':0.0,
                        'account_wh_itf_id': False})
        return
