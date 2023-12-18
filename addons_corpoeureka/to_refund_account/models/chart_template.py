# -*- coding: utf-8 -*-
from odoo import models, fields


class AccountChartTemplate(models.Model):
    _inherit = 'account.chart.template'

    property_account_income_refund_categ_id = fields.Many2one('account.account.template', string='Income Refund Account on Product Category')
    property_account_expense_refund_categ_id = fields.Many2one('account.account.template', string='Expense Refund Account on Product Category')    
    property_account_income_refund_id = fields.Many2one('account.account.template', string='Income Refund Account on Product Template')
    property_account_expense_refund_id = fields.Many2one('account.account.template', string='Expense Refund Account on Product Template')
