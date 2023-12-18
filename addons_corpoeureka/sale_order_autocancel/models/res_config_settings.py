# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    enable_autocancel_orders = fields.Boolean(string="Enable Auto Cancel Orders",
                                              config_parameter='config_enable_autocancel_orders')
    days_autocancel_orders = fields.Integer(string="Auto cancel orders (draft, sent) after (days)",
                                            config_parameter='config_days_autocancel_orders')
