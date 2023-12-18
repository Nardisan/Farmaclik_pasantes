# -*- coding: utf-8 -*-
#################################################################################
# Author      : Kanak Infosystems LLP. (<https://www.kanakinfosystems.com/>)
# Copyright(c): 2012-Present Kanak Infosystems LLP.
# All Rights Reserved.
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://www.kanakinfosystems.com/license>
#################################################################################
{
    'name': 'Website Login',
    'version': '1.0',
    'description': 'Customised Website Login Page',
    'category': 'Website',
    'summary': 'Change the way Odoo website page looks , make it dynamic & appealing',
    'license': 'OPL-1',
    'author': 'Kanak Infosystems LLP.',
    'website': 'https://www.kanakinfosystems.com',
    'images': ['static/description/banner.jpg'],
    'depends': ['website', 'auth_oauth'],
    'data': [
        'data/auth_oauth_data.xml',
        'views/website_login_template.xml',
        'views/auth_facebook_view.xml',
    ],
    'sequence': 1,
    'installable': True,
    'auto_install': False,
    'application': False,
    'price': 20,
    'currency': 'EUR',
}
