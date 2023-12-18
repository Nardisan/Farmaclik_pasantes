# coding: utf-8
from odoo import fields, models, api, exceptions, _

class Account(models.Model):
    _inherit = 'account.move'


    is_credit = fields.Boolean(string="A Crédito",default=False)