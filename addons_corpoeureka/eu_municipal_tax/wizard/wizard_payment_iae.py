# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class AccountPayIae(models.Model):
    _name = "account.iae.pay"
    _order = 'payment_date desc'
    _description = "Pagar Declaracion Mensual Ingresos IAE"
    
    name = fields.Char(readonly=True, copy=False, default="Pago Declaración Mensual de Ingresos")
    account_id = fields.Many2one('account.account',  string='Cuenta Contable', required=True, help="Cuenta Contable respectiva")
    amount = fields.Monetary(string='Monto a Pagar', required=True,readonly=True,help="Monto a pagar al municipio por declaración de ingresos")
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)
    payment_date = fields.Date(string='Fecha de Pago', default=fields.Date.context_today, required=True, copy=False,help="Fecha en la que se realizó el pago")
    communication = fields.Char(string='Circular',help="Descripción opcional del pago")
    journal_id = fields.Many2one('account.journal', string='Diario de Pago', required=True, domain=[('type', '=', 'purchase')],help="Diario en la cual saldra el Pago")
    company_id = fields.Many2one('res.company', related='journal_id.company_id', string='Company', readonly=True)
    tax_municipal = fields.Many2one('tax.municipal',string="Declaración",required=True,readonly=True,help="Declaracion Mensual de ingresos")
    move_id = fields.Many2one('account.move',string="Asiento Contable del Pago",readonly=True,help="Asiento contable que genera el pago al Validar")
    partner_id = fields.Many2one('res.partner',string="Entidad Gubernamental",required=True)
    product_id = fields.Many2one(string="Producto a Facturar", comodel_name="product.product", required=True,domain="[('type', '=', 'service')]")
    company_currency_id = fields.Many2one('res.currency',string="Moneda de la Compañía",default=lambda self: self.env.company.currency_id)
    tasa = fields.Float(string="Tasa")
    same_currency = fields.Boolean(string="Tasas iguales",compute="_compute_same_currency")

    def action_pays_iae(self):
        active_ids = self.env.context.get('active_ids')
        if not active_ids:
            return ''

        return {
            'name': _('Pago de Declaracion Mensual de Ingresos '),
            'res_model': len(active_ids) == 1 and 'account.iae.pay' or 'account.iae.pay',
            'view_mode': 'form',
            'view_id': len(active_ids) != 1 and self.env.ref('eu_municipal_tax.view_pay_iae_view_form').id or self.env.ref('eu_municipal_tax.view_pay_iae_view_form').id,
            'context': self.env.context,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    @api.depends('currency_id','company_currency_id')
    def _compute_same_currency(self):
        for rec in self:
            rec.same_currency = True if rec.currency_id == rec.company_currency_id else False

    @api.model
    def default_get(self, default_fields):
        rec = super(AccountPayIae, self).default_get(default_fields)
        active_ids = self._context.get('active_ids') or self._context.get('active_id')
        active_model = self._context.get('active_model')

        # Chequea que venga desde la Orden
        if not active_ids or active_model != 'tax.municipal':
            return rec

        tax_municipal = self.env['tax.municipal'].browse(active_ids)

        # Revisa que exista un resultado en la busqueda, para no permitir crear una carga manual sin consolidado
        if not tax_municipal:
            raise UserError(_("Para crear un Pago de Declaracion Mensual de Ingresos, debe hacerlo desde la Declaracion Directamente"))
        # Actualiza los campos para la vista
        rec.update({
            'tax_municipal': tax_municipal[0].id,
            'amount': tax_municipal[0].total_iae,
        })
        return rec
   
    # def pay_tax_municipal(self):
    #     # TO DO Multi Currency
    #     line_ids = []
    #     self.name=self.env['ir.sequence'].next_by_code('account.payment.iae.out_invoice')
    #     for pay in self:
    #         move_dict = {
    #                 'ref': pay.name,
    #                 'narration': pay.communication,
    #                 'journal_id': pay.journal_id.id,
    #                 'date': pay.payment_date,
    #             }
            
    #         credit_account_id = pay.journal_id.payment_credit_account_id.id
    #         if credit_account_id:
    #             credit_line = (0, 0, {
    #                 'name': 'Pago del IAE Declaración Mensual',
    #                 'account_id': credit_account_id,
    #                 'journal_id': pay.journal_id.id,
    #                 'date': pay.payment_date,
    #                 'debit': False,
    #                 'credit': pay.amount,
    #             })
    #             line_ids.append(credit_line)
    #         if pay.account_id:
    #             debit_line = (0, 0, {
    #                 'name': 'Pago del IAE Declaración Mensual',
    #                 'account_id': pay.account_id.id,
    #                 'journal_id': pay.journal_id.id,
    #                 'date': pay.payment_date,
    #                 'debit': pay.amount,
    #                 'credit': False,
    #             })
    #             line_ids.append(debit_line)
    #         move_dict['line_ids'] = line_ids
    #         move = self.env['account.move'].create(move_dict)
    #         move.post()
    #         self.move_id=move.id
            
    #         list_line=[]
    #         if move:
    #             for wh in pay.tax_municipal.invoice_line:
    #                 #raise UserError(('%s') %(wh.invoice_id.status_account))
    #                 if wh.invoice_id.status_account == 'declared':
    #                     list_line.append(wh.invoice_id.id)
    #         #raise UserError(('%s') %(list_line)) chivo expiatorio
    #         pay.tax_municipal.write({'state':'done'})
    #         self.env['account.move'].search([('id','in',list_line)]).write({'status_account':'done'})
    #     return True

    def pay_tax_municipal(self):
        for rec in self:
            amount_product = rec.amount
            vals = {
                'date': fields.Datetime.now(),
                'journal_id': rec.journal_id.id,
                'line_ids': False,
                'state': 'draft',
                'partner_id': rec.partner_id.id,
                'currency_id':rec.currency_id.id,
                'move_type':'in_invoice',
            }
            if self.env['ir.module.module'].search([('name','=','l10n_ve_fiscal_requirements'),('state','=','installed')]):
                vals['nro_control'] = rec.name
            if not rec.same_currency:
                vals['apply_manual_currency_exchange'] = True
                vals['manual_currency_exchange_rate'] = 1/rec.tasa
                amount_product = rec.amount * rec.tasa
            move_apply_id = self.env['account.move'].sudo().create(vals)
            move_advance = {
                'account_id': rec.account_id.id,
                'product_id': rec.product_id.id,
                'price_unit': amount_product,
                'company_id': self.env.company.id,
                'currency_id': rec.currency_id.id,
                'date_maturity': False,
                #'ref': ref_payment,
                'date': fields.Datetime.now(),
                'partner_id': rec.partner_id.id,
                'move_id': move_apply_id.id,
                'name': 'Pago de Impuesto Municipal',
                'journal_id': rec.journal_id.id,
                'debit': rec.amount,
                'credit': 0.0,
            }
            if not self.same_currency:
                move_advance['amount_currency'] = amount_product
            asiento = move_advance
            move_line_obj = self.env['account.move.line']
            move_line_id1 = move_line_obj.with_context(check_move_validity=False).create(asiento)
            move_apply_id.with_context(check_move_validity=False)._onchange_partner_id()
            move_apply_id.with_context(check_move_validity=False).action_post()
            
            rec.move_id=move_apply_id.id
            rec.tax_municipal.invoice_ids = move_apply_id.id

            list_line=[]
            if move_apply_id:
                for wh in rec.tax_municipal.invoice_line:
                    #raise UserError(('%s') %(wh.invoice_id.status_account))
                    if wh.invoice_id.status_account == 'declared':
                        list_line.append(wh.invoice_id.id)
            #raise UserError(('%s') %(list_line)) chivo expiatorio
            rec.tax_municipal.write({'state':'done'})
            self.env['account.move'].search([('id','in',list_line)]).write({'status_account':'done'})
        return True