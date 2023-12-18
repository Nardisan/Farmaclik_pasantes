# -*- coding: utf-8 -*-


import logging
from datetime import datetime, date
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError




class AccountJournal(models.Model):
    _inherit = 'account.journal'

    tipo_bank = fields.Selection([('na', 'Nacional'),('ex', 'Extranjero')], required=True)
    apply_igft = fields.Boolean(string="¿Aplica IGTF ?",track_visibility="always")