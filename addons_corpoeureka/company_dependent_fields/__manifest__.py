# -*- coding: utf-8 -*-
{
	'name': "Company Dependent Fields",
	'summary': """Company Dependent Fields""",
	'description': """Make certain fields dependent on the company""",
	'author': "leonel.loyo93@gmail.com",
	'category': 'Product',
	'version': '1.0',
	'depends': ['product','contacts', 'sale_management'],
	'data': [
      './views/res_partner_bank.xml',
      './reports/productos_formato_etiqueta.xml',
      './reports/orden_de_venta_talonario.xml'
	],
	'license': 'LGPL-3'
}
