# -*- coding: utf-8 -*-
{
    'name': 'Odoo Vendor Portal: Sign Purchase RFQ Online',
    'version': '13.0.1.0',
    'category': 'Purchases',
    'description': """
Odoo vendor portal: Send your RFQ to your vendor online, they input the price and sign online also
    """,
    'summary': '''
    Odoo vendor portal: Send your RFQ to your vendor online, they input the price and sign online also
    ''',
    'live_test_url': 'https://demo13.domiup.com',
    'author': 'Domiup',
    'price': 30,
    'currency': 'EUR',
    'license': 'OPL-1',
    'support': 'domiup.contact@gmail.com',
    'website': 'https://youtu.be/4LcCtc3mmxU',
    'depends': [
        'purchase',
    ],
    'data': [
        'views/purchase_order_views.xml',
        'views/purchase_portal_templates.xml',
    ],

    'test': [],
    'demo': [],
    'images': ['static/description/banner.gif'],
    'installable': True,
    'active': False,
    'application': True,
}
