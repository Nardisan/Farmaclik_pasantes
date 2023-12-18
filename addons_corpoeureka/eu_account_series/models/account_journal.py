# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    multi_serie     =   fields.Boolean(string="Multiserie company",invisible=True, related="company_id.multi_serie")
    account_serie   =   fields.Selection(
        [
        ('a', 'Serie A'), 
        ('b', 'Serie B'),
        ('c', 'Serie C')
        ], 
        string="Tipo de Serie",
        default="a")