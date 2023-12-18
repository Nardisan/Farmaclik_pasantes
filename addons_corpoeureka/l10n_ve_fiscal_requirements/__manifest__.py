# -*- coding: utf-8 -*-
{
    "name": "Requerimientos Fiscales Venezolanos",
    "version": "1.0",
    'author': 'Kiran Kantesariya',
    'skype': 'kiran.backup0412@gmail.com',
    "category": 'Localization',

    "depends": ["base","account", 'l10n_ve_dpt'],
    'data': [
        # ~ 'security/ir.model.access.csv',
        'views/partner_view.xml',
        'views/company_view.xml',
        'views/account_invoice_view.xml',
        'views/account_tax_view.xml',
       # 'views/pos_partner_view.xml',
        # ~ 'reports/fiscal_invoice.xml',
        # ~ 'reports/internal_layout_laws.xml',
    ],
    'qweb': ['static/src/xml/pos.xml'],
    "installable": True,
    "application": True,
    "auto_install": False,
}
