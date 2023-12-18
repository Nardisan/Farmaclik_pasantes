
{
    "name": """POS: Recibo en Bs (Compañía Dolar)""",
    "summary": """Muestra los precios del recibo en Bs, estando la Compañía en USD""",
    "category": "Point Of Sale",
    "version": "14.0.1.0.0",
    "application": False,
    'author': 'CorpoEureka',
    'company': 'CorpoEureka',
    "depends": [
        "pos_show_dual_currency",
        "point_of_sale",
    ],
    "data": [
    ],
    "qweb": [
        "static/src/xml/receipt.xml"
    ],
    "auto_install": False,
    "installable": True,
}
