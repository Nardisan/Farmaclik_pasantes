# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Facturación, Multiseries",
    'version': '1.0',
    'category' : 'Facturación - Accounting',
    'license': 'Other proprietary',
    'summary': """Esta aplicación permite diversas secuencias para Facturación.""",
    'author': "Corpo Eureka C.A - Jose Mazzei.",
    'website': "http://www.corpoeureka.com",
    'description': """
Esta APP permite Agregar una segunda Secuencia a Facturación por Compañía, de esta manera
se puede facturar diferentes series.
    """,
    'depends': [
                'base',
                'account',
                ],
    'data':[
        'data/account_serie_sequence.xml',
        'views/company_view.xml',
        'views/account_move_view.xml',
        'views/account_journal_view.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
