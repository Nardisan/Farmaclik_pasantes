# -*- coding: utf-8 -*-

from operator import add, mod, mul, truediv
from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.depends('price_unit','move_id.manual_currency_exchange_rate')
    def _compute_price_unit_ref(self):
        for record in self:
            record[("price_unit_ref")] = record['price_unit']
            if record.move_id.manual_currency_exchange_rate != 0 and record.display_type == False:
                record[("price_unit_ref")] = record['price_unit']*record.move_id.manual_currency_exchange_rate

    @api.onchange('product_id','quantity','price_subtotal','move_id.manual_currency_exchange_rate')
    def onchange_product_id_ref(self):
        for record in self:  
            record._compute_price_unit_ref()
            record[("price_subtotal_ref")] = record.quantity * record.price_unit_ref

    @api.depends('price_unit_ref','quantity')
    def _compute_price_subtotal_ref(self):
        for record in self:
            record[("price_subtotal_ref")] = record[("price_subtotal")]
            if record.move_id.manual_currency_exchange_rate != 0 and record.display_type == False:  
                record[("price_subtotal_ref")] = record.quantity * record.price_unit_ref
    
    # Campos para Calcular la MultiMoneda
    price_unit_ref = fields.Float(string='Monto Ref', store=True,readonly=True, compute='_compute_price_unit_ref', tracking=4, default=0, invisible="1",digits=(20,3))
    price_subtotal_ref = fields.Float(string='Subtotal Ref',store=True, readonly=True, tracking=4, default=0,compute='_compute_price_subtotal_ref',digits=(20,3))
    currency_id_line = fields.Many2one(related="move_id.currency_id_dif",string="Moneda Referencia", invisible="1",store=True)
    company_id = fields.Many2one(related="move_id.company_id",store=True)
    invoice_date = fields.Date(related="move_id.invoice_date",store=True)

    # Añadir Multimoneda en Cuenta Analítica (Centro de Costos)
    def _prepare_analytic_line(self):
        """ Prepare the values used to create() an account.analytic.line upon validation of an account.move.line having
            an analytic account. This method is intended to be extended in other modules.
            :return list of values to create analytic.line
            :rtype list
        """
        super(AccountMoveLine, self)._prepare_analytic_line()
        result = []
        amount_usd= 0.0
        for move_line in self:
            amount = (move_line.credit or 0.0) - (move_line.debit or 0.0)
            if amount < 0:
                amount_usd=move_line.price_subtotal_ref * -1
            else:
                amount_usd=move_line.price_subtotal_ref
            default_name = move_line.name or (move_line.ref or '/' + ' -- ' + (move_line.partner_id and move_line.partner_id.name or '/'))
            result.append({
                'name': default_name,
                'date': move_line.date,
                'account_id': move_line.analytic_account_id.id,
                'tag_ids': [(6, 0, move_line._get_analytic_tag_ids())],
                'unit_amount': move_line.quantity,
                'product_id': move_line.product_id and move_line.product_id.id or False,
                'product_uom_id': move_line.product_uom_id and move_line.product_uom_id.id or False,
                'amount': amount,
                'amount_usd': amount_usd,
                'general_account_id': move_line.account_id.id,
                'ref': move_line.ref,
                'move_id': move_line.id,
                'user_id': move_line.move_id.invoice_user_id.id or self._uid,
                'partner_id': move_line.partner_id.id,
                'company_id': move_line.analytic_account_id.company_id.id or self.env.company.id,
            })
        return result

    # Añadir Multimoneda en Cuenta Analítica (Centro de Costos)
    def _prepare_analytic_distribution_line(self, distribution):
        """ Prepare the values used to create() an account.analytic.line upon validation of an account.move.line having
            analytic tags with analytic distribution.
        """
        super(AccountMoveLine, self)._prepare_analytic_distribution_line(distribution)
        amount_usd= 0.0
        self.ensure_one()
        amount = -self.balance * distribution.percentage / 100.0
        default_name = self.name or (self.ref or '/' + ' -- ' + (self.partner_id and self.partner_id.name or '/'))
        if amount < 0:
                amount_usd=self.price_subtotal_ref * -1
        else:
            amount_usd=self.price_subtotal_ref
        return {
            'name': default_name,
            'date': self.date,
            'account_id': distribution.account_id.id,
            'partner_id': self.partner_id.id,
            'tag_ids': [(6, 0, [distribution.tag_id.id] + self._get_analytic_tag_ids())],
            'unit_amount': self.quantity,
            'product_id': self.product_id and self.product_id.id or False,
            'product_uom_id': self.product_uom_id and self.product_uom_id.id or False,
            'amount': amount,
            'amount_usd': amount_usd,
            'general_account_id': self.account_id.id,
            'ref': self.ref,
            'move_id': self.id,
            'user_id': self.move_id.invoice_user_id.id or self._uid,
            'company_id': distribution.account_id.company_id.id or self.env.company.id,
        }

    debit_usd = fields.Monetary(
        'Debit $', 
        'currency_id_line',
        compute="_report_usd_fields",
        store=True,
        default=0.
    )
    credit_usd = fields.Monetary(
        'Credit $', 
        'currency_id_line',
        compute="_report_usd_fields",
        store=True,
        default=0.
    )
    balance_usd = fields.Monetary(
        'Balance $', 
        'currency_id_line',
        compute="_report_usd_fields",
        store=True,
        default=0.
    )
    
    @api.depends('debit','credit','balance','move_id.manual_currency_exchange_rate','move_id.currency_id')
    def _report_usd_fields(self):
        for rec in self:
            rec.debit_usd = rec.credit_usd = rec.balance_usd = 0 

            if rec.manual_currency_exchange_rate != 0:
                AMOUNTS = (rec.debit, rec.credit, rec.balance)
                rate = rec.move_id.manual_currency_exchange_rate

                rec.debit_usd, rec.credit_usd, rec.balance_usd = (
                    (mul if rec.move_id.currency_id == rec.company_currency_id else truediv)(a, rate) 
                        for a in AMOUNTS
                )


    @api.onchange('amount_currency')
    def _onchange_amount_currency_ref(self):
        balance = self.amount_currency if self.env.company.currency_id == self.move_id.currency_id else self.amount_currency * self.manual_currency_exchange_rate
        #balance = currency._convert(amount_currency, company.currency_id, company, date or fields.Date.context_today(self))
        self.debit =  balance > 0.0 and balance or 0.0
        self.credit =  balance < 0.0 and -balance or 0.0
