
{
    "name" : "POS Lot Auto Selection depend on expiry date",
    "description": """Using this module to auto select LOT/Serial in POS sorted by expiry date""",
    'summary': 'Using this module to auto select LOT/Serial in POS sorted by expiry date.',
    'category': 'Point of Sale',
    'version': '14.0',
    'author': 'Ahmed Elmahdi',
    'price': 62,
    'currency': 'EUR',
    "depends" : ['point_of_sale', 'product_expiry'],
    "data": [
        'views/pos.xml',
    ],
    'license': 'LGPL-3',
    'qweb': ['static/src/xml/pos.xml'],
    'installable': True,
    'auto_install': False,
    'images':['static/description/image.png'],
    'live_test_url':'https://youtu.be/__pwDKGwMwc',
}
