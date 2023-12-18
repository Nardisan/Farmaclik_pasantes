# -*- coding: utf-8 -*-

{
    'name': 'Sale Order Detail',
    'version':'1.0',
    'category': 'Inventory',
    'author': 'CorpoEureka',
    'category': 'Sale',
    'author': 'CorpoEureka',
    'support': 'proyectos@corpoeureka.com',
    'website' : 'http://www.corpoeureka.com',
    'license' : 'OPL-1',
    'description': """

    """,
    'depends':[
    'base',
    'stock',
    #'fleet',
    'sale_management',
    'account',
    'contacts',
    'purchase',

    ],
    'data':[
        'views/sale_order_view.xml',
        'views/stock_picking_view.xml',
        'views/purchase_view.xml',
    ],
    'installable': True,
    'application': True
}
