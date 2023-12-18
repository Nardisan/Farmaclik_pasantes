# -*- coding: utf-8 -*-

from odoo import fields, models


class AccountPrintJournal(models.TransientModel):
    _inherit = "account.common.report"
    _name = "account.print.journal.sale"
    _description = "Account Print Journal"

    journal_ids = fields.Many2many('account.journal', string='Diario', 
                    required=True, 
                    readonly=True, 
                    default=lambda self: self.env['account.journal'].search([('type', '=', 'sale')]))

    def _print_report(self, data):
        data = self.pre_print_report(data)
        records = self.env['account.invoice'].search([('type','=','out_invoice'),
                                                      ('type', '=', 'out_invoice'),
                                                      ('state', 'in', ('paid','open')),
                                                      ('date_invoice', '<=',data['form'].get('date_to')),
                                                      ('date_invoice', '>=',data['form'].get('date_from')),
                                                      ],order='date_invoice ASC')
        price_subtotal=0.00
        price_subtotal_person=0.00
        amount_untaxed=0.00
        amount_tax=0.00
        amount_untaxed_person=0.00
        amount_tax_person=0.00
        internal_sales_not_tax=0.00
        internal_sales_not_tax_person=0.00
        iva_per=0.00
        
        price_subtotal_aj=0.00
        price_subtotal_person_aj=0.00
        amount_untaxed_aj=0.00
        amount_tax_aj=0.00
        amount_untaxed_person_aj=0.00
        amount_tax_person_aj=0.00
        internal_sales_not_tax_aj=0.00
        internal_sales_not_tax_person_aj=0.00
        
        withheld_iva=0.00
        perceived_iva=0.00
        withheld_iva_aj=0.00
        perceived_iva_aj=0.00
        for invoice in records:
            
            if invoice.transaction_type != '04-ajuste':
                if invoice.is_scripture or invoice.wh_id:
                    withheld_iva+=invoice.amount_wh_iva
                price_subtotal+=invoice.amount_total
                if invoice.partner_id.company_type == 'company':
                    amount_tax+=invoice.amount_tax
                    amount_untaxed+=invoice.amount_untaxed
                    for line_invoice in invoice.invoice_line_ids:
                        for line_invoice_tax in line_invoice.invoice_line_tax_ids:
                            if line_invoice_tax.amount == 0 and line_invoice_tax.type_tax_use == 'sale':
                                internal_sales_not_tax+=line_invoice.price_subtotal
                                
                elif invoice.partner_id.company_type == 'person':
                    amount_tax_person+=invoice.amount_tax
                    amount_untaxed_person+=invoice.amount_untaxed
                    for line_invoice_person in invoice.invoice_line_ids:
                        for line_invoice_tax in line_invoice_person.invoice_line_tax_ids:
                            if line_invoice_tax.amount == 0 and line_invoice_tax.type_tax_use == 'sale':
                                internal_sales_not_tax_person+=line_invoice_person.price_subtotal
            
            else:
                if invoice.is_scripture or invoice.wh_id:
                    withheld_iva_aj+=invoice.amount_wh_iva
                price_subtotal_aj+=invoice.amount_total
                if invoice.partner_id.company_type == 'company':
                    amount_tax_aj+=invoice.amount_tax
                    amount_untaxed_aj+=invoice.amount_untaxed
                    for line_invoice in invoice.invoice_line_ids:
                        for line_invoice_tax in line_invoice.invoice_line_tax_ids:
                            if line_invoice_tax.amount == 0 and line_invoice_tax.type_tax_use == 'sale':
                                internal_sales_not_tax_aj+=line_invoice.price_subtotal
                
                elif invoice.partner_id.company_type == 'person':
                    amount_tax_person_aj+=invoice.amount_tax
                    amount_untaxed_person_aj+=invoice.amount_untaxed
                    for line_invoice_person in invoice.invoice_line_ids:
                        for line_invoice_tax in line_invoice_person.invoice_line_tax_ids:
                            if line_invoice_tax.amount == 0 and line_invoice_tax.type_tax_use == 'sale':
                                internal_sales_not_tax_person_aj+=line_invoice_person.price_subtotal
                
        data['form'].update({
                            'price_subtotal': price_subtotal,
                            'internal_sales_not_tax': internal_sales_not_tax,
                            'amount_untaxed': amount_untaxed,
                            'amount_tax': amount_tax,
                            'internal_sales_not_tax_person': internal_sales_not_tax_person,
                            'amount_untaxed_person': amount_untaxed_person,
                            'amount_tax_person': amount_tax_person,
                            
                            'price_subtotal_aj': price_subtotal_aj,
                            'internal_sales_not_tax_person_aj': internal_sales_not_tax_person_aj,
                            'amount_untaxed_aj': amount_untaxed_aj,
                            'amount_tax_aj': amount_tax_aj,
                            'internal_sales_not_tax_aj': internal_sales_not_tax_aj,
                            'amount_untaxed_person_aj': amount_untaxed_person_aj,
                            'amount_tax_person_aj': amount_tax_person_aj,
                            
                            'price_subtotal_person': price_subtotal_person,
                            'price_subtotal_person_aj': price_subtotal_person_aj,
                            
                            'withheld_iva': withheld_iva,
                            'perceived_iva': (amount_tax+amount_tax_person)-withheld_iva,
                            'withheld_iva_aj': withheld_iva_aj,
                            'perceived_iva_aj': (amount_tax_aj+amount_tax_person_aj)-withheld_iva_aj,
                            })
        data['model']= records._name
        data['docs_ids']= records.ids
        return self.env['report'].with_context(landscape=True).get_action(records, 'sale_invoice_ledger2', data=data)
