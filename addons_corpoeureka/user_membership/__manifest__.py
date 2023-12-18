# -*- coding: utf-8 -*-
{
    'name': "Website Membership Program",

    'summary': """Enable extra membership features on your website""",

    'description': """
        This module gives you a flexibility to create memberships plan and their benefits for website customer. 
        Website Membership Program
        Membership Management in Odoo Website 
        Odoo Membership Management
        Membership-based services in Odoo
        Membership Management Software in Odoo
        Membership module for Odoo website users
        Module for membership management in Odoo
        Website Membership Module for Odoo
        How to manage recurring services bills in Odoo
        Membership Plans services
        Membership
        Odoo Membership
        manage membership products in Odoo
        Membership products
        Odoo Subscription Management
        Odoo Website Subscription management
        Odoo booking & reservation management
        Odoo appointment management
        Odoo website appointment management
    """,

    'author': "ErpMstar Solutions",
    'category': 'eCommerce',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'website_sale_delivery',
        'website_sale_wishlist',
        'theme_clarico_vega',
    ],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/views.xml',
        'wizard/wizard.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'live_test_url': "https://youtu.be/nAlegwhOgnQ",
    'price': 80,
    'currency': 'EUR',
}
