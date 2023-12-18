# -*- coding: utf-8 -*-
#COdigo  creado y modificado por Elio Meza 
#eliomeza1@gmail.com


{
        'name': 'Municipal Taxes for Venezuela Localization',
        'version': '0.1',
        'author': 'CorpoEureka',
        'description': 'Municipal Taxes',
        'category': 'Accounting/Accounting',
        'website': '',
        'images': [],
        'depends': [
            'account',
            'mail',
            #'account_accountant',
            'base',
            'l10n_ve_fiscal_requirements',
            'l10n_ve_dpt',
            'eu_template_report_corpoeureka',
            ],
        'data': [
            'security/ir.model.access.csv',
            'security/multi_company.xml',
            'data/seq_muni_tax_data.xml',
            'data/period.month.csv',
            'data/period.year.csv',
            'views/res_config_view.xml',
            'views/account_move_views.xml',
            'views/res_partner_views.xml',
            'views/municipality_tax_views.xml',
            'views/tax_municipal_declaration_view.xml',
            'report/report_municipal_tax.xml',
            'report/iae_report.xml',
            'report/iae_template.xml',
            'data/muni_mail_template_data.xml',
            'views/res_company_views.xml',
            'views/menu_item.xml',
            'views/iae_wizard_view.xml',
            'wizard/wizard_payment_retention.xml',
            #'data/muni.wh.concept.csv',
            ],
        'installable': True,
        'application': True,
        'auto_install': False,
        
        }
