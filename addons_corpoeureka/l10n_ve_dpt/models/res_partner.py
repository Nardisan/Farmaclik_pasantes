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
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api, _

class ResPartnerInherit(models.Model):

	_inherit = 'res.partner'

	country_id=fields.Many2one(default=lambda self: self.env['res.country'].search([('code','=','VE')]))
	city_id = fields.Many2one('res.country.state.city', 'Ciudad')
	municipality_id = fields.Many2one('res.country.state.municipality', 'Municipality')
	parish_id = fields.Many2one('res.country.state.municipality.parish', 'Parish')

	# @api.model_create_multi
	# def create(self, vals):

	# 	if 'name' in vals[0]:
	# 		vals[0]['name'] = str(vals[0]['name']).upper()
	# 	res = super(ResPartnerInherit, self).create(vals)
	# 	return res

	def write(self, vals):

		if 'name' in vals:
			vals['name'] = str(vals['name']).upper()
		res= super(ResPartnerInherit,self).write(vals)
		return res


	@api.onchange('country_id')
	def _onchage_country_id(self):
		if self.state_id:
			self.state_id = self.city_id = self.municipality_id = self.parish_id = self.zip = False
			
	@api.onchange('state_id')
	def _onchage_state(self):
		if self.state_id:
			self.city_id = self.municipality_id = self.parish_id = self.zip = False

	@api.onchange('city_id')
	def _onchage_city(self):
		if self.city_id:
			self.city = self.city_id.name
			self.municipality_id = self.parish_id = self.zip = False

	@api.onchange('municipality_id')
	def _onchage_municipality(self):
		if self.municipality_id:
			self.parish_id = self.zip = False

	@api.model
	def _address_fields(self):
		address_fields = set(super(ResPartnerInherit, self)._address_fields())
		address_fields.add('municipality_id')
		address_fields.add('parish_id')
		return list(address_fields)

	# @api.multi
	def _display_address(self, without_company=False):

		'''
		The purpose of this function is to build and return an address formatted accordingly to the
		standards of the country where it belongs.

		:param address: browse record of the res.partner to format
		:returns: the address formatted in a display that fit its country habits (or the default ones
			if not country is specified)
		:rtype: string
		'''
		# get the information that will be injected into the display format
		# get the address format
		address_format = self.country_id.address_format or \
			  "%(street)s\n%(street2)s\n%(city)s %(state_code)s %(zip)s\n%(country_name)s"
		args = {
			'state_code': self.state_id.code or '',
			'state_name': self.state_id.name or '',
			'municipality_code': self.municipality_id.code or '',
			'municipality_name': self.municipality_id.name or '',
			'parish_code': self.parish_id.code or '',
			'parish_name': self.parish_id.name or '',
			'country_code': self.country_id.code or '',
			'country_name': self.country_id.name or '',
			'company_name': self.commercial_company_name or '',
		}
		for field in self._address_fields():
			args[field] = getattr(self, field) or ''
		if without_company:
			args['company_name'] = ''
		elif self.commercial_company_name:
			address_format = '%(company_name)s\n' + address_format
		return address_format % args
