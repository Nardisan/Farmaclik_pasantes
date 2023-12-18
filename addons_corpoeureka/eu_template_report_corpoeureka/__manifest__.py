# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{   

    'name': 'Template report CorpoEureka',
    'version': '1.0',
    'author': 'CorpoEureka',
    'category': 'web',
    'summary': '',
    'description': '''
        El modulo añade un nuevo template de reportes
    ''',
    'depends': [
        'base',
        'web',
    ],
    'data': [
        'views/report_templates.xml',
        #'views/report_books.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'qweb': [],
}