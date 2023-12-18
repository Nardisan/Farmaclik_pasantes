# -*- coding: utf-8 -*-
{
    'name': "change_product",

    'description': """
       Adicion del campo Rentabilidad en la ficha del producto
       Actualizacion de principio activo
    """,

    'author': "FARMACIA_PP",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'stock',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/product_template.xml',
        'views/product_profitability.xml',
    ],
}
