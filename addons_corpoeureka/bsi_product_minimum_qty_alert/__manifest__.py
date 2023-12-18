# -*- coding: utf-8 -*-

{
    'name': "Minimum Product Quantity Alert",
    'author': 'Botspot Infoware Pvt. Ltd.',
    'category': 'Inventory',
    'summary': """This app is to remind a quantity that is in fact less than Avilable Quantity and it will show you the product in red lines. And the Product's quantity of that can be update.
The main advantage of our app is that" the Available Quantity which is less than the Minimum Quantity, About it users can see in the mail all the information.""",
    'website': 'http://www.botspotinfoware.com',
    'company': 'Botspot Infoware Pvt. Ltd.',
    'maintainer': 'Botspot Infoware Pvt. Ltd.',
    'description': """This app is to remind a quantity that is in fact less than Avilable Quantity and it will show you the product in red lines. And the Product's quantity of that can be update.
The main advantage of our app is that" the Available Quantity which is less than the Minimum Quantity, About it users can see in the mail all the information.""",
    'version': '14.0.1.0',
    'depends': ['base', 'sale_management', 'stock'],
    'data': [
             "security/ir.model.access.csv",
             "data/cron.xml",
             "views/product_product_view.xml",
             ],
    "images": ['static/description/Banner.gif'],
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
