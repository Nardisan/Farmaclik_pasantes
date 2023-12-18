# -*- coding: utf-8 -*-
{
    'name': "Website MultiMoneda",
    'version': '1.0',
    'category' : 'web',
    'license': 'Other proprietary',
    'summary': """Esta aplicación permite visualizar otra moneda en la vista web.""",
    'author': "CorpoEureka",
    'website': "http://www.corpoeureka.com",
    'description': """
Esta APP permite visualizar y calcular otro campo Total en la vista Web
    """,
    'depends': [
                'sale',
                'sale_management',
                'product',
                'base',
                'website_sale',
                'eu_multi_currency',
                ],
    'data':[
       'views/assets.xml',
       'views/website_multi.xml',
    ],
    'installable' : True,
    'application' : False,
}
