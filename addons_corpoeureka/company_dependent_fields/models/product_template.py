# -*- coding: utf-8 -*-#

from odoo import api, fields, models, _

class ProductTemplate(models.Model):
	_inherit = 'product.template'

	list_price = fields.Float(company_dependent=True)
	lst_price = fields.Float(tracking=True)

	@api.depends('company_id')
	def _compute_currency_id(self):
		for template in self:
			template.currency_id = template.company_id.sudo().currency_id.id or self.env.company.currency_id.id