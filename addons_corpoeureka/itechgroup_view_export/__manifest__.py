{
    "name": "Export views to EXCEL | Export views to PDF | Export views to CSV",
    "summary": "This module helps users to export Odoo list views in PDF/EXCEL/CSV format",
    "description": """
        This module helps users to export Odoo list views in PDF/EXCEL/CSV format
        PDF
        pdf
        EXCEL
        CSV
        export
        Export
        List views
        views
        print
        Print
        print header
        tree/list views
        select the records in list view to export it
    """,
    "category": "Extra Tools",
    "version": "10.0.0.1",
    "sequence": 3,
    "author": "Itechgroup",
    "depends": ['base', 'web'],
    "live_test_url": "http://ec2-18-191-155-154.us-east-2.compute.amazonaws.com:8069/",
    "data": [
        "security/view_export_security.xml",
        "views/assets.xml",
        "views/company_view.xml"
    ],
    "qweb": [
        'static/src/xml/widget.xml'
    ],
    "license": "OPL-1",
    "images": ['static/description/banner.gif'],
    "price": '49.99',
    "currency": "EUR",
    "installable": True,
    "application": True
}
