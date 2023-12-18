
{
    "name": """POS: Mostrar Dualidad de moneda""",
    "summary": """Agrega el precio de otra moneda en los productos en POS""",
    "category": "Point Of Sale",
    "version": "14.0.1.0.0",
    "application": False,
    'author': 'CorpoEureka',
    'company': 'CorpoEureka',
    "depends": [
        "point_of_sale",
        "stock",
        'eu_multi_currency',
        
    ],
    "data": [
        "views/data.xml", 
        "views/views.xml"
    ],
    "qweb": [
        "static/src/xml/pos.xml"
    ],
    "auto_install": False,
    "installable": True,
}
