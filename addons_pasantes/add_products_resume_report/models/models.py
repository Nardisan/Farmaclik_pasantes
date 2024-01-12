# -*- coding: utf-8 -*-

from odoo import models, fields


class products_resume_report_wizard(models.TransientModel):
    _name = 'add_products_resume_report.resume_report'
    _description = 'add_products_resume_report.add_products_resume_report'

    applied_on = fields.Selection([
        ('todos', 'Todos'),
        ('categoria', 'Categoria'),
        ('productos', 'Productos')
    ],
        string="Filtrar por",
        default='todos', required=True,
        help='Pricelist Item applicable on selected option')
    products_id = fields.Many2one(
        'product.template', 'Products', ondelete='cascade', check_company=True,
        help="Specify a product if this rule only applies to one product. Keep empty otherwise.")
    categ_id = fields.Many2one(
        'product.category', 'Product Category', ondelete='cascade',
        help="Specify a product category if this rule only applies to products belonging to this category or its "
             "children categories. Keep empty otherwise.")

    def print_report(self, cr, uid, ids, context=None):
        datas = {}
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        datas = {
            'ids': [],
            'model': 'object.object',
            'form': data
        }
        return {'type': 'ir.actions.report.xml', 'report_name': 'your_report_name', 'datas': datas}
