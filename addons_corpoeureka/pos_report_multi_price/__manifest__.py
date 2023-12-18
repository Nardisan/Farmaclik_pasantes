# -*- coding: utf-8 -*-
{
    'name': 'PoS Report and Payments Multi currency',
    'version': '14.0.1.0',
    'category': 'Point Of Sale',
    'summary': 'Customized Receipt of Point Of Sales',
    'description': "Customized our point of sale detail Report",
    'depends': ['base', 'point_of_sale','pos_show_dual_currency'],
    "data": [
    'views/pos_order_view.xml',
    'views/pos_order_line_view.xml',
    'views/pos_payment_view.xml',
    'views/report_saledetails.xml',
    ],
    'installable': True,
}
