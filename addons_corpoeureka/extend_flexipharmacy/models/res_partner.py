
from odoo import models, fields, api, _

class ResPartner(models.Model):
    _inherit = 'res.partner'

    #DESCUENTO PARA CLIENTES 
    descuento = fields.Integer(string="Descuento aplicado al cliente")
    #Especialidad
    especialidad = fields.Char(string="Especialidad")
    #Centro medico
    medical_center = fields.Char(string="Centro Médico")
    


    
    