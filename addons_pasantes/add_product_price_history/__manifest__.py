# -*- coding: utf-8 -*-
{
    'name': "add_product_price_history",

    'summary': """
        Añade un historial de cambios de precios a los productos
        """,

    'description': """
        Añade un historial de cambios de precios a los productos, tomando en cuenta
        la inicializacion del modulo y las actualizaciones o creaciones sobre el modelo
        de productos.
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'product', 'flexipharmacy'],

    "post_init_hook": "initialize_module",

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        # Cron
        'cron/register_product_price_startup.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
