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

from odoo import models, fields, api, _


class AccountPayments(models.Model):
    _inherit = 'account.payment'

    apply_manual_currency_exchange = fields.Boolean(string='Aplicar cambio de tasa manual')
    manual_currency_exchange_rate = fields.Float(string='Tipo de tasa manual',digits=(10,10))
    active_manual_currency_rate = fields.Boolean('Activar Moneda manual', default=True)

    @api.model
    def default_get(self, fields):
        result = super(AccountPayments, self).default_get(fields)
        active_ids = self._context.get('active_ids') or self._context.get('active_id')
        active_model = self._context.get('active_model')
        if not active_ids or active_model != 'account.move':
            return result
        move_id = self.env['account.move'].browse(self._context.get('active_ids')).filtered(lambda move: move.is_invoice(include_receipts=True))
        result.update({
            'apply_manual_currency_exchange':move_id[0].apply_manual_currency_exchange,
            'manual_currency_exchange_rate':move_id[0].manual_currency_exchange_rate,
            })
        return result

    @api.model
    def _compute_payment_amount(self, invoices, currency, journal, date):
        '''Compute the total amount for the payment wizard.

        :param invoices:    Invoices on which compute the total as an account.invoice recordset.
        :param currency:    The payment's currency as a res.currency record.
        :param journal:     The payment's journal as an account.journal record.
        :param date:        The payment's date as a datetime.date object.
        :return:            The total amount to pay the invoices.
        '''
        company = journal.company_id
        currency = currency or journal.currency_id or company.currency_id
        date = date or fields.Date.today()

        if not invoices:
            return 0.0

        self.env['account.move'].flush(['move_type', 'currency_id'])
        self.env['account.move.line'].flush(['amount_residual', 'amount_residual_currency', 'move_id', 'account_id'])
        self.env['account.account'].flush(['user_type_id'])
        self.env['account.account.type'].flush(['type'])
        self._cr.execute('''
            SELECT
                move.move_type AS move_type,
                move.currency_id AS currency_id,
                SUM(line.amount_residual) AS amount_residual,
                SUM(line.amount_residual_currency) AS residual_currency
            FROM account_move move
            LEFT JOIN account_move_line line ON line.move_id = move.id
            LEFT JOIN account_account account ON account.id = line.account_id
            LEFT JOIN account_account_type account_type ON account_type.id = account.user_type_id
            WHERE move.id IN %s
            AND account_type.type IN ('receivable', 'payable')
            GROUP BY move.id, move.move_type
        ''', [tuple(invoices.ids)])
        query_res = self._cr.dictfetchall()

        total = 0.0
        for res in query_res:
            move_currency = self.env['res.currency'].browse(res['currency_id'])
            if move_currency == currency and move_currency != company.currency_id:
                total += res['residual_currency']
            else:
                company = company.with_context(
                manual_rate=self.manual_currency_exchange_rate,
                active_manutal_currency = self.apply_manual_currency_exchange,
            )
                total += company.currency_id._convert(res['amount_residual'], currency, company, date)
        return total


    def _prepare_move_line_default_vals(self, write_off_line_vals=None):
        ''' Prepare the dictionary to create the default account.move.lines for the current payment.
        :param write_off_line_vals: Optional dictionary to create a write-off account.move.line easily containing:
            * amount:       The amount to be added to the counterpart amount.
            * name:         The label to set on the line.
            * account_id:   The account on which create the write-off.
        :return: A list of python dictionary to be passed to the account.move.line's 'create' method.
        '''
        res = super(AccountPayments, self)._prepare_move_line_default_vals(False)
        self.ensure_one()
        write_off_line_vals = write_off_line_vals or {}

        if not self.journal_id.payment_debit_account_id or not self.journal_id.payment_credit_account_id:
            raise UserError(_(
                "You can't create a new payment without an outstanding payments/receipts account set on the %s journal.",
                self.journal_id.display_name))

        # Compute amounts.
        write_off_amount_currency = write_off_line_vals.get('amount', 0.0)

        if self.payment_type == 'inbound':
            # Receive money.
            liquidity_amount_currency = self.amount
        elif self.payment_type == 'outbound':
            # Send money.
            liquidity_amount_currency = -self.amount
            write_off_amount_currency *= -1
        else:
            liquidity_amount_currency = write_off_amount_currency = 0.0


        if self.manual_currency_exchange_rate >0.0 and self.currency_id.id != self.env.company.currency_id.id:
                write_off_balance = write_off_amount_currency * self.manual_currency_exchange_rate
                liquidity_balance = liquidity_amount_currency * self.manual_currency_exchange_rate
        else:
            write_off_balance = self.currency_id._convert(
                write_off_amount_currency,
                self.company_id.currency_id,
                self.company_id,
                self.date,
            )
            liquidity_balance = self.currency_id._convert(
                liquidity_amount_currency,
                self.company_id.currency_id,
                self.company_id,
                self.date,
            )
        counterpart_amount_currency = -liquidity_amount_currency - write_off_amount_currency
        counterpart_balance = -liquidity_balance - write_off_balance
        currency_id = self.currency_id.id

        if self.is_internal_transfer:
            if self.payment_type == 'inbound':
                liquidity_line_name = _('Transfer to %s', self.journal_id.name)
            else: # payment.payment_type == 'outbound':
                liquidity_line_name = _('Transfer from %s', self.journal_id.name)
        else:
            liquidity_line_name = self.payment_reference

        # Compute a default label to set on the journal items.

        payment_display_name = {
            'outbound-customer': _("Customer Reimbursement"),
            'inbound-customer': _("Customer Payment"),
            'outbound-supplier': _("Vendor Payment"),
            'inbound-supplier': _("Vendor Reimbursement"),
        }

        default_line_name = self.env['account.move.line']._get_default_line_name(
            _("Internal Transfer") if self.is_internal_transfer else payment_display_name['%s-%s' % (self.payment_type, self.partner_type)],
            self.amount,
            self.currency_id,
            self.date,
            partner=self.partner_id,
        )

        line_vals_list = [
            # Liquidity line.
            {
                'name': liquidity_line_name or default_line_name,
                'date_maturity': self.date,
                'amount_currency': liquidity_amount_currency,
                'currency_id': currency_id,
                'debit': liquidity_balance if liquidity_balance > 0.0 else 0.0,
                'credit': -liquidity_balance if liquidity_balance < 0.0 else 0.0,
                'partner_id': self.partner_id.id,
                'account_id': self.journal_id.payment_credit_account_id.id if liquidity_balance < 0.0 else self.journal_id.payment_debit_account_id.id,
            },
            # Receivable / Payable.
            {
                'name': self.payment_reference or default_line_name,
                'date_maturity': self.date,
                'amount_currency': counterpart_amount_currency,
                'currency_id': currency_id,
                'debit': counterpart_balance if counterpart_balance > 0.0 else 0.0,
                'credit': -counterpart_balance if counterpart_balance < 0.0 else 0.0,
                'partner_id': self.partner_id.id,
                'account_id': self.destination_account_id.id,
            },
        ]
        if not self.currency_id.is_zero(write_off_amount_currency):
            # Write-off line.
            line_vals_list.append({
                'name': write_off_line_vals.get('name') or default_line_name,
                'amount_currency': write_off_amount_currency,
                'currency_id': currency_id,
                'debit': write_off_balance if write_off_balance > 0.0 else 0.0,
                'credit': -write_off_balance if write_off_balance < 0.0 else 0.0,
                'partner_id': self.partner_id.id,
                'account_id': write_off_line_vals.get('account_id'),
            })
        return line_vals_list

    def _synchronize_to_moves(self, changed_fields):
        ''' Update the account.move regarding the modified account.payment.
        :param changed_fields: A list containing all modified fields on account.payment.
        '''
        result = super(AccountPayments, self)._synchronize_to_moves(changed_fields)
        #if self._context.get('skip_account_move_synchronization'):
        #    return

        #if not any(field_name in changed_fields for field_name in (
        #    'date', 'amount', 'payment_type', 'partner_type', 'payment_reference', 'is_internal_transfer',
        #    'currency_id', 'partner_id', 'destination_account_id', 'partner_bank_id','manual_currency_exchange_rate',
        #    'active_manual_currency_rate',
        #)):
        #    return

        #for pay in self.with_context(skip_account_move_synchronization=True):
        #   liquidity_lines, counterpart_lines, writeoff_lines = pay._seek_for_lines()

        #   # Make sure to preserve the write-off amount.
        #   # This allows to create a new payment with custom 'line_ids'.

        #   if writeoff_lines:
        #       writeoff_amount = sum(writeoff_lines.mapped('amount_currency'))
        #       counterpart_amount = counterpart_lines['amount_currency']
        #       if writeoff_amount > 0.0 and counterpart_amount > 0.0:
        #           sign = 1
        #       else:
        #           sign = -1

        #       write_off_line_vals = {
        #           'name': writeoff_lines[0].name,
        #           'amount': writeoff_amount * sign,
        #           'account_id': writeoff_lines[0].account_id.id,
        #       }
        #   else:
        #       write_off_line_vals = {}

        #   line_vals_list = pay._prepare_move_line_default_vals(write_off_line_vals=write_off_line_vals)

        #   line_ids_commands = [
        #       (1, liquidity_lines.id, line_vals_list[0]),
        #       (1, counterpart_lines.id, line_vals_list[1]),
        #   ]

        #   for line in writeoff_lines:
        #       line_ids_commands.append((2, line.id))

        #   if writeoff_lines:
        #       line_ids_commands.append((0, 0, line_vals_list[2]))

            # Update the existing journal items.
        #    # If dealing with multiple write-off lines, they are dropped and a new one is generated.

            #pay.move_id.write({
                ##'partner_id': pay.partner_id.id,
                ##'currency_id': pay.currency_id.id,
                ##'partner_bank_id': pay.partner_bank_id.id,
                ##'line_ids': line_ids_commands,
                #'manual_currency_exchange_rate': pay.manual_currency_exchange_rate,
                #'active_manual_currency_rate': pay.active_manual_currency_rate,
            #})
        self.move_id.write({
            #'partner_id': pay.partner_id.id,
            #'currency_id': pay.currency_id.id,
            #'partner_bank_id': pay.partner_bank_id.id,
            #'line_ids': line_ids_commands,
            'manual_currency_exchange_rate': self.manual_currency_exchange_rate,
            'active_manual_currency_rate': self.active_manual_currency_rate,
        })

class AccountPaymentRegisters(models.TransientModel):
    _inherit = 'account.payment.register'

    apply_manual_currency_exchange = fields.Boolean(string='Aplicar cambio de tasa manual')
    manual_currency_exchange_rate = fields.Float(string='Tipo de tasa manual',digits=(20,16))
    active_manual_currency_rate = fields.Boolean('Activar Moneda manual', default=True)
    amount_ref = fields.Float(string="Monto Ref",store=True,compute="_compute_amount_ref")


    @api.depends('amount','manual_currency_exchange_rate')
    def _compute_amount_ref(self):
        for wizard in self:
            #if wizard.currency_id == wizard.company_id.currency_id:
            wizard.amount_ref = wizard.amount * wizard.manual_currency_exchange_rate
            #else:
            #    wizard.amount_ref = wizard.amount * wizard.manual_currency_exchange_rate

    @api.model
    def default_get(self, fields):
        result = super(AccountPaymentRegisters, self).default_get(fields)
        active_ids = self._context.get('active_ids') or self._context.get('active_id')
        active_model = self._context.get('active_model')
        if not active_ids or active_model != 'account.move':
            return result
        move_id = self.env['account.move'].browse(self._context.get('active_ids')).filtered(lambda move: move.is_invoice(include_receipts=True))
        result.update({
            'apply_manual_currency_exchange':move_id[0].apply_manual_currency_exchange,
            'manual_currency_exchange_rate':move_id[0].manual_currency_exchange_rate,
            })
        return result

    def _create_payment_vals_from_wizard(self):
        result = super(AccountPaymentRegisters, self)._create_payment_vals_from_wizard()
        result.update({
            'apply_manual_currency_exchange':self.apply_manual_currency_exchange,
            'manual_currency_exchange_rate':self.manual_currency_exchange_rate,
        })
        return result

    @api.depends('source_amount', 'source_amount_currency', 'source_currency_id', 'company_id', 'currency_id', 'payment_date','manual_currency_exchange_rate',)
    def _compute_amount(self):
        result = super(AccountPaymentRegisters, self)._compute_amount()
        for wizard in self:
            if wizard.source_currency_id == wizard.currency_id:
                # Same currency.
                wizard.amount = wizard.source_amount_currency
            elif wizard.currency_id == wizard.company_id.currency_id:
                # Payment expressed on the company's currency.
                wizard.amount = wizard.source_amount
            else:
                # Foreign currency on payment different than the one set on the journal entries.
                amount_payment_currency = wizard.source_amount / wizard.manual_currency_exchange_rate
                wizard.amount = amount_payment_currency
        return result

    @api.depends('amount','manual_currency_exchange_rate','currency_id')
    def _compute_payment_difference(self):
        result = super(AccountPaymentRegisters, self)._compute_payment_difference()
        for wizard in self:
            if wizard.source_currency_id == wizard.currency_id:
                # Same currency.
                wizard.payment_difference = wizard.source_amount_currency - wizard.amount
            elif wizard.currency_id == wizard.company_id.currency_id:
                # Payment expressed on the company's currency.
                wizard.payment_difference = wizard.source_amount - wizard.amount
            else:
                # Foreign currency on payment different than the one set on the journal entries.
                amount_payment_currency = wizard.source_amount / wizard.manual_currency_exchange_rate
                wizard.payment_difference = amount_payment_currency - wizard.amount

    @api.onchange('manual_currency_exchange_rate')
    def _onchange_manual_currency_exchange_rate(self):
        self._compute_payment_difference()
        self._compute_amount()

