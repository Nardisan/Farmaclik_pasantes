# -*- coding: utf-8 -*-

{
    # Module Information
    'name': 'Website Clear Cart',
    'category': 'Website',
    'summary': 'Clear all cart product by just one click.',
    'version': '14.0.0.2',
    "description": """
            Website Clear Cart, 
            Shop cart clear,
            Website Remove Products from the cart,
            Clear cart, 
            Remove option from the customize if you don't need,
        
    """,
    'license': 'OPL-1',    
    'depends': ['website_sale'],

    'data': [
        'templates/template.xml',
    ],

    #Odoo Store Specific
    'images': [
        'static/description/clear_cart.png',
    ],

    # Author
    'author': 'AV Technolabs',
    'website': 'http://avtechnolabs.com',
    'maintainer': 'AV Technolabs',

    # Technical
    'installable': True,
    'auto_install': False,
    'price': 0,
    'currency': 'EUR', 
}
