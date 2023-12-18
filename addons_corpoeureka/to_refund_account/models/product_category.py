from odoo import models, fields

class ProductCategory(models.Model):
    _inherit = 'product.category'


    property_account_income_refund_categ_id = fields.Many2one('account.account', string='Income Refund Account', company_dependent=True,
                                                              help="This account, instead of the original Income Account, will be used for customer invoice refund, if set."
                                                              " I.e. When validating customer invoice refund, the amount will be debited into this account."
                                                              " You can leave this field empty to have the Income Account debited instead.")

    property_account_expense_refund_categ_id = fields.Many2one('account.account', string='Expense Refund Account', company_dependent=True,
                                                              help="This account, instead of the original Expense Account, will be used for vendor bill refund, if set."
                                                              " I.e. When validating vendor bill refund, the amount will be credited into this account."
                                                              " You can leave this field empty to have the Expense Account credited instead.")
