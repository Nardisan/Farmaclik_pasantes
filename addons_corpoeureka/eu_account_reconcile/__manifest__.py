# -*- coding: utf-8 -*-
{
    'name': 'Accounting Reconcile CE',
    'version': '14.0.1',
    'license': 'OPL-1',
    'category': 'Accounting/Accounting',
    'summary': 'Add Reconcile Freatures to CE Account',
    'description': """
""",
    'depends': [
        'account', 
        'web'
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/eu_account_reconcile_security.xml',
        'views/eu_account_reconcile_templates.xml',
        'views/account_account_views.xml',
        'views/account_bank_statement_views.xml',
        'views/account_fiscal_year_view.xml',
        'views/account_journal_dashboard_views.xml',
        'views/account_move_views.xml',
        'views/account_payment_views.xml',
        'views/eu_account_reconcile_menuitems.xml',
        'views/res_config_settings_views.xml',
        'views/product_views.xml',
        'wizard/account_change_lock_date.xml',
        'wizard/reconcile_model_wizard.xml',
    ],
    'qweb': [
        "static/src/xml/account_reconciliation.xml",
    ],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
