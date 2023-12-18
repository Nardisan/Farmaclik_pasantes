{    
    'name': 'Reporte de Presupuesto',
    'version': '1.0',
    'category': 'Presupuesto',
    'author': 'CorpoEureka',
    'website': 'http://www.corpoeureka.com',
    'description': """
       Reporte de presupuesto
    """,
    'depends':[
    	'base',
        'account_budget',
    ],
    'data':[
        'views/account_budget_templates.xml',
    	'views/account_budget_views_main.xml',
    ],
    'installable': True,
}