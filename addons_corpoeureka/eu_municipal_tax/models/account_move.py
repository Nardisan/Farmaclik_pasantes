# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    status_account = fields.Selection([
        ('not_declared','Sin Declaración'),
        ('to_declared', 'Por Declarar'),
        ('declared', 'Declarado'),
        ('done', 'Declaración Pagada'),
        #('no_declarable', 'No declarables'),
        ], string='Estatus tributario municipal', readonly=True, copy=False,index=True, track_visibility='always', default='not_declared', store=True)
