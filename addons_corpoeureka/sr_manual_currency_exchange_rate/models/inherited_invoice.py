# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C) 2017-Today Sitaram
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

from odoo import models, fields, api
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    apply_manual_currency_exchange = fields.Boolean(string='Aplicar cambio de tasa manual')
    manual_currency_exchange_rate = fields.Float(string='Tipo de tasa manual', digits=(10,10),store=True,readonly=False,)#compute="_compute_manual_currency_exchange_rate")
    #manual_currency_exchange_rate_inverter = fields.Float(string='Tipo de tasa manual Inverter', digits=(20,16),default=0.0)
    active_manual_currency_rate = fields.Boolean('Activar Moneda manual', default=True)
    
    #def write(self,vals):
    #    result = super(AccountMove, self).write(vals)
    #    if self.manual_currency_exchange_rate_inverter and self.manual_currency_exchange_rate_inverter > 0:
    #        vals['manual_currency_exchange_rate'] = 1 / self.manual_currency_exchange_rate_inverter
    #    return result
    #@api.onchange('line_ids','invoice_line_ids')    
    #def onchange_invoice_ids(self):
    #    for lines in self.line_ids:
    #        res = lines._get_fields_onchange_subtotal_model(lines.price_subtotal,self.move_type,self.currency_id,self.company_id,self.invoice_date)
    #        lines.write({'amount_currency':res['amount_currency'],'debit':res['debit'],'credit':res['credit'],})

    #@api.onchange('manual_currency_exchange_rate_inverter')
    #def _onchange_manual_currency_rate_inverter(self):
    #    if self.manual_currency_exchange_rate_inverter > 0:
    #        self.manual_currency_exchange_rate = 1/self.manual_currency_exchange_rate_inverter 

    #@api.depends('manual_currency_exchange_rate_inverter')
    #def _compute_manual_currency_exchange_rate(self):
    #    if self.manual_currency_exchange_rate_inverter > 0:
    #        self.manual_currency_exchange_rate = 1 / self.manual_currency_exchange_rate_inverter 

    @api.onchange('manual_currency_exchange_rate', 'apply_manual_currency_exchange')
    def _onchange_manual_currency_rate(self):
        self._onchange_currency()

    @api.onchange('purchase_vendor_bill_id', 'purchase_id')
    def _onchange_purchase_auto_complete(self):
        ''' Load from either an old purchase order, either an old vendor bill.

        When setting a 'purchase.bill.union' in 'purchase_vendor_bill_id':
        * If it's a vendor bill, 'invoice_vendor_bill_id' is set and the loading is done by '_onchange_invoice_vendor_bill'.
        * If it's a purchase order, 'purchase_id' is set and this method will load lines.

        /!\ All this not-stored fields must be empty at the end of this function.
        '''
        if self.purchase_vendor_bill_id.vendor_bill_id:
            self.invoice_vendor_bill_id = self.purchase_vendor_bill_id.vendor_bill_id
            self._onchange_invoice_vendor_bill()
        elif self.purchase_vendor_bill_id.purchase_order_id:
            self.purchase_id = self.purchase_vendor_bill_id.purchase_order_id
        self.purchase_vendor_bill_id = False

        if not self.purchase_id:
            return

        # Copy partner.
        self.partner_id = self.purchase_id.partner_id
        self.fiscal_position_id = self.purchase_id.fiscal_position_id
        self.invoice_payment_term_id = self.purchase_id.payment_term_id
        self.currency_id = self.purchase_id.currency_id
        self.apply_manual_currency_exchange = self.purchase_id.apply_manual_currency_exchange
        self.manual_currency_exchange_rate = self.purchase_id.manual_currency_exchange_rate

        # Copy purchase lines.
        po_lines = self.purchase_id.order_line - self.line_ids.mapped('purchase_line_id')
        new_lines = self.env['account.move.line']
        for line in po_lines.filtered(lambda l: not l.display_type):
            new_line = new_lines.new(line._prepare_account_move_line(self))
            new_line.account_id = new_line._get_computed_account()
            new_line._onchange_price_subtotal()
            new_lines += new_line
        new_lines._onchange_mark_recompute_taxes()

        # Compute invoice_origin.
        origins = set(self.line_ids.mapped('purchase_line_id.order_id.name'))
        self.invoice_origin = ','.join(list(origins))

        # Compute ref.
        refs = set(self.line_ids.mapped('purchase_line_id.order_id.partner_ref'))
        refs = [ref for ref in refs if ref]
        self.ref = ','.join(refs)

        # Compute _invoice_payment_ref.
        if len(refs) == 1:
            self._invoice_payment_ref = refs[0]

        self.purchase_id = False
        self._onchange_currency()

    def _check_balanced(self):
        ''' Assert the move is fully balanced debit = credit.
        An error is raised if it's not the case.
        '''
        moves = self.filtered(lambda move: move.line_ids)
        if not moves:
            return

        # /!\ As this method is called in create / write, we can't make the assumption the computed stored fields
        # are already done. Then, this query MUST NOT depend of computed stored fields (e.g. balance).
        # It happens as the ORM makes the create with the 'no_recompute' statement.
        self.env['account.move.line'].flush(['debit', 'credit', 'move_id'])
        self.env['account.move'].flush(['journal_id'])
        self._cr.execute('''
               SELECT line.move_id, ROUND(SUM(debit - credit), currency.decimal_places)
               FROM account_move_line line
               JOIN account_move move ON move.id = line.move_id
               JOIN account_journal journal ON journal.id = move.journal_id
               JOIN res_company company ON company.id = journal.company_id
               JOIN res_currency currency ON currency.id = company.currency_id
               WHERE line.move_id IN %s
               GROUP BY line.move_id, currency.decimal_places
               HAVING ROUND(SUM(debit - credit), currency.decimal_places) != 0.0;
           ''', [tuple(self.ids)])

    
class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    active_manual_currency_rate = fields.Boolean('Activar Moneda manual', default=False,related='move_id.active_manual_currency_rate')
    apply_manual_currency_exchange = fields.Boolean(string='Aplicar cambio de tasa manual',related='move_id.apply_manual_currency_exchange')
    manual_currency_exchange_rate = fields.Float(string='Tipo de tasa manual', digits=(10,10),related="move_id.manual_currency_exchange_rate")
    #manual_currency_exchange_rate_inverter = fields.Float(string='Tipo de tasa manual Inverter', digits=(10,10),related="move_id.manual_currency_exchange_rate_inverter")

    @api.model
    def _get_fields_onchange_subtotal_model(self, price_subtotal, move_type, currency, company, date):
        ''' This method is used to recompute the values of 'amount_currency', 'debit', 'credit' due to a change made
        in some business fields (affecting the 'price_subtotal' field).

        :param price_subtotal:  The untaxed amount.
        :param move_type:       The type of the move.
        :param currency:        The line's currency.
        :param company:         The move's company.
        :param date:            The move's date.
        :return:                A dictionary containing 'debit', 'credit', 'amount_currency'.
        '''
        balance = 0.0
        if move_type in self.move_id.get_outbound_types():
            sign = 1
        elif move_type in self.move_id.get_inbound_types():
            sign = -1
        else:
            sign = 1
        price_subtotal *= sign
        if currency and currency != company.currency_id:
            # Multi-currencies.
            if self.move_id.manual_currency_exchange_rate != 0:
                balance = price_subtotal*self.move_id.manual_currency_exchange_rate
            
            return {
                'amount_currency': price_subtotal,
                'debit': balance > 0.0 and balance or 0.0,
                'credit': balance < 0.0 and -balance or 0.0,
            }
        else:
            # Single-currency.
            return {
                'amount_currency': price_subtotal,
                'debit': price_subtotal > 0.0 and price_subtotal or 0.0,
                'credit': price_subtotal < 0.0 and -price_subtotal or 0.0,
            }


