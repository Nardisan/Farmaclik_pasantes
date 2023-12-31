# -*- coding: utf-8 -*-
{
    'name': "eCommerce Multipayment",
    'summary': "A module that allows multiple payment methods to pay a sale order on website's shop",
    'author': 'CorpoEureka',
    'support': 'proyectos@corpoeureka.com',
    'website' : 'http://www.corpoeureka.com',
    'category': 'Website',
    'version': '0.5.0',
    'depends': [
        'base',
        'website_sale', 
        'sale', 
        'payment',
        'sale_management', 
        'eu_multi_currency',
        'flexipharmacy',
        'eu_website_multicurrency',
        'theme_clarico_vega',
    ],
    'data': [
        'views/templates.xml',
        'views/payment_acquirer.xml',
        'views/sale_order.xml',
        'views/res_partner_view.xml',
        'wizard/add_wallet_wizard_view.xml',
        'security/res_groups.xml',
        'security/ir.model.access.csv',
    ],
}