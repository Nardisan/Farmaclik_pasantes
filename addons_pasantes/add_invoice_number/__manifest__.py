# -*- coding: utf-8 -*-
{
    'name': "add_invoice_number",

    'summary': """
        Añade el numero de proveedor a la factura de proveedor
        """,

    'description': """
        Añade el campo de nro de proveedor a la factura de proveedor extendiendo el modelo account.move
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'l10n_ve_fiscal_requirements', 'eu_multi_currency'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],

}
