# encoding: UTF-8
{
    'name': 'Account Advanced Payment',
    'version':'13.0',
    'category': 'account',
    'summary':'Registro de Anticipo para proveedores y clientes',
    'description': '''
Registro de Anticipos para ser aplicados a las facturas y notas de créditos
de clientes y proveedores.
============================
''',
    'author': 'Venezuela',
    'website': '',
    'data': [
             'security/security.xml',
             'security/ir.model.access.csv',
             'view/account_advance_payment.xml',
             'data/sequence_advance_data.xml',
             'view/res_partner_view.xml',
             'view/account_move_view.xml',
             'security/multi_company_rules.xml',
             'report/locv_template.xml',
    ],
    'depends': ['base','web','mail','account','eu_multi_currency'],
    'application': True,
}
