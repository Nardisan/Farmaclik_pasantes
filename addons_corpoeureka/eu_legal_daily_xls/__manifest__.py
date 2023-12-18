# -*- coding: utf-8 -*-
{
    'name': "Diario Legal Excel",

    'description': """
        Este addon genera el diario legal en el excel
    """,

    'author': "CorpoEureka",
    'website': "http://Corpoeureka.com/",
    'company': 'CorpoEureka',
    'category': 'Employees',
    'version': '1.0',
    'depends': [
        'base',
        'account',
        'eu_legal_daily',
     ],

    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/report_views.xml',
        #'views/account_view.xml',
        #'views/templates.xml',
    ],
    "application": True,
    "installable": True,
}
