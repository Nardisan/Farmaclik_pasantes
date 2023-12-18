from odoo import api, fields, models, tools, _

class ResCompany(models.Model):
    _inherit = 'account.fiscal.position'

    ret_IVA_purchase = fields.Selection(([('01-sin','No Retention'),
                                            ('02-special', '75% special contributor'),
                                            ('03-ordinary', '100% contributor ordinary'),
                                            ]),
                                             string='Retention IVA Purchase',
                                             help='Porcentaje Retenido por este Contribuyente como Proveedor')

    ret_IVA_sale = fields.Selection(([('01-sin','No Retention'),
                                            ('02-special', '75% special contributor'),
                                            ('03-ordinary', '100% contributor ordinary'),
                                            ]),
                                             string='Retention IVA Sale',                                       
                                             help='Porcentaje Retenido por este Contribuyente como Cliente')