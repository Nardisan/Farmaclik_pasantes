# -*- coding: utf-8 -*-
{
    'name': "Daily Legal Report ",

    'summary': """
        Daily Legal Report for account module""",

    'description': """
        This app helps you to print the Daily Legal Report .
    """,

    'author': "CorpoEureka",
    'website': "http://Corpoeureka.com/",
    'company': 'CorpoEureka',
    'category': 'Employees',
    'version': '13.0.1',
    'depends': [
        'base',
        'account',
     ],

    # always loaded
    'data': [
        'views/account_view.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/report_views.xml',
        'security/ir.model.access.csv',
    ],
    "application": True,
    "installable": True,
}
