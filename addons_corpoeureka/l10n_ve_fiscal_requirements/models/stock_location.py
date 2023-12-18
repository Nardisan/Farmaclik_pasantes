# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class StockLocation(models.Model):
    _inherit = 'stock.location'
    
    # _sql_constraints = [
    #     ('location_name_uniq', 'unique(complete_name, company_id)', 'The name of the location must be unique per company!'),
    #     ('location_name_uniq_without', 'unique(complete_name)', 'The name of the location must be unique!'),
    # ]

    # @api.constrains('complete_name')
    # def _check_complete_name(self):
    #     if self.complete_name:
    #         name_exist = self.search_count([('complete_name', '=', self.complete_name),('id', '!=', self.id),('company_id', '=', self.env.company.id)])
    #         if name_exist > 0:
    #             raise ValidationError(
    #                 ("Ya existe un registro con este nombre para ese Almacén"))
    #         else:
    #             return True