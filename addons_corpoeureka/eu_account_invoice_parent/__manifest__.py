# -*- coding: utf-8 -*-
#Colaboradores (Team Desarrollo Corpoeureka)
#Elio Meza eliomeza1@gmail.com 
#Jose Mazzei  @josemazzeip
{
    'name': "Account Parent in Invoice",

    'summary': """
        Account Parent in Invoice for Credit Invoice""",

    'description': """
        This app helps you to create a automatic parent id when you create a Credit note.
        Esta aplicación le ayuda a crear una identificación  padre automática cuando crea una nota de crédito.
    """,

    'author': "CorpoEureka",
    'website': "corpoeureka.com",
    'company': 'Corporación Eureka',
    'category': 'Account',
    'version': '14.0.1',
    'depends': ['base', 'account'],
    # always loaded
    'data': [
        'views/account_move_view.xml',
        'security/ir.model.access.csv',
    ],
    "application": True,
    "installable": True,
}
