# -*- coding: utf-8 -*-
{
    'name': 'Sale Order - Cancel after expire date.',
    'version': '1.0',
    'author': 'GAMA Recursos Tecnologicos (PERU)',
    'website': 'https://www.recursostecnologicos.pe',
    'category': 'Accounting/Sales',
    'description': """
Sale Order - Cancel after expire date.
=======================
Allows auto cancellation of sale order that stay in quotation state after a time (draft and sent state). This time is configurable in Sales settings when this addon was installed.
""",
    'depends': ['base', 'website_sale', 'sale_management'],
    'data': [
        'views/ir_cron.xml',
        ],
    'demo': [
     ],
    'test': [],
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'auto_install': True,
    'support': 'info@recursostecnologicos.pe',
    'post_init_hook': 'post_init_check',
}