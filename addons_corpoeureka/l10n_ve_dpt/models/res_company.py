# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _


class Company(models.Model):
    _inherit = "res.company"

    municipality_id = fields.Many2one('res.country.state.municipality', compute='_compute_address', inverse='_inverse_municipality', string='Municipality')
    parish_id = fields.Many2one('res.country.state.municipality.parish', compute='_compute_address', inverse='_inverse_parish', string='Parish')
    country_id=fields.Many2one(default=lambda self: self.env['res.country'].search([('code','=','VE')]))

    def _compute_address(self):
        for company in self.filtered(lambda company: company.partner_id):
            address_data = company.partner_id.sudo().address_get(adr_pref=['contact'])
            if address_data['contact']:
                partner = company.partner_id.browse(address_data['contact']).sudo()
                company.street = partner.street
                company.street2 = partner.street2
                company.city = partner.city
                company.zip = partner.zip
                company.state_id = partner.state_id
                company.country_id = partner.country_id
                company.municipality_id = partner.municipality_id
                company.parish_id = partner.parish_id

    def _inverse_municipality(self):
        for company in self:
            company.partner_id.municipality_id = company.municipality_id

    def _inverse_parish(self):
        for company in self:
            company.partner_id.parish_id = company.parish_id
