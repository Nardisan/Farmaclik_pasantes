# -*- coding: utf-8 -*-
{
    'name': "extend_stock",

    'description': """
       Modificacion de Nombres de las localizaciones que se crean por default para cada empresa
       (NO QUITAR ESTE MODULO YA QUE NO PODRA CREAR UNA NUEVA COMPAÑIA )
    """,

    'author': "FARMACIA_PP",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'stock',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
    ],
}