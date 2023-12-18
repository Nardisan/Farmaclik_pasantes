# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Account Small Report",
    'version': '13.1',
    'category' : 'account',
    'license': 'Other proprietary',
    'summary': """Small Account Report (80width).""",
    'author': "Corpo Eureka C.A - Development Team",
    'website': "http://www.corpoeureka.com",
    'description': """

    """,
    'depends': [
                'base',
                'account',
                ],
    'data':[
       'report/template.xml',
       'report/report_account.xml',
       'views/account_move_view.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
