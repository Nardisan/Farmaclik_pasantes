# -*- coding: utf-8 -*-
{
    'name': "change_purchase_order",

    'summary': """
        Cambios en ordenes de compras""",

    'description': """
        Cambios en ordenes de compras
    """,

    'author': "FarmaPaseo",
    'category': 'purchase',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','purchase'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/purchase_views.xml',
    ],
}
