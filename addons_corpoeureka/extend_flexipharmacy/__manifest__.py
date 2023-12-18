{
    'name': "POS Pharmacy EXTEND",
    'summary': "POS Pharmacy extend",
    'description': """POS Pharmacy C
    -Comisiones de medicos
    """,
    'category': 'Point of Sale',
    'author': 'FARMACIA_PP',
    'depends': ['flexipharmacy', 'point_of_sale','pos_report_session_summary'],
   
    'data': [
        'views/pos_commission_payment_view.xml',        
        'views/res_partner_view.xml'
    ],
    
    'qweb': [
        "./static/xml/index.xml"
    ],
}
