from odoo import api, fields, models
from odoo.exceptions import ValidationError

class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    plantilla_mensaje_sms_para_pacientes_cronicos = fields.Char(size=140, string="Plantilla Mensaje SMS para Pacientes Crónicos", default="Saludos [p], desde [c] le recordamos que puede adquirir [m] cuando guste, estaremos para servirle.", config_parameter="mensajeria_pacientes_cronicos.plantilla_mensaje_sms_para_pacientes_cronicos")