# -*- coding: utf-8 -*-
from odoo import models, fields, api
 
class AccountAccountTemplate(models.Model):
    _inherit = "account.account.template"
    
    parent_id = fields.Many2one('account.account.template','Parent Account', ondelete="set null")
    
       
class AccountAccount(models.Model):
    _inherit = "account.account"

    parent_id = fields.Many2one('account.account','Parent Account', ondelete="set null")
    
    @api.depends('move_line_ids','move_line_ids.amount_currency','move_line_ids.debit','move_line_ids.credit')
    def compute_values(self):
        for account in self:
            sub_accounts = self.with_context({'show_parent_account':True}).search([('id','child_of',[account.id])])
            balance = 0.0
            credit = 0.0
            debit = 0.0
            initial_balance = 0.0
            initial_deb = 0.0
            initial_cre = 0.0
            context = self._context.copy()
            context.update({'account_ids':sub_accounts})
            tables, where_clause, where_params = self.env['account.move.line'].with_context(context)._query_get()
            query1 = 'SELECT account_move_line.debit,account_move_line.credit FROM ' + tables + 'WHERE' + where_clause 
            self.env.cr.execute(query1,tuple(where_params))
            for deb,cre in self.env.cr.fetchall():
                balance += deb - cre
                credit += cre
                debit += deb
            account.balance = balance
            account.credit = credit
            account.debit = debit
            if context.get('show_initial_balance'):
                context.update({'initial_bal': True})
                tables, where_clause, where_params = self.env['account.move.line'].with_context(context)._query_get()
                query2 = 'SELECT account_move_line.debit,account_move_line.credit FROM ' + tables + 'WHERE' + where_clause 
                self.env.cr.execute(query2,tuple(where_params))
                for deb,cre in self.env.cr.fetchall():
                    initial_cre += cre
                    initial_deb += deb
                initial_balance += initial_deb - initial_cre
                account.initial_balance = initial_balance
            else:
                account.initial_balance = 0
    move_line_ids = fields.One2many('account.move.line','account_id','Journal Entry Lines')
    balance = fields.Float(compute="compute_values", digits=(16, 4), string='Balance')
    credit = fields.Float(compute="compute_values", digits=(16, 4), string='Credit')
    debit = fields.Float(compute="compute_values", digits=(16, 4), string='Debit')
    parent_id = fields.Many2one('account.account','Parent Account', ondelete="set null")
    child_ids = fields.One2many('account.account','parent_id', 'Child Accounts')
    parent_path = fields.Char(index=True)
    initial_balance = fields.Float(compute="compute_values", digits=(16, 4), string='Initial Balance')
    
    
    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = 'code, name'
    _order = 'code, id'
    
