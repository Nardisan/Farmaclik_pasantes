# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp

class AccountInvoice(models.Model):
    _inherit = 'account.move'
    
    @api.depends('invoice_line_ids.price_subtotal','wh_id','wh_id.wh_lines','retention', 'currency_id', 'company_id', 'invoice_date', 'move_type','manual_currency_exchange_rate')
    def _compute_wh_iva(self):
        amount_iva = 0.0
        for invoice in self:
            if invoice.wh_id:
                whl_ids = self.env['account.wh.iva.line'].search(
                    [
                        ('invoice_id', '=', invoice.id),
                    ]
                )
                amount_iva = sum(whl.ret_amount for whl in whl_ids)
                invoice.amount_wh_iva = round(amount_iva,2) if invoice.currency_id == self.env.company.currency_id else round(amount_iva/invoice.manual_currency_exchange_rate,2)
            else:
                invoice.amount_wh_iva = 0.0

    @api.depends('invoice_line_ids','invoice_line_ids.price_unit','invoice_line_ids.price_subtotal','exempt_amount', 'currency_id', 'company_id', 'invoice_date', 'move_type')
    def get_exempt_amount(self):
        amount = 0.0
        #amount = sum(self.invoice_line_ids.filtered(lambda line: not line.tax_ids or sum(line.tax_ids.mapped('amount')) == 0).mapped('price_subtotal'))
        self.exempt_amount = amount

    pay_withholding_id_iva = fields.Many2one('account.wh.iva.pay', 'Pago IVA Asociado', 
                                    readonly=True, 
                                    copy=False)
    wh_id = fields.Many2one('account.wh.iva', 'Retención IVA', copy = False,
        readonly=True)
    amount_wh_iva = fields.Monetary(string='Wh IVA Amount', copy = False, digits=dp.get_precision('Withhold'),
        readonly=True, store=True, compute='_compute_wh_iva', track_visibility='onchangue')
    exempt_amount = fields.Monetary(string='Exempt amount', copy = False, digits=dp.get_precision('Withhold'),
        readonly=True, compute='get_exempt_amount', track_visibility='always')
    retention = fields.Selection(([('01-sin','No Retention'),
                                            ('02-special', '75% special contributor'),
                                            ('03-ordinary', '100% contributor ordinary'),
                                            ]),string='% de retencion', compute='_compute_retention', store=True, readonly=False)
    can_delete_iva = fields.Boolean('Puede eliminar la retención de IVA',default=False,copy = False)

    @api.depends('partner_id', 'move_type', 'partner_id.property_account_position_id')
    def _compute_retention(self):
        for inv in self:
            if inv.move_type in ('out_invoice', 'out_refund', 'out_receipt'):
                inv.retention = self.partner_id.property_account_position_id.ret_IVA_sale
            else:
                inv.retention = self.partner_id.property_account_position_id.ret_IVA_purchase

    def action_invoice_cancel(self):
       invoice_cancel= super(AccountInvoice, self).action_invoice_cancel()
       for inv in self:
           if inv.wh_id:
                if inv.wh_id.state in ['draft','confirmed','withhold']:
                    inv.wh_id.write({'state': 'draft'})
                    for whl in inv.wh_id.wh_lines:
                        if whl.invoice_id.id == inv.id:
                            whl.write({'state': 'draft'})
                else:
                    raise UserError(_('La factura está asociada a una retención IVA Declarada.'))
                    return
       return invoice_cancel

    @api.model
    def create_lines_retention(self, retention_id):
        if not self.can_delete_iva or not retention_id.asiento_iva:
            account_ret = self.company_id.sale_iva_ret_account.id if self.move_type in ('out_invoice', 'out_refund', 'out_receipt') else self.company_id.purchase_iva_ret_account.id
            vals = {
                'date': fields.Datetime.now(),
                'journal_id': self.company_id.journal_iva.id,
                'line_ids': False,
                'state': 'draft',
                'partner_id': self.partner_id.id,
                'move_type':'entry',
                'manual_currency_exchange_rate':self.manual_currency_exchange_rate if self.currency_id != self.company_id.currency_id else 1/self.manual_currency_exchange_rate,
                'currency_id': self.currency_id.id if self.currency_id != self.company_id.currency_id else self.currency_id.parent_id.id,
                'apply_manual_currency_exchange':True,
            }
            move_apply_obj = self.env['account.move']
            move_apply_id = move_apply_obj.create(vals)
            retention_id.asiento_iva = move_apply_id.id
            # amount_currency = round(retention_id.total_tax_ret * self.manual_currency_exchange_rate,2) if self.currency_id == self.company_id.currency_id else round(self.amount_tax *(retention_id.wh_lines[0].rate_amount/100),2)
            amount_currency = round((self.amount_tax *(retention_id.wh_lines[0].rate_amount/100)) * self.manual_currency_exchange_rate,2) if self.currency_id == self.company_id.currency_id else round(self.amount_tax *(retention_id.wh_lines[0].rate_amount/100),2)
            move_advance = {
                'account_id': self.partner_id.property_account_receivable_id.id if self.move_type in ('out_invoice', 'out_refund', 'out_receipt') else self.partner_id.property_account_payable_id.id,
                'company_id': self.env.company.id,
                'currency_id': self.currency_id.id if self.currency_id != self.company_id.currency_id else self.currency_id.parent_id.id,
                'date_maturity': False,
                'ref': self.ref,
                'date': fields.Datetime.now(),
                'partner_id': self.partner_id.id,
                'move_id': move_apply_id.id,
                'name': 'Retención de IVA',
                'journal_id': self.journal_id.id,
                
                'amount_currency': (amount_currency) *-1 if self.move_type in ('out_invoice', 'in_refund', 'out_receipt') else (amount_currency),
                'credit': round(retention_id.total_tax_ret,2) if self.move_type in ('out_invoice', 'in_refund', 'out_receipt') else 0.0,
                'debit': round(retention_id.total_tax_ret,2) if self.move_type not in ('out_invoice', 'in_refund', 'out_receipt') else 0.0,
            }
            
            # if not self.currency_id == self.company_id.currency_id:
            move_advance.update({
                'credit':move_advance['credit'] / self.manual_currency_exchange_rate if not self.currency_id == self.company_id.currency_id
                    else move_advance['credit'] * self.manual_currency_exchange_rate,
                'debit':move_advance['debit'] / self.manual_currency_exchange_rate if not self.currency_id == self.company_id.currency_id
                    else move_advance['debit'] * self.manual_currency_exchange_rate,
            })
                
            
            asiento = move_advance
            move_line_obj = self.env['account.move.line']
            move_line_id1 = move_line_obj.with_context(check_move_validity=False).create(asiento)
            asiento['account_id'] = account_ret
            asiento['amount_currency']  = round(amount_currency,2) if self.move_type in ('out_invoice', 'in_refund', 'out_receipt') else round((amount_currency) *-1,2)
            asiento['debit'] = round(retention_id.total_tax_ret,2) if self.move_type in ('out_invoice', 'in_refund', 'out_receipt') else 0.0
            asiento['credit'] = round(retention_id.total_tax_ret,2) if self.move_type not in ('out_invoice', 'in_refund', 'out_receipt') else 0.0
            move_line_id2 = move_line_obj.create(asiento)
            for move in move_apply_id.invoice_line_ids:
                move._onchange_amount_currency_ref()
            move_apply_id.action_post()
            self.can_delete_iva = True
        else:

            retention = self.env['account.wh.iva.line'].search([('invoice_id', '=', self.id)])
            for ret in retention:
                if ret.state == 'confirmed':
                    ret.state = 'draft'
                    ret.unlink()
            if self.retention == '01-sin' or not self.retention:
                raise UserError(_('Esta factura no posee un porcentaje de Retención asociado.'))
                return
            amount_retention = 100.00 if self.retention == '03-ordinary' else 75.0 if self.retention == '02-special' else 0
            if self.move_type in ('out_invoice', 'out_refund', 'out_receipt'):
                account_ret = self.company_id.purchase_iva_ret_account.id
            else:
                account_ret = self.company_id.sale_iva_ret_account.id

            invoice_id = 0
            base_tax = 0
            rate_amount = 0
            ret_tax = 0
            amount_tax = 0
            ret_amount = 0
            payments_three = False
            line_dict = {}
            ret_tax_amount = 0
            for tax in self.invoice_line_ids.filtered(lambda line: line.tax_ids):
                base_tax += tax.debit if self.move_type not in ('out_invoice','in_refund','out_receipt') else tax.credit 
                ret_tax = tax.tax_ids.mapped('id')[0] if ret_tax_amount < tax.tax_ids.mapped('amount')[0] else ret_tax
                amount_tax += sum(tax.tax_ids.mapped('amount'))*tax.debit/100 if self.move_type not in ('out_invoice','in_refund','out_receipt') else sum(tax.tax_ids.mapped('amount'))*tax.credit/100
                ret_amount += float((sum(tax.tax_ids.mapped('amount'))*tax.debit/100) * float(amount_retention) / 100)
                payments_three = tax.payments_three
                ret_tax_amount = tax.tax_ids.mapped('amount')[0]
            line_dict = {
                'invoice_id':self.id,
                'move_id':self.id,
                'base_tax':base_tax,
                'rate_amount':float(amount_retention) ,
                'ret_tax':ret_tax,
                'amount_tax':amount_tax,
                'ret_amount':ret_amount,
                'payments_three': payments_three,
                'state': 'confirmed',
            }
            lines = [(0,False,line_dict)]
            vals_retention = {
                'company_id': self.company_id.id,
                'partner_id': self.partner_id.id,
                'journal_id': self.company_id.journal_iva.id,
                'account_id': account_ret,
                'date': fields.Datetime.now(),
                'move_type': self.move_type,
                'refund': True if self.move_type in ('in_refund', 'out_refund') else False,
                'wh_lines': lines,
                'manual_currency_exchange_rate':self.manual_currency_exchange_rate,

            }
            self.env['account.wh.iva'].search([('id', '=', self.wh_id.id)]).write(vals_retention)
            retention_id.asiento_iva.button_draft()
            for rec in retention_id.asiento_iva.line_ids:
                if rec.debit > 0:
                    rec.debit = retention_id.total_tax_ret
                    retention_id.asiento_iva._onchange_currency()
                if rec.credit > 0:
                    rec.credit = retention_id.total_tax_ret
                    retention_id.asiento_iva._onchange_currency()
            retention_id.asiento_iva.action_post()


    def print_wh_iva(self):
        self.ensure_one()
        iva = self.env['account.wh.iva'].search([('id', '=', self.wh_id.id)])
        return self.env['account.wh.iva'].search([('id', '=', self.wh_id.id)]).env.ref('l10n_ve_retencion_iva.report_withholding_receipt').report_action(iva)

    def action_post_iva(self):
        for inv in self:
            if inv.wh_id and inv.wh_id.state == 'draft':
                if inv.wh_id.wh_lines:
                    for line in inv.wh_id.wh_lines:
                        if line.state == 'draft':
                            line.write({'move_id':inv.id, 'state':'confirmed'})
                inv.wh_id.state = 'confirmed'
                inv.create_lines_retention(inv.wh_id)
                inv.wh_id.action_confirm()

    #def action_post(self):
    #    if self.wh_id and self.wh_id not in ('withhold','declared','done','cancel'):
    #        self.wh_id.action_update()
    #
    #    return super(AccountInvoice, self).button_draft()

    def button_draft(self):
        for inv in self:
            if inv.wh_id and inv.wh_id.state not in ('withhold','declared','done','cancel'):
                inv.wh_id.asiento_iva.button_draft()
                inv.wh_id.state = 'draft'
                if inv.wh_id.wh_lines:
                    for line in inv.wh_id.wh_lines:
                        if line.state == 'confirmed':
                            line.write({'move_id':inv.id, 'state':'draft'})
        return super(AccountInvoice, self).button_draft()

    def button_cancel(self):
        for move in self:
            if move.wh_id and move.wh_id.state not in ('withhold','declared','done'):
                move.wh_id.asiento_iva.button_cancel()
                move.wh_id.state = 'cancel'
        return super(AccountInvoice, self).button_cancel()

    def create_retention(self):
        if self.wh_id:
            raise UserError(_('Ya existe una retención para esta factura. Por favor, eliminela primero antes de crear otra.'))
            return
        if self.retention == '01-sin' or not self.retention:
            raise UserError(_('Esta factura no posee un porcentaje de Retención asociado.'))
            return
        amount_retention = 100.00 if self.retention == '03-ordinary' else 75.0 if self.retention == '02-special' else 0

        if self.move_type in ('out_invoice', 'out_refund', 'out_receipt'):
            account_ret = self.company_id.purchase_iva_ret_account.id
        else:
            account_ret = self.company_id.sale_iva_ret_account.id
        invoice_id = 0
        base_tax = 0
        rate_amount = 0
        ret_tax = 0
        amount_tax = 0
        ret_amount = 0
        payments_three = False
        line_dict = {}
        ret_tax_amount = 0
        for tax in self.invoice_line_ids.filtered(lambda line: line.tax_ids):
            base_tax += tax.debit if self.move_type not in ('out_invoice','in_refund','out_receipt') else tax.credit
            ret_tax = tax.tax_ids.mapped('id')[0] if ret_tax_amount < tax.tax_ids.mapped('amount')[0] else ret_tax
            amount_tax += round(sum(tax.tax_ids.mapped('amount'))*tax.debit/100,2) if self.move_type not in ('out_invoice','in_refund','out_receipt') else round(sum(tax.tax_ids.mapped('amount'))*tax.credit/100,2)
            ret_amount += float((sum(tax.tax_ids.mapped('amount'))*tax.debit/100) * float(amount_retention) / 100)
            payments_three = tax.payments_three
            ret_tax_amount = tax.tax_ids.mapped('amount')[0]
        line_dict = {
            'invoice_id':self.id,
            'base_tax':base_tax,
            'rate_amount':float(amount_retention) ,
            'ret_tax':ret_tax,
            'amount_tax':amount_tax,
            'ret_amount':ret_amount,
            'payments_three': payments_three,
        }
        lines = [(0,False,line_dict)]
        vals_retention = {
            'company_id': self.company_id.id,
            'partner_id': self.partner_id.id,
            'journal_id': self.company_id.journal_iva.id,
            'account_id': account_ret,
            'date': fields.Datetime.now(),
            'move_type': self.move_type,
            'refund': True if self.move_type in ('in_refund', 'out_refund') else False,
            'manual_currency_exchange_rate':self.manual_currency_exchange_rate,
            'wh_lines': lines,
        }
        retention_id = self.env['account.wh.iva'].create(vals_retention)
        self.wh_id = retention_id.id

    def delete_retention(self):
        retention = self.env['account.wh.iva'].search([('id', '=', self.wh_id.id)])
        if retention and retention.state not in ('draft','cancel') and retention.number:
            raise UserError(_('No puedes eliminar una retención que no esté en estado Borrador o Cancelada'))
        else:
            retention.unlink()

    #def write(self, vals):
    #    value = {}
    #    wh_iva_line_obj = self.env['account.wh.iva.line']
    #    for inv in self:
    #        if 'wh_id' in vals.keys():
    #            if vals['wh_id']:
    #                wh_iva = self.env['account.wh.iva'].search([('id', '=', int(vals['wh_id']))])
    #                wh_iva_line_ids = wh_iva_line_obj.search([('invoice_id', '=', inv.id)])
    #                value = {'invoice_id': inv.id,
    #                        'retention_id':  wh_iva.id,
    #                        'ret_tax':  inv.invoice_line_ids.tax_ids,
    #                        'base_tax': inv.amount_untaxed,
    #                        'amount_tax': inv.amount_total,
    #                        'rate_amount': 100.00 if inv.retention =='03-ordinary' else 75.0 if inv.retention=='02-special' else 0,}
    #                if not wh_iva_line_ids:
    #                    wh_iva_line_obj.create(value)
    #                else:
    #                    for wh_line in wh_iva_line_ids:
    #                        if wh_line.retention_id.id != int(vals['wh_id']):
    #                            wh_line.unlink()
    #                            wh_iva_line_obj.create(value)
    #    invoice =  super(AccountInvoice, self).write(vals)
    #    for wh in self:
    #        if wh.wh_id:
    #            if 'invoice_line_ids' in vals.keys() or 'retention' in vals.keys():
    #                wh_line_ids = wh_iva_line_obj.search([('invoice_id', '=', inv.id)])
    #                if wh_line_ids:
    #                    for whl in wh_line_ids:
    #                        whl.state='draft'
    #                        whl.unlink()
    #                    [wh_line_ids.create({
    #                            'retention_id':wh.wh_id.id,
    #                            'invoice_id': wh.id,
    #                            'ret_tax':  tax_id.tax_id.id,
    #                            'base_tax': tax_id.base,
    #                            'amount_tax': tax_id.mapped('amount'),
    #                            'rate_amount': 100.00 if inv.retention=='03-ordinary' else 75.0 if inv.retention=='02-special' else 0,
    #                        }) for tax_id in wh.invoice_line_ids.tax_ids if tax_id.amount > 0]
    #                    wh_line_new = wh_iva_line_obj.search([('invoice_id', '=', inv.id)])
    #                    if wh_line_new:
    #                        for whln in wh_line_new:
    #                            whln.state = whln.retention_id.state
    #    return invoice

class AccountMoveLineInherit(models.Model):
    _inherit = "account.move.line"
    
    pay_wh_id = fields.Many2one('account.wh.iva.pay', 'Withholding IVA', 
                                    readonly=True, 
                                    copy=False)

class AccountPayment(models.Model):
    _inherit='account.payment'

    iva_entry = fields.Many2one('account.move',string="Pago de IVA Relacionado")
    iva_entry_amount = fields.Monetary(string="Monto del Pago de IVA Relacionado", related="iva_entry.amount_total")
