# -*- coding: utf-8 -*-
{
    'name': "user_actions_notifier",

    'summary': """
        Permite generar notificaciones de acciones realizadas por los usuarios cuando se crea, edita, imprime
         o elimina un registro.
        """,

    'description': """
        Permite generar notificaciones de acciones realizadas por los usuarios cuando se crea, edita, imprime
         o elimina un registro. Cuenta con partes vistas: 
         - user_action: muestra las acciones que se pueden registrar.
         - monitor: posee registros de las reglas (usuarios y acciones) que se van a monitorear.
         - notifier: muestra las acciones realizadas por los usuarios monitoreados.
         
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        # demo data for user_actions_notifier.user_action
        'data/actions-demo.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
