# -*- coding: utf-8 -*-

from collections import defaultdict
from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.exceptions import ValidationError

class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.depends('line_ids.amount_usd',)
    def _compute_debit_credit_balance_usd(self):
        Curr = self.env['res.currency']
        analytic_line_obj = self.env['account.analytic.line']
        domain = [('account_id', 'in', self.ids)]
        if self._context.get('from_date', False):
            domain.append(('date', '>=', self._context['from_date']))
        if self._context.get('to_date', False):
            domain.append(('date', '<=', self._context['to_date']))
        if self._context.get('tag_ids'):
            tag_domain = expression.OR([[('tag_ids', 'in', [tag])] for tag in self._context['tag_ids']])
            domain = expression.AND([domain, tag_domain])
        if self._context.get('company_ids'):
            domain.append(('company_id', 'in', self._context['company_ids']))


        user_currency = self.env.company.currency_id
        credit_groups = analytic_line_obj.read_group(
            domain=domain + [('amount_usd', '>=', 0.0)],
            fields=['account_id', 'currency_id', 'amount_usd'],
            groupby=['account_id', 'currency_id'],
            lazy=False,
        )
        data_credit = defaultdict(float)
        for l in credit_groups:
            data_credit[l['account_id'][0]] += Curr.browse(l['currency_id'][0])._convert(
                l['amount_usd'], user_currency, self.env.company, fields.Date.today())

        debit_groups = analytic_line_obj.read_group(
            domain=domain + [('amount_usd', '<', 0.0)],
            fields=['account_id', 'currency_id', 'amount_usd'],
            groupby=['account_id', 'currency_id'],
            lazy=False,
        )
        data_debit = defaultdict(float)
        for l in debit_groups:
            data_debit[l['account_id'][0]] += Curr.browse(l['currency_id'][0])._convert(
                l['amount_usd'], user_currency, self.env.company, fields.Date.today())


        for account in self:
            account.debit_usd = abs(data_debit.get(account.id, 0.0))
            account.credit_usd = data_credit.get(account.id, 0.0)
            account.balance_usd = account.credit_usd - account.debit_usd

    
    
    balance_usd = fields.Monetary(compute='_compute_debit_credit_balance_usd', string='Balance USD')
    debit_usd = fields.Monetary(compute='_compute_debit_credit_balance_usd', string='Debe USD')
    credit_usd = fields.Monetary(compute='_compute_debit_credit_balance_usd', string='Haber USD')
    currency_id_dif = fields.Many2one("res.currency", 
        string="Referencia en Divisa",
        default=lambda self: self.env['res.currency'].search([('name', '=', 'USD')], limit=1),)
