{
    'name': 'POS Manager Validation (User)',
    'version': '14.0.1.2',
    'summary': """   """,
    'description': """
Solicita validaciones por pin
""",
    'category': 'Point of Sale',
    'author': 'Sinergia',
    'website': 'www.sinergia-e.com',
    'depends': [
        'point_of_sale',
    ],
    'data': [
        'views/pos_manager_validation_templates.xml',
        'views/res_users_views.xml',
        'views/pos_config_views.xml',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'images': ['static/description/pos_ui_validate.png'],
    'price': 69.99,
    'currency': 'EUR',
    'license': 'OPL-1',
}
