# -*- coding: utf-8 -*-
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2020. All rights reserved.

{
    'name': 'Price Checker',
    'version': '14.0.0.5',
    'sequence': 1,
    'category': 'Warehouse',
    'summary': 'Price Checker Kiosk Mode',
    'author': 'Technaureus Info Solutions Pvt. Ltd.',
    'website': 'http://www.technaureus.com/',
    'price': 85,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'description': """
    Price Checker Kiosk Mode
        """,
    'depends': ['product'],
    'data': [
        'security/security.xml',
        'views/price_checker_kiosk_view.xml',
        'views/web_asset_backend_template.xml',
    ],
    'qweb': [
        "static/src/xml/*.xml",
    ],
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'auto_install': False,
    'application': True,
    'live_test_url': 'https://www.youtube.com/watch?v=fnSzjRjYyFw&feature=youtu.be'
}
