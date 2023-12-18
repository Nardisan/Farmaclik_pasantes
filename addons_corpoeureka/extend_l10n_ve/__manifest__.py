# -*- coding: utf-8 -*-
{
    'name': "extend_l10n_ve",

    'description': """
       Extención de localización 
       -Base imponible de Factura a Proveedor 
       Extencion de l10n_ve_accountant
       -Reporte en excel de venta y compra
    """,

    'author': "FARMACIA_PP",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'account',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','l10n_ve_accountant'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_move_view.xml',
        'reports/l10n_ve_accountant_shoopin_book.xml',
        'reports/l10n_ve_accountant_sale_book.xml',
        'reports/report.xml',
        'wizard/wizard_book_view.xml',
        'wizard/wizard_sale_book_view.xml',
    ],
}