from odoo import fields, models, api
from datetime import datetime, date, timedelta
from odoo.exceptions import ValidationError

class ProductTemplate(models.Model):

    _inherit = "product.template"

    para_enfermedad_cronica = fields.Boolean( string="Para enfermedad crónica", default=False )
    dias_de_duracion = fields.Integer(string="Días de duración", default=0)

    @api.constrains('dias_de_duracion')
    def _check_value(self):
        if self.dias_de_duracion < 0:
            raise ValidationError("Campo 'Días de Duración' debe ser mayor o igual a cero (0)")
