# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    Autor: Brayhan Andres Jaramillo Castaño
#    Correo: brayhanjaramillo@hotmail.com
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import api, fields, models, _

class ResCountryStateCity(models.Model):

	_name = 'res.country.state.city'
	_description="Cities"

	code = fields.Char(u'Código', size=5, required=True)
	name = fields.Char('Nombre', size=64, required=True)
	state_id = fields.Many2one('res.country.state', 'Estado', required=True)
	country_id = fields.Many2one('res.country', u'País', required=True)
	municipality_id = fields.One2many('res.country.state.municipality', 'city_id', 'Municipios en esta Ciudad')
	_sql_constraints = [('res_country_state_city_code_uniq', 'unique (code)', u'Ya existe una ciudad con el mismo Código')]


	# def create(self, vals):
	# 	vals['name'] = str(vals['name']).upper()
	# 	res = super(ResCountryStateCity, self).create(vals)
	# 	return res

	# def write(self, vals):
	# 	if 'name' in vals:
	# 		vals['name'] = str(vals['name']).upper()
	# 	res= super(ResCountryStateCity,self).write(vals)
	# 	return res

	def name_get(self):
		result = []
		for record in self:
			result.append((record.id, "{} ({})".format(record.name, record.state_id.code)))
		return result

ResCountryStateCity()