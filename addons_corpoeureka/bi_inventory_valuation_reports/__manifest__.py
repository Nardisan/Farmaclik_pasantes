# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Libro de Inventario (PDF/EXCEL) in odoo',
    'version': '13.0.0.6',
    'category': 'Warehouse',
    'summary': 'Libro de Inventario',
    'description': """
    Libro de Inventario
    """,
    'author': "Softw & Hardw Solutions SSH",
    'website': "https://solutionssh.com/",
    'depends': ['stock','sale','account','purchase','sale_stock'],
    'data': [
        
        'views/sales_daybook_report_product_category_wizard.xml',
        'views/report_pdf.xml',
        'views/inventory_valuation_detail_template.xml',
    ],
    'live_test_url':'https://youtu.be/Lpr2cqdzs_I',
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    "images":["static/description/Banner.png"],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

