from odoo import models, api

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    def _reverse_moves(self, default_values_list=None, cancel=False):
        res = super(AccountMove, self)._reverse_moves(default_values_list, cancel)
        move_type = self.move_type
        
        for move in res:
            move_lines = move.mapped('line_ids')
            for line in move_lines:
                if not line.product_id:
                    continue
                else:
                    accounts = line.product_id.product_tmpl_id._get_product_accounts()
                    income_refund_acc = accounts['income_refund']
                    expense_refund_acc = accounts['expense_refund']

                if  move_type == 'out_invoice' and income_refund_acc:
                    line.account_id = income_refund_acc.id
                elif move_type == 'in_invoice' and expense_refund_acc:
                    line.account_id = expense_refund_acc.id
        return res