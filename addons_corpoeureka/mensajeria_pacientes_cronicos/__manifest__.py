{
    'name': 'mensajeria_pacientes_cronicos',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Gestión de mensajería SMS para pacientes crónicos',
    'description': 'Gestión de mensajería SMS para pacientes crónicos',
    'depends': ['point_of_sale', 'stock', 'contacts'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_template.xml',
        'views/res_config_settings.xml',
        'views/mensajeria_sms_pacientes_cronicos.xml'
    ],
}