# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from math import copysign

class CrossoveredBudget(models.Model):
    _inherit = 'crossovered.budget'

    tasa_presu = fields.Float(string="Tasa del Presupuesto",compute="_compute_tasa_presu",store=True,readonly=False)

    @api.depends('company_id')
    def _compute_tasa_presu(self):
      for record in self:
        record.tasa_presu = record.env.company.currency_id.parent_id._convert(1, record.env.company.currency_id, record.company_id or self.env.company, fields.date.today())

class CrossoveredBudgetLine(models.Model):
    _inherit = 'crossovered.budget.lines'
    restante_amount = fields.Float(string="Importe Restante",compute="_compute_restante_amount")

    @api.depends('planned_amount','practical_amount')
    def _compute_restante_amount(self):
        for rec in self:
            rec.restante_amount = 0.0
            if rec.planned_amount and rec.practical_amount:
                rec.restante_amount = rec.planned_amount - rec.practical_amount
    currency_id_dif = fields.Many2one(related="currency_id.parent_id",
        string="Divisa de Referencia",)
    practical_amount_usd = fields.Monetary(
        compute='_compute_practical_amount_usd', string='Importe Real $')
    planned_amount_usd = fields.Monetary(
        'Importe Previsto $', compute='_compute_planned_amount_usd',store=True,readonly=True)

    def _compute_practical_amount_usd(self):
        for line in self:
            acc_ids = line.general_budget_id.account_ids.ids
            date_to = line.date_to
            date_from = line.date_from
            if line.analytic_account_id.id:
                analytic_line_obj = self.env['account.analytic.line']
                domain = [('account_id', '=', line.analytic_account_id.id),
                          ('date', '>=', date_from),
                          ('date', '<=', date_to),
                          ]
                if acc_ids:
                    domain += [('general_account_id', 'in', acc_ids)]

                where_query = analytic_line_obj._where_calc(domain)
                analytic_line_obj._apply_ir_rules(where_query, 'read')
                from_clause, where_clause, where_clause_params = where_query.get_sql()
                select = "SELECT SUM(amount_usd) from " + from_clause + " where " + where_clause

            else:
                aml_obj = self.env['account.move.line']
                domain = [('account_id', 'in',
                           line.general_budget_id.account_ids.ids),
                          ('date', '>=', date_from),
                          ('date', '<=', date_to),
                          ('move_id.state', '=', 'posted')
                          ]
                where_query = aml_obj._where_calc(domain)
                aml_obj._apply_ir_rules(where_query, 'read')
                from_clause, where_clause, where_clause_params = where_query.get_sql()
                select = "SELECT sum(credit_usd)-sum(debit_usd) from " + from_clause + " where " + where_clause

            self.env.cr.execute(select, where_clause_params)
            line.practical_amount_usd = self.env.cr.fetchone()[0] or 0.0

    @api.depends('planned_amount','currency_id_dif','currency_id','company_id')
    def _compute_planned_amount_usd(self):
      for record in self:
        record.planned_amount_usd = record.planned_amount / record.crossovered_budget_id.tasa_presu