{
    'name': 'calculo_min_max_farmacia',
    'version': '1.0',
    'category': 'Warehouse Management',
    'summary': 'Establece los mín y máx por producto de cada almacén',
    'description': 'Establece los mín y máx por producto de cada almacén',
    'depends': ['point_of_sale', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/min_max_farmacia.xml',
        'views/lista_productos_min_max.xml',
        'views/producto_rotacion.xml',
        'wizard/calculo_rotacion_producto.xml',

    ],
}