# -*- coding: utf-8 -*-

from odoo import models

class PosSession(models.Model):
    _inherit = 'pos.session'

    def print_z_report(self):
        pass

    def print_x_report(self):
        pass