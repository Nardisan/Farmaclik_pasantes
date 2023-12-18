# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Instant and Manual Multi Currency",

    'version': '1.0',
    'category' : 'Account - Facturación',
    'license': 'Other proprietary',
    'summary': """Esta aplicación permite visualizar otra moneda en la vista de Facturación.""",
    'website': "http://www.corpoeureka.com",
    'author': 'CorpoEureka',
    'support': 'proyectos@corpoeureka.com',
    'license' : 'OPL-1',
    'description': """
Esta APP permite visualizar y calcular otro campo Total en la vista de Facturación
Permitiendo mostrar el total en otra divisa
    """,
    'depends': [
                'account',
                'sale',
                'purchase',
                'sr_manual_currency_exchange_rate',
                'analytic',
                #'account_budget',
                ],
    'data':[
       'views/product_pricelist_view.xml',
       'views/product_pricelist_item_view.xml',
       'views/res_currency_view.xml',
        'views/res_currency_rate_view.xml',
       'views/account_move_view.xml',
       'views/account_move_line_view.xml',
       'views/account_payment_view.xml',
       'views/sale_order_view.xml',
       'views/sale_order_line_view.xml',
       'views/purchase_order_view.xml',
       'views/purchase_order_line_view.xml',
       'views/account_analytic_line_view.xml',
       'views/account_analytic_account_view.xml',
       #'views/account_budget_view.xml',
       'report/report_invoice.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
