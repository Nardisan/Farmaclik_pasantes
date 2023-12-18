# encoding: UTF-8
# Create:  Corpoeureka** 23/03/2021 ** Team Desarrollo Jose Mazzei(@josemazzeip) - Elio Meza (eliomeza1@gmail.com)  **
# type of the change:  Creacion
# Comments: Creacion del modulo de eu_withholding_itf
#Contiene un diccionario en Python para agregar las descripciones del módulo, como autor, versión, etc.
{
    'name': 'Impuesto a las Grandes Transacciones Financieras',
    'version':'1.0',
    'category': 'Account',
    'summary':'Automatic ITF Withhold',
    'description': '''\
Calculate automatic itf withholding
===========================
Creador: Elio Meza
Colaborador: Jose Mazzei

V1.0
Calculate automatic itf withholding
''',
    'author': 'Corpoeureka',
    'website': 'https://www.corpoeureka.com/web/soluciones/odoo',
    #data, es una lista donde se agregan todas las vistas del módulo, es decir los archivos.xml y archivos.csv.
    'data': [

             'security/ir.model.access.csv',
             'view/res_company_view.xml',
             'view/account_journal_view.xml',
             'view/account_payment_view.xml',
             #'view/advance_payment_view.xml',
             'view/wizard_igtf_report.xml',
             'reports/igtf_template.xml',

            ],
    #depends,  es una lista donde se agregan los módulos que deberían estar instalados (Módulos dependencia) para que el modulo pueda ser instalado en Odoo.
    'depends': ['base','account','sr_manual_currency_exchange_rate', 'locv_account_advance_payment'],
    'js': [],
    'css': [],
    'qweb' : [],
    'images': ['static/description/image/icon_eu.png'],
    #'installable': True,
    #'auto_install': False,
    'application': True,
}
