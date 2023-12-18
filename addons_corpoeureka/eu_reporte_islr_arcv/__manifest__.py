{
	'name':'Reporte ISLR AR-CV',
	'descripion':'Modulo para generar reporte Impuesto Sobre la Renta por Conceptos',
	'data':[
		'security/ir.model.access.csv',
		'views/islr_arcv_wizard_view.xml',
		'reports/islr_arcv_report.xml',
		'reports/islr_arcv_templates.xml',
	],
	'depends':[
		'base',
		'account',
		'l10n_ve_retencion_islr',
		'l10n_ve_fiscal_requirements',
	]
}