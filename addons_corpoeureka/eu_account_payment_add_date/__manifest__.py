# -*- coding: utf-8 -*-
{
    'name': "Add Payment Date ",

    'summary': """
       Payment Module, Add Two Dates""",

    'description': """
        
            """,

    'author': "CorpoEureka",
    'website': "http://CorpoEureka.com/",
    'company': 'Corporación Eureka',
    'category': 'Accounting',
    'version': '14.0.0.1',
    'depends': ['base', 'account','eu_template_report_corpoeureka'],

    # always loaded
    'data': [
        'views/views.xml',
        'views/report_payment_receipt_templates.xml',
        'security/ir.model.access.csv',
        'data/account_payment_motivo.xml',
    ],
    "application": True,
    "installable": True,
}
