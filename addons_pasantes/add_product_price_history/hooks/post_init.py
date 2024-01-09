# post_init.py
from odoo import api, SUPERUSER_ID


def initialize_module(cr, registry):
    # Obtener el objeto del modelo
    env = api.Environment(cr, SUPERUSER_ID, {})
    model = env["product.template"]
    # Llamar al método del modelo
    model.register_starting_price()
