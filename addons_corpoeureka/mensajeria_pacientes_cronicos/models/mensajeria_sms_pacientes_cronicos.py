from odoo import fields, models, api
from datetime import datetime, date, timedelta
from odoo.exceptions import ValidationError

class MensajeriaSmsPacientesCronicos(models.Model):

    _name = 'mensajeria.sms.pacientes.cronicos'
    _description = 'Mensajeria SMS programada de para pacientes cronicos'

    @api.model
    def calcular_mensaje_plantilla(self):
        config = self.env['ir.config_parameter']
        return config.sudo().get_param("mensajeria_pacientes_cronicos.plantilla_mensaje_sms_para_pacientes_cronicos")


    name = fields.Char(string="Nombre", compute="calcular_nombre")
    registrado_desde  = fields.Many2one('res.company', string="Registrado desde", required=True)
    telefono = fields.Char(related='paciente_id.phone',string="Teléfono")
    paciente_id  = fields.Many2one('res.partner', string="Paciente", required=True)
    medicamento_id  = fields.Many2one('product.product', string="Medicamento", required=True)
    mensaje_plantilla = fields.Char(size=140, string="Mensaje Plantilla", required=True, default = calcular_mensaje_plantilla)
    mensaje_final = fields.Char(size= 280, string="Mensaje Final", compute="calcular_mensaje_final")
    fecha_de_registro = fields.Date(string='Fecha de Registro', required=True,  default=datetime.today())
    fecha_de_envio_sms = fields.Date(string='Fecha de envio SMS', compute="calcular_fecha_de_envio_sms", store=True, required=True)
    estatus_de_envio_sms = fields.Selection([('Pendiente','Pendiente'), ('Enviado', 'Enviado')], string='Estatus de envio SMS', default='Pendiente')

    @api.depends('paciente_id', 'medicamento_id')
    def calcular_nombre(self):
        for e in self:
            e.name = e.paciente_id.name

    @api.depends('mensaje_plantilla', 'registrado_desde', 'paciente_id', 'medicamento_id', 'fecha_de_registro' )
    def calcular_mensaje_final(self):
        mensaje = ""
        for e in self:
            mensaje = str(e.mensaje_plantilla)
            mensaje = mensaje.replace("[c]", str(e.registrado_desde.name) if e.registrado_desde else "[c]")
            mensaje = mensaje.replace("[p]", str(e.paciente_id.name) if e.paciente_id else "[p]")
            mensaje = mensaje.replace("[m]", str(e.medicamento_id.name) if e.medicamento_id else "[m]")
            mensaje = mensaje.replace("[f]", str(e.fecha_de_registro) if e.fecha_de_registro else "[f]")
            mensaje = mensaje.replace("Blister ", "")
            mensaje = mensaje.replace("Generico ", "")
            mensaje = mensaje.replace("generico ", "")
            mensaje = mensaje.replace("Tab", "")
            mensaje = mensaje.replace("Tabletas", "")

            # Blister Generico
            e.mensaje_final = mensaje

    @api.depends('fecha_de_registro', 'medicamento_id')
    def calcular_fecha_de_envio_sms(self):
        for e in self:
            e.fecha_de_envio_sms = e.fecha_de_registro + timedelta(days=e.medicamento_id.dias_de_duracion) if e.fecha_de_registro else False
    
