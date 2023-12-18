# -*- coding: utf-8 -*-
{
    'name': 'pos_reconcile_old_sessions',
    'version': '1.0',
    'category': 'Sales/Point of Sale',
    'summary': 'Concilia facturas de POS Order',
    'description': 'Concilia facturas de que no fueron cruzadas con sus repectivos pagos al contabilizar sesion de POS',
    'depends': ['point_of_sale', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/reconcile_wizard_view.xml',
        'wizard/productos_compra_venta_wizard.xml',
        'wizard/productos_valoracion_mercancia_vendida.xml',

    ],
}