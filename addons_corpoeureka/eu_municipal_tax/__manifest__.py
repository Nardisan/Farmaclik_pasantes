# -*- coding: utf-8 -*-
#Codigo Desarrollado y modificado por Elio Meza 
# eliomeza1@gmail.com 

{
    'name': 'Declaración Mensual de Ingresos',
    'version':'1.0',
    'category': 'Account',
    'author': 'CorpoEureka',
    'support': 'proyectos@corpoeureka.com',
    'website' : 'http://www.corpoeureka.com',
    'license' : 'OPL-1',
    'description': """
        Declaración mensual de ingreso sobre actividades economicas en el municipio   
    """,
    'depends':[
    'base',
    'sale_management',
    'account',
    'contacts',
    'municipality_tax',
    'eu_template_report_corpoeureka',
    ],
    'data':[
        #Permiso de Acceso
        'security/ir.model.access.csv',
        # Secuencias 
        'data/sequence.xml',
        # Multi Company
        'security/security_multi_company.xml',
        #wizard
        'wizard/payment_iae_wizard.xml',
        # Vistas Creadas y Heredadas
        'views/consolidate_tax_muni.xml',
        'views/menu_item.xml',
        'reports/tax_municipal_report.xml'
    ],
    'images': ['static/description/image/icon_eu.png'],
    'installable': True,
    'application': True
}
