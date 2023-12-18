# -*- coding: utf-8 -*-
{
    'name': "permitting_user",

    'description': """
       Permisologia de los usuarios 
       - usuario de caja solo visualiza su caja 
    """,

    'author': "FARMACIA_PP",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    #'category': '',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['flexipharmacy'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/pos_user_restrict_security.xml',
    ],
}