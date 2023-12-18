from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'



    property_account_income_refund_id = fields.Many2one('account.account', string='Income Refund Account', company_dependent=True,
                                                       help="This account, instead of the original Income Account, will be used for customer invoice refund, if set."
                                                       " I.e. When validating customer invoice refund, the amount will be debited into this account."
                                                       " You can leave this field empty to have the Income Account debited instead.")

    property_account_expense_refund_id = fields.Many2one('account.account', string='Expense Refund Account', company_dependent=True,
                                                       help="This account, instead of the original Expense Account, will be used for vendor bill refund, if set."
                                                       " I.e. When validating vendor bill refund, the amount will be credited into this account."
                                                       " You can leave this field empty to have the Expense Account credited instead.")

    def _get_product_accounts(self):
        accounts = super(ProductTemplate, self)._get_product_accounts()
        accounts['income_refund'] = self.property_account_income_refund_id or self.categ_id.property_account_income_refund_categ_id
        accounts['expense_refund'] = self.property_account_expense_refund_id or self.categ_id.property_account_expense_refund_categ_id
        return accounts
