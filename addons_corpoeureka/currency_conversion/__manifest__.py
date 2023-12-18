# -*- coding: utf-8 -*-
{
    'name': "currency_conversion",

    'description': """
       Conversion correcta en bolivares del monto total de facturas 
    """,

    'author': "FARMACIA_PP",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'account',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','eu_multi_currency'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
    ],
}