# -*- coding: utf-8 -*-

{
    'name': 'Flour Extraction',
    'version': '1.0',
    'category': 'Mrp',
    'author': 'CorpoEureka - Anderson Rodriguez',
    'website': 'http://www.corpoeureka.com', 
    'description': """

    """,
    'summary':" ",
    'depends': [
        'mrp',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/mrp_bom_view.xml',
        'views/mrp_production_view.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': True,
}
