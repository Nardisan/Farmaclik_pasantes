# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models


class Company(models.Model):
    _inherit = "res.company"

    def _create_transit_location(self):
        '''Create a transit location with company_id being the given company_id. This is needed
           in case of resuply routes between warehouses belonging to the same company, because
           we don't want to create accounting entries at that time.
        '''
        parent_location = self.env.ref('stock.stock_location_locations', raise_if_not_found=False)
        for company in self:
            location = self.env['stock.location'].create({
                'name': _('Inter-warehouse transit ' + company.name ),
                'usage': 'transit',
                'location_id': parent_location and parent_location.id or False,
                'company_id': company.id,
                'active': False
            })

            company.write({'internal_transit_location_id': location.id})

            company.partner_id.with_company(company).write({
                'property_stock_customer': location.id,
                'property_stock_supplier': location.id,
            })

    def _create_inventory_loss_location(self):
        parent_location = self.env.ref('stock.stock_location_locations_virtual', raise_if_not_found=False)
        for company in self:
            inventory_loss_location = self.env['stock.location'].create({
                'name': 'Inventory adjustment ' + company.name,
                'usage': 'inventory',
                'location_id': parent_location.id,
                'company_id': company.id,
            })
            self.env['ir.property']._set_default(
                "property_stock_inventory",
                "product.template",
                inventory_loss_location,
                company.id,
            )

    def _create_production_location(self):
        parent_location = self.env.ref('stock.stock_location_locations_virtual', raise_if_not_found=False)
        for company in self:
            production_location = self.env['stock.location'].create({
                'name': 'Production ' + company.name,
                'usage': 'production',
                'location_id': parent_location.id,
                'company_id': company.id,
            })
            self.env['ir.property']._set_default(
                "property_stock_production",
                "product.template",
                production_location,
                company.id,
            )


    def _create_scrap_location(self):
        parent_location = self.env.ref('stock.stock_location_locations_virtual', raise_if_not_found=False)
        for company in self:
            scrap_location = self.env['stock.location'].create({
                'name': 'Scrap ' + company.name,
                'usage': 'inventory',
                'location_id': parent_location.id,
                'company_id': company.id,
                'scrap_location': True,
            })