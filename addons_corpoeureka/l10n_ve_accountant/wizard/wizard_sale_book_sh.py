# -*- coding: utf-8 -*-
from datetime import datetime
from datetime import date

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError

class SaleBook(models.TransientModel):
    _name = 'wizard.book.sale'
    _description = 'Libro de ventas'

    account_ids = fields.Many2many('account.account',
                                   'account_report_sales_account_rel',
                                   'report_id', 'account_id',
                                   'Accounts')
    company_id = fields.Many2one('res.company', string='Company',
                                 readonly=True,
                                 default=lambda self: self.env.user.company_id)
    display_account = fields.Selection(
        [('all', 'All'), ('movement', 'With movements'),
         ('not_zero', 'With balance is not equal to 0')],
        string='Display Accounts', required=True, default='movement')
    date_to = fields.Date(string='End Date', default=date.today())
    date_from = fields.Date(string='Start Date', default=date.today())
    journal_ids = fields.Many2many('account.journal', string='Journals',
                                   required=True,
                                   default=lambda self: self.env[
                                       'account.journal'].search([('type', '=', 'sale')]))
    #def _domain_branch_ids(self):
    #    return [('id','in',(self.env.user.branch_ids.ids))]
    #branch_ids = fields.Many2many('res.branch', string='Sucursales',
    #                               required=True,
    #                               default=lambda self: self.env.user.branch_ids,domain=_domain_branch_ids)

    target_move = fields.Selection([('posted', 'All Posted Entries'),
                                    ('all', 'All Entries')], string='Target Moves', required=True,
                                   default='posted')
    sortby = fields.Selection(
        [('sort_date', 'Date'), ('sort_journal_partner', 'Journal & Partner')],
        string='Sort by',
        required=True, default='sort_date')

    currency_id = fields.Many2one(comodel_name='res.currency', string="Currency", default=lambda self: self.env.company.currency_id)
    in_bs = fields.Boolean(string="Mostrar en Bs",default=True)
    def _build_contexts(self, data):
        results = {}
        results['journal_ids'] = 'journal_ids' in data['form'] and data['form']['journal_ids'] or False
        #results['branch_ids'] = 'branch_ids' in data['form'] and data['form']['branch_ids'] or False
        results['state'] = 'target_move' in data['form'] and data['form']['target_move'] or ''
        results['date_from'] = data['form']['date_from'] or False
        results['date_to'] = data['form']['date_to'] or False
        results['strict_range'] = True if results['date_from'] else False
        results['currency_id'] = data['form']['currency_id'] or False
        results['in_bs'] = data['form']['in_bs'] or False
        return results


    def check_reports(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = \
        self.read(['date_from', 'date_to', 'journal_ids','display_account', 'target_move','account_ids','sortby','currency_id','in_bs'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context,lang=self.env.context.get('lang') or 'es_ES')
        return self.env.ref('l10n_ve_accountant.sales_book').report_action(self,data=data)

    @api.constrains('date_from', 'date_to')
    def _check_date(self):
        '''
        This method validated that the final date is not less than the initial date
        :return:
        '''
        if self.date_to < self.date_from:
            raise UserError(_("The end date cannot be less than the start date "))
