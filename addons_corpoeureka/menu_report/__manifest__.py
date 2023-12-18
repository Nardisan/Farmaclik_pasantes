# -*- coding: utf-8 -*-
{
    'name': "menu_report",

    'summary': """
        Reportes en general""",

    'description': """
        Reportes de ventas, facturacion e inventario
    """,

    'author': "FARMACIA_PP",
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','point_of_sale','pos_orders_all'],
    'application': True,

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/stock_negative.xml',
        'views/menu_report.xml',
        'views/pos_order_negative_view.xml',
        'views/pos_order_report_view.xml'
    ],
}
