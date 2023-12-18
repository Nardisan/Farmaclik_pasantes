# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ResCompany(models.Model):
    _inherit = 'res.company'

    multi_serie = fields.Boolean(string="¿Utiliza Multi Series?")