# -*- coding: utf-8 -*-

from datetime import date
from odoo import _, api, fields, models
from odoo.exceptions import UserError

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    transfer_account_id = fields.Many2one('account.account', string="Transfer Account",
        related='company_id.transfer_account_id', readonly=False,
        domain=lambda self: [('reconcile', '=', True), ('user_type_id.id', '=', self.env.ref('account.data_account_type_current_assets').id)],
        help="Intermediary account used when moving money from a liquidity account to another")


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def unlink(self):
        for rec in self:
            if rec.name != '/':
                raise UserError('No puedes borrar un pago que ha sido publicado al menos una vez')
        return super(AccountPayment, self).unlink() 
# class AccountBankStatement(models.Model):
#     _inherit = 'account.bank.statement'

#     def action_bank_reconcile_bank_statements(self):
#         self.ensure_one()
#         limit = int(self.env["ir.config_parameter"].sudo().get_param("account.reconcile.batch", 1000))
#         bank_stmt_lines = self.env['account.bank.statement.line'].search([
#             ('statement_id', 'in', self.ids),
#             ('is_reconciled', '=', False),
#         ], limit=limit)
#         return {
#             'type': 'ir.actions.client',
#             'tag': 'bank_statement_reconciliation_view',
#             'context': {'statement_line_ids': bank_stmt_lines.ids, 'company_ids': self.mapped('company_id').ids},
#         }

# class AccountAccount(models.Model):
#     _inherit = "account.account"

#     def action_open_reconcile(self):
#         self.ensure_one()
#         # Open reconciliation view for this account
#         action_context = {'show_mode_selector': False, 'mode': 'accounts', 'account_ids': [self.id,]}
#         return {
#             'type': 'ir.actions.client',
#             'tag': 'manual_reconciliation_view',
#             'context': action_context,
#         }
