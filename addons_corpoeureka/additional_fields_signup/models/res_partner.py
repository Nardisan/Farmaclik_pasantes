# -*- coding: utf-8 -*-

from odoo import fields, models

class ResPartnerSector(models.Model):
	_name			=	'res.partner.ciudad'
	_description 	=	'Ciudades'

	def _get_country_vene(self):
		return self.env['res.country'].search([('name', '=', 'Venezuela')], limit=1)
	name 		= fields.Char(string="Nombre de la ciudad", required=True)	
	short_name 	= fields.Char(string="Nombre corto",required=True)
	country_id = fields.Many2one('res.country',string="Estado",default=_get_country_vene)
	state_id  = fields.Many2one('res.country.state',string="Estado",required=True)

class ResPartnerSector(models.Model):
	_name			=	'res.partner.sectores'
	_description 	=	'Sectores'

	name 		=  	fields.Char(string="Nombre del Sector", required=True)
	short_name	=  	fields.Char(string="Nombre Corto",required=True)
	id_ciudad	=	fields.Many2one('res.partner.ciudad', string="Ciudad", required=True)

class ResPartner(models.Model):
    _inherit = "res.partner"

    birthday 	= fields.Date('Fecha de nacimiento')
    ciudad 		= fields.Many2one('res.partner.ciudad',string="Ciudades")
    sector 		= fields.Many2one('res.partner.sectores',string="Sector")
