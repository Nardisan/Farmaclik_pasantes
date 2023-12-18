# -*- coding: utf-8 -*-
from datetime import timedelta
import collections
import base64

from odoo import api, fields, models, tools, _
from odoo import models, fields, api, exceptions, _
from odoo.addons import decimal_precision as dp
from odoo.tools import float_compare, float_is_zero
from odoo.exceptions import UserError, RedirectWarning, ValidationError
import calendar

TYPE2JOURNAL = {
    'out_invoice': 'sale',
    'in_invoice': 'purchase',
    'out_refund': 'sale',
    'in_refund': 'purchase',
}


class AccountWhIva(models.Model):
    _name = "account.wh.iva"
    _inherit = ['mail.thread']
    _description = "Withholding Vat"
    _rec_name = "number"
    _order = 'create_date desc, id desc'
    
    def name_get(self):
        result = []
        for wh in self:
            result.append((wh.id, "%s" % (wh.number or wh.customer_doc_number or str(wh.partner_id.name)+', '+str(wh.id) or '')))
        return result

    def action_cancel_draft(self):
        for wh in self:
            for whl in wh.wh_lines:
                if whl.state=='withold':
                    raise UserError(_('No se puede cancelar una retención IVA con una factura declarada.'))
            wh.state='cancel'
            wh.wh_lines = False
            for whl in wh.wh_lines:
                whl.invoice_id.wh_id = False

    def action_draft(self):
        for wh in self:
            wh.state = 'draft';
    #def action_update(self):
    #    for rec in self.wh_lines:
    #        rec.invoice_id.create_lines_retention(self)
    
    def action_confirm(self):
        for hw in self:
            if hw.wh_lines:
                for hwl in hw.wh_lines:
                    if hwl.state == 'draft':
                        hwl.write({'move_id':hwl.invoice_id.id, 'state':'confirmed'})
                        hwl.invoice_id.create_lines_retention(self)
            else:
                raise UserError(_('No se puede confirmar una retención sin asociar facturas.'))
        return self.write({'state': 'confirmed',
                    'number': self.env['ir.sequence'].next_by_code('account.wh.iva.in_invoice') if self.move_type in ('in_invoice', 'in_refund') and not self.number else self.number or ''})
       
    def action_declaration(self):
        for hw in self:
            for hwl in hw.wh_lines:
                if hwl.state=='confirmed':
                    hwl.invoice_id.action_post()
        return self.write({'state': 'withhold'})

    @api.model
    def _default_journal(self):
        if self._context.get('default_journal_id', False):
            return self.env['account.journal'].browse(self._context.get('default_journal_id'))
        inv_move_type = self._context.get('move_type', 'out_invoice')
        inv_move_types = inv_move_type if isinstance(inv_move_type, list) else [inv_move_type]
        company_id = self._context.get('company_id', self.env.user.company_id.id)
        domain = [('company_id', '=', company_id)]
        return self.env['account.journal'].search(domain, limit=1)

    @api.depends('wh_lines.ret_amount','wh_lines.state','wh_lines')
    def _get_amount_total(self):
        for wh in self:
            wh.total_tax_ret = round(sum(wh.wh_lines.filtered(lambda whl: whl.state != 'annulled').mapped('ret_amount')), 2)
            
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        vals = []
        domain = {}
        warning = {}
        if self.partner_id:
            inv_ids = []
            for wh in self:
                invoice_ids = self.env['account.move'].search(
                    [
                        ('partner_id', '=', wh.partner_id.id),
                        ('state', '=', 'draft'),
                        ('move_type', '=', wh.move_type),
                        ('wh_id', '=', False),
                        
                    ],
                limit=1)
                if not invoice_ids:
                    self.partner_id = False
                    self.wh_lines = False
                    warning = {
                        'title': _('Aviso!'),
                        'message': _('Este proveedor no tiene facturas para generar retención.'),
                    }
                    return {'warning': warning}
                else:
                    for inv in invoice_ids:
                        tax_list = []
                        if inv.amount_total > 0:
                            tax_list.append(self.id)
                            inv_ids.append([0, 0, {
                                'invoice_id': inv.id,
                                'ret_tax': inv.invoice_line_ids.tax_ids,
                                'base_tax': inv.amount_untaxed,
                                'state': 'draft',
                                'amount_tax': inv.amount_tax,
                                'rate_amount': 100.00 if inv.retention=='03-ordinary' else 75.0 if inv.retention=='02-special' else 0,
                            }])

                    vals = {'wh_lines': inv_ids}
                    return {'value': vals}
    
    @api.onchange('partner_id')
    @api.model
    def _get_default_witholding_account(self):
        for wh in self:
            if wh.move_type == 'out_invoice' or wh.move_type == 'out_refund':
                wh.account_id = wh.company_id.sale_iva_ret_account.id
            else:
                wh.account_id = wh.company_id.purchase_iva_ret_account.id
    
    def act_getfile(self,wh_id,tax_period):
        wh_iva_obj = self.env['account.wh.iva']
        zero = 0
        r=''
        rs=''
        type_doc = ''
        if not self.env.user.company_id.rif:
            raise UserError('El RIF para la compañía no ha sido establecido.')
        rif = r.join(self.env.user.company_id.rif.split('-'))
        content = ''
        for wh in wh_id:
            move_type = 'C' if wh.move_type in ('in_invoice','in_refund') else 'V'
            
            if wh.wh_lines.invoice_id.transaction_type == '01-reg':
                type_doc = '01'
            if wh.wh_lines.invoice_id.transaction_type  == '02-complemento' and wh.wh_lines.invoice_id.parent_id:
                type_doc = '03'
            if wh.wh_lines.invoice_id.transaction_type  == '02-complemento' and wh.wh_lines.invoice_id.debit_origin_id:
                type_doc = '02'
            
            # if wh.move_type == 'in_refund':
            #     type_doc = '03'
            base_imponible = 0
            for whl in wh.wh_lines:
                if not wh.partner_id.rif:
                    raise UserError('Debe establecer el RIF del contacto para poder realizar la retención.')
                if whl.state != 'annulled':
                    base_imponible += (whl.amount_tax/(whl.ret_tax.amount/100))
                    content += '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%.2f\t%.2f\t%.2f\t%s\t%s\t%.2f\t%.2f\t%s\n'%(
                    rif,
                    tax_period,
                    wh.date,
                    move_type,
                    type_doc,
                    rs.join(wh.partner_id.rif.split('-')),
                    whl.invoice_id.vendor_invoice_number,
                    whl.invoice_id.ref_credit if whl.invoice_id.move_type=='in_refund' else whl.invoice_id.nro_control,
                    abs(whl.invoice_id.amount_total * whl.invoice_id.manual_currency_exchange_rate) if whl.invoice_id.currency_id == whl.invoice_id.company_id.currency_id else (whl.invoice_id.amount_total),
                    abs(whl.base_tax * whl.invoice_id.manual_currency_exchange_rate) if whl.invoice_id.currency_id == whl.invoice_id.company_id.currency_id else (base_imponible /  whl.invoice_id.manual_currency_exchange_rate),
                    abs(whl.ret_amount * whl.invoice_id.manual_currency_exchange_rate) if whl.invoice_id.currency_id == whl.invoice_id.company_id.currency_id else (whl.ret_amount  /  whl.invoice_id.manual_currency_exchange_rate),
                    whl.invoice_id.parent_id.vendor_invoice_number if whl.invoice_id.move_type=='in_refund' else whl.invoice_id.debit_origin_id.vendor_invoice_number if whl.invoice_id.debit_origin_id else zero,
                    wh.number,
                    (sum(whl.invoice_id.invoice_line_ids.filtered(lambda line: not line.tax_ids or sum(line.tax_ids.mapped('amount')) == 0).mapped('price_subtotal'))* whl.invoice_id.manual_currency_exchange_rate) if whl.invoice_id.currency_id == whl.invoice_id.company_id.currency_id else (sum(whl.invoice_id.invoice_line_ids.filtered(lambda line: not line.tax_ids or sum(line.tax_ids.mapped('amount')) == 0).mapped('price_subtotal'))),
                    #(whl.ret_tax.amount * whl.invoice_id.manual_currency_exchange_rate),
                    whl.ret_tax.amount,
                    zero)
        return base64.encodebytes(bytes(content, 'utf-8'))

    def download_txt(self):
        name = '%s.txt' %(self.number)
        today = fields.Date.today().split('-')
        tax_period = today[0]+today[1] if not self.period else self.period
        content = self.act_getfile(self,tax_period)
        this = self.env['account.iva.txt.export'].create({'state': 'get', 'data': content, 'name': name})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.iva.txt.export',
            'view_mode': 'form',
            'res_id': this.id,
            'views': [(False, 'form')],
            'target': 'new',
        }
        
    def create_attachment(self, content,company_id):
        ir_attachment = self.env['ir.attachment']
        value = {u'name': u'Reporte TXT de retención.txt',
                u'url': False,
                u'company_id': company_id.id, 
                u'type': u'binary',
                u'public': False, 
                u'datas': content, 
                #u'mimetype': 'txt',
                u'description': False}
        file_txt_id = ir_attachment.create(value)
        return file_txt_id
    
    def wh_refund_invoice(self,invoice_id):
        wh_lines = self.env['account.wh.iva.line'].search([('invoice_id', '=', invoice_id)])
        for whl in wh_lines:
            whl.refund=True
        return True
        
    journal_id = fields.Many2one('account.journal', string='Journal',
                                 required=True, readonly=True, states={'draft': [('readonly', False)]},
                                 default=_default_journal,
                                 domain="[('type', 'in', {'out_invoice': ['sale'], 'out_refund': ['sale'], 'in_refund': ['purchase'], 'in_invoice': ['purchase']}.get(move_type, [])), ('company_id', '=', company_id)]")
    number = fields.Char(
        string='Número de Comprobante', size=32, readonly=True,
        help="Número de comprobante")
    move_type = fields.Selection([
            ('out_invoice','Customer Invoice'),
            ('in_invoice','Vendor Bill'),
            ('out_refund','Customer Refund'),
            ('in_refund','Vendor Refund'),
    ], string='Tipo', readonly=True,
        help="Tipo de retención")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('withhold', 'Withhold'),
        ('declared', 'Declared'),
        ('done', 'Done'),
        ('annulled', 'Annulled'),
        ('cancel', 'Cancel')
    ], string='Estatus', readonly=True, default='draft',
        help="estatus de la retención")
    date = fields.Date(
        string='Date', readonly=True, required=True,
        default = fields.Date.context_today,
        states={'draft': [('readonly', False)]},
        help="Date of the issuance of the withholding document")
    account_id = fields.Many2one(
        'account.account', compute='_get_default_witholding_account', string='Cuenta', required=True, readonly=True,
        states={'draft': [('readonly', False)]}, 
        help="Cuenta contable de la retención.")
    currency_id = fields.Many2one(
        'res.currency', string='Moneda', required=True, readonly=True,
        states={'draft': [('readonly', False)]}, help="Moneda",
        default=lambda self: self.env.user.company_id.currency_id.id)
    company_id = fields.Many2one(
        'res.company', string='Compañia', required=True, readonly=True,
        default=lambda self: self.env.user.company_id.id,
        help="Company")
    partner_id = fields.Many2one(
        'res.partner', string='Razón Social', readonly=True, required=True,
        states={'draft': [('readonly', False)]},
        help="Cliente o proveedor a retener")
    wh_lines = fields.One2many(
        'account.wh.iva.line', 'retention_id',
        string='Lineas de retención de iva', readonly=False,
        help="Lineas de retención de IVA")
    total_tax_ret = fields.Monetary(
        string='Monto total retenido', digits=dp.get_precision('Withhold'),
        compute='_get_amount_total', 
        help="Calcula el monto total retenido de este comprobante")
    customer_doc_number = fields.Char(string="Nro Comprobante Cliente",
        help="Número de comprobante de retención emitido por el Cliente.")
    file_txt_id = fields.Many2many('ir.attachment',
        'account_wh_attachment_rel', 'wh_id', 'attachment_id', string="File TXT", copy=False, readonly=True)
    period = fields.Char(
        string='Tax Period', size=64, readonly=True,
        help="Tax Period")
    payment_id = fields.Many2one('account.payment', 'Pago Relacionado', 
                            readonly=True, 
                            copy=False, 
                            help="",)
    move_paid_id = fields.Many2one('account.move', 'Move Paid', 
                            readonly=True, 
                            copy=False, 
                            help="",)
    asiento_iva = fields.Many2one('account.move', 'Asiento Relacionado', 
                            readonly=True, 
                            copy=False, 
                            help="",)
    refund = fields.Boolean(string='Refund', default=False, help="")
    manual_currency_exchange_rate = fields.Float(string='Tipo de tasa manual', digits=(20,12))
    
    def action_withhold_iva_send(self):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('l10n_ve_retencion_iva', 'email_template_wh_iva')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict()
        ctx.update({
            'default_model': 'account.wh.iva',
            'active_model': 'account.wh.iva',
            'active_id': self.ids[0],
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            #'custom_layout': "l10n_ve_retencion_iva.mail_template_data_notification_email_wh_iva"
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }
    
    def print_wh_iva_receipt(self):
        self.ensure_one()
        return self.env['report'].get_action(self, 'l10n_ve_retencion_iva.report_withholding_receipt_iva')

    @api.model
    def create(self, vals):
        wh_iva = super(AccountWhIva, self).create(vals)
        for wh in wh_iva.wh_lines:
            wh.invoice_id.write({'wh_id': wh_iva.id})
        return wh_iva
    
    def write(self, vals):
        wh_iva = super(AccountWhIva, self).write(vals)
        for inv in self:
            self.env['account.move'].search([('wh_id', '=', inv.id )]).write({'wh_id':False })
            for wh in inv.wh_lines:
                wh.invoice_id.write({'wh_id': inv.id})
        return wh_iva

    
    def unlink(self):
        for wh in self:
            if wh.state not in ('draft', 'cancel'):
                raise UserError(_('No puede eliminar retenciones confirmadas.'))
        return super(AccountWhIva, self).unlink()
    
    
class AccountWhIvaLine(models.Model):
    _name = "account.wh.iva.line"
    _description = "Lineas de retención de IVA"

    @api.model
    def _get_ret_amount(self):
        for wh in self:
            round_curr = wh.retention_id.currency_id.round
            wh.ret_amount = round((wh.rate_amount * wh.amount_tax / 100), 2)

    @api.model
    def _get_sub_total(self):
        for wh in self:
            wh.sub_total = round(wh.base_tax + wh.amount_tax, 2)

    retention_id = fields.Many2one(
        'account.wh.iva', string='Vat Withholding',
        ondelete='cascade', help="Vat Withholding")
    invoice_id = fields.Many2one(
        'account.move', string='Factura', required=True, readonly=False,
        ondelete='restrict', help="Factura a retener")
    ret_tax = fields.Many2one('account.tax', string='Impuesto a retener', required=True,readonly=False,
        help="Impuesto a retener.")
    base_tax = fields.Float(string='Base Imponible', digits=dp.get_precision('Withhold'),readonly=False,
        help='Base imponible del impuesto')
    amount_tax = fields.Float(string='IVA Facturado', digits=dp.get_precision('Withhold'),
                              help="Monto a retener", readonly=False)
    rate_amount = fields.Float(string='% Retenido', digits=dp.get_precision('Withhold'), readonly=False,
                               help="Porcentaje aplicado al monto a retener")
    ret_amount = fields.Float(string='IVA Retenido', digits=dp.get_precision('Withhold'),
                              help="Monto a retener", readonly=False, compute='_get_ret_amount')
    sub_total = fields.Float(string='Total Compra', digits=dp.get_precision('Withhold'),
                              help="Total Compra", readonly=False, compute='_get_sub_total')
    move_id = fields.Many2one('account.move', 'Accounting Entry', readonly=False, copy=False)
    active = fields.Boolean('Active', default=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('withhold', 'Withhold'),
        ('declared', 'Declared'),
        ('done', 'Done'),
        ('annulled', 'Annulled'),
        ('cancel', 'Cancel')
    ], string='Status', readonly=True, default='draft',
        help="Status of Withholding")
    payments_three = fields.Boolean(string='Payments to third parties', default=False)

    #def unlink(self):
    #    for wh in self:
    #        if wh.state!='draft':
    #            raise UserError(_('Una retención IVA declarada no puede ser eliminada.'))
    #            return
    #    return super(AccountWhIvaLine, self).unlink()


