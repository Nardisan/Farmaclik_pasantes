# -*- coding: utf-8 -*-

from odoo import api, fields, models

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.depends('amount','manual_currency_exchange_rate')
    def _amount_all_usd(self):
        for record in self:
            record[("amount_ref")]       = record.amount
            record[("tasa_del_dia")]     = 1
            record[("tasa_del_dia_two")] = 1
            if record.manual_currency_exchange_rate != 0:
                record[("amount_ref")]    = record['amount']*record.manual_currency_exchange_rate
                record[("tasa_del_dia")]     = 1*record.manual_currency_exchange_rate
                record[("tasa_del_dia_two")] = 1/record.manual_currency_exchange_rate

    #  Campos Nuevos para el calculo de la doble moneda
    currency_id_ref = fields.Many2one(related="currency_id.parent_id",
    string="Moneda Referencia", invisible="1",store=True)
    tasa_del_dia     = fields.Float(store=True,readonly=True, compute="_amount_all_usd", default=0, digits=(20,10)) 
    tasa_del_dia_two = fields.Float(store=True,readonly=True, compute="_amount_all_usd", default=0, digits=(20,10)) 
    amount_ref       = fields.Float(string='Monto Ref', store=True, readonly=True, compute='_amount_all_usd', tracking=4, default=0)
    manual_currency_exchange_rate = fields.Float(string='Tipo de tasa manual', digits=(20,10),default=lambda self: self.env.company.currency_id.parent_id.rate)
    # Modificación de campo para predefinir la compañia
    company_id = fields.Many2one('res.company',default=lambda self: self.env.company.id,)

class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    def _create_payments(self):
        self.ensure_one()
        batches = self._get_batches()
        edit_mode = self.can_edit_wizard and (len(batches[0]['lines']) == 1 or self.group_payment)

        to_reconcile = []
        if edit_mode:
            payment_vals = self._create_payment_vals_from_wizard()
            payment_vals_list = [payment_vals]
            to_reconcile.append(batches[0]['lines'])
        else:
            # Don't group payments: Create one batch per move.
            if not self.group_payment:
                new_batches = []
                for batch_result in batches:
                    for line in batch_result['lines']:
                        new_batches.append({
                            **batch_result,
                            'lines': line,
                        })
                batches = new_batches

            payment_vals_list = []
            for batch_result in batches:
                payment_vals_list.append(self._create_payment_vals_from_batch(batch_result))
                to_reconcile.append(batch_result['lines'])

        payments = self.env['account.payment'].create(payment_vals_list)

        # If payments are made using a currency different than the source one, ensure the balance match exactly in
        # order to fully paid the source journal items.
        # For example, suppose a new currency B having a rate 100:1 regarding the company currency A.
        # If you try to pay 12.15A using 0.12B, the computed balance will be 12.00A for the payment instead of 12.15A.
        if edit_mode:
            for payment, lines in zip(payments, to_reconcile):
                # Batches are made using the same currency so making 'lines.currency_id' is ok.
                if payment.currency_id != lines.currency_id:
                    liquidity_lines, counterpart_lines, writeoff_lines = payment._seek_for_lines()
                    source_balance = abs(sum(lines.mapped('amount_residual')))
                    payment_rate = liquidity_lines[0].amount_currency / liquidity_lines[0].balance
                    source_balance_converted = abs(source_balance) * payment_rate

                    # Translate the balance into the payment currency is order to be able to compare them.
                    # In case in both have the same value (12.15 * 0.01 ~= 0.12 in our example), it means the user
                    # attempt to fully paid the source lines and then, we need to manually fix them to get a perfect
                    # match.
                    payment_balance = abs(sum(counterpart_lines.mapped('balance')))
                    payment_amount_currency = abs(sum(counterpart_lines.mapped('amount_currency')))
                    if not payment.currency_id.is_zero(source_balance_converted - payment_amount_currency):
                        continue

                    delta_balance = source_balance - payment_balance

                    # Balance are already the same.
                    if self.company_currency_id.is_zero(delta_balance):
                        continue

                    # Fix the balance but make sure to peek the liquidity and counterpart lines first.
                    debit_lines = (liquidity_lines + counterpart_lines).filtered('debit')
                    credit_lines = (liquidity_lines + counterpart_lines).filtered('credit')

                    payment.move_id.write({'line_ids': [
                        (1, debit_lines[0].id, {'debit': debit_lines[0].debit + delta_balance}),
                        (1, credit_lines[0].id, {'credit': credit_lines[0].credit + delta_balance}),
                    ]})

        for line in payments.move_id.line_ids:
            #line._onchange_amount_currency_ref()
            if not line.mapped('full_reconcile_id.exchange_move_id'):
                balance = 0 
                if line.env.company.currency_id == line.move_id.currency_id:
                    balance = line.amount_currency 
                if line.env.company.currency_id != line.move_id.currency_id and line.manual_currency_exchange_rate !=0:
                    balance = line.amount_currency * line.manual_currency_exchange_rate
                 #balance = currency._convert(amount_currency, company.currency_id, company, date or fields.Date.context_today(self))
                if not line.matched_debit_ids and not line.matched_credit_ids:
                    line.debit =  balance > 0.0 and balance or 0.0
                    line.credit =  balance < 0.0 and -balance or 0.0
        payments.action_post()

        domain = [('account_internal_type', 'in', ('receivable', 'payable')), ('reconciled', '=', False)]
        for payment, lines in zip(payments, to_reconcile):

            # When using the payment tokens, the payment could not be posted at this point (e.g. the transaction failed)
            # and then, we can't perform the reconciliation.
            if payment.state != 'posted':
                continue

            payment_lines = payment.line_ids.filtered_domain(domain)
            for account in payment_lines.account_id:
                (payment_lines + lines)\
                    .filtered_domain([('account_id', '=', account.id), ('reconciled', '=', False)])\
                    .reconcile()

        return payments