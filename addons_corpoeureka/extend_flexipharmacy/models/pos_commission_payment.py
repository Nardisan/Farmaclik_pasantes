from datetime import date
from odoo.exceptions import Warning
from odoo import models, fields, api, _


class PosCommissionPayment(models.Model):
    _inherit = 'pos.commission.payment'
    _description = "Point of Sale Commission Payment"

    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)

    #DIARIO QUE SE ELIGE PARA EL PAGO DE LAS COMISIONES A MEDICOS
    journal_id = fields.Many2one('account.journal', string='Journal', required=True, domain="[('company_id', '=', company_id),('type', 'in', ('bank', 'cash'))]")
    is_invoice_paid = fields.Boolean(string='Paid Invoice', default=True)

    def payment(self):
        if self.commission_pay_ids:
            IrDefault = self.env['ir.default'].sudo()
            account_id = IrDefault.get('res.config.settings', "pos_account_id")
            if not account_id:
                raise Warning(_(
                    'Commission Account is not Found. Please go to Invoice Configuration and set the Commission account.'))
            account_id = self.env['account.account'].browse(account_id)
            doctor_detail = {
                'partner_id': self.doctor_id.id,
                'invoice_date': date.today(),
                'move_type': 'in_invoice'
            }
            invoice_line_data = []
            total_amount = 0
            for each in self.commission_pay_ids:
                total_amount += each.amount
                each.write({'state': 'reserved'})
                invoice_line_data.append((0, 0, {
                    'account_id': account_id.id,
                    'name': each.commission_number + " Doctor Commission" if each.commission_number else  " Doctor Commission",
                    'quantity': 1,
                    'price_unit': each.amount,
                }))

            journal_id = self.env['account.journal'].search([('type','=','purchase'),('code','=','NE1')]),

            doctor_detail.update({
                'invoice_line_ids': invoice_line_data,
                'pos_vendor_commission_ids': [(6, 0, self.commission_pay_ids.ids)]
            })
            invoice_id = self.env['account.move'].create(doctor_detail)
            invoice_id.journal_id = journal_id[0].id
            if self.is_invoice_paid:
                invoice_id.action_post()
                amount = total_amount * self.doctor_id.currency_id._get_conversion_rate(from_currency=invoice_id.currency_id,
                    to_currency=self.doctor_id.currency_id, company=self.env.user.company_id, date=date.today())
                values = {
                    'payment_type': 'outbound',
                    'partner_type': 'supplier',
                    'partner_id': self.doctor_id.id,
                    'amount': round(round (amount,2) * invoice_id.manual_currency_exchange_rate,2) if self.journal_id.currency_id else amount,
                    'amount_ref': amount if self.journal_id.currency_id else round(round (amount,2) / invoice_id.manual_currency_exchange_rate,2),
                    'ref': invoice_id.name,
                    'currency_id': self.journal_id.currency_id.id if self.journal_id.currency_id else self.env.company.currency_id.id,
                    # 'reference_invoice_id': invoice_id.id,
                    'journal_id': self.journal_id.id,
                    'date': date.today(),
                }
                payment = self.env['account.payment'].sudo().create(values)
                payment.sudo().action_post()
                # for line in payment_ids:
                move_line = self.env['account.move.line'].search([('payment_id', '=', payment.id), ('account_id', '=', self.doctor_id.property_account_payable_id.id)])
                invoice_id.js_assign_outstanding_line(move_line.id)
                for each in invoice_id.pos_vendor_commission_ids:
                    if each.state == 'reserved':
                        each.state = 'paid'
            else: 
                for each in invoice_id.pos_vendor_commission_ids:
                    each.state == 'reserved'
