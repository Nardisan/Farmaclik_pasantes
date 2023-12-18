from odoo import api, fields, models


class RetProductIslr(models.Model):
    _inherit = 'product.template'

    # Columns
    service_concept_retention = fields.Many2one('account.withholding.concept', 'Withholding', copy=False)


