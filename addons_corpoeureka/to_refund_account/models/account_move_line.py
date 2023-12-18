from odoo import models

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def _get_computed_account(self):
        fiscal_position = self.move_id.fiscal_position_id
        accounts = self.product_id.product_tmpl_id.get_product_accounts(fiscal_position)
        type = self.move_id.move_type
        if type == 'out_refund' and accounts['income_refund']:
            return accounts['income_refund']
        elif type == 'in_refund' and accounts['expense_refund']:
            return accounts['expense_refund']
        
        return super(AccountMoveLine, self)._get_computed_account()