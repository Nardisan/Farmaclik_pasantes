# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.depends('invoice_line_ids.price_subtotal', 'withholding_id.amount_total', 'withholding_id.withholding_line')
    def _compute_wh_islr(self):
        for invoice in self:
            invoice.amount_wh_islr = 0.0
            for whl in invoice.withholding_id:
                invoice.amount_wh_islr = round(whl.amount_total,2)

    @api.depends('invoice_line_ids.price_subtotal', 'withholding_id.amount_total', 'withholding_id.withholding_line','company_id','currency_id','manual_currency_exchange_rate')
    def _compute_islr(self):
        for invoice in self:
            invoice.amount_islr = 0.0
            for whl in invoice.withholding_id:
                invoice.amount_islr = round(whl.amount_total,2) if invoice.currency_id == self.env.company.currency_id else round(whl.amount_total,2) * invoice.manual_currency_exchange_rate

    #Columns
    withholding_id = fields.Many2one('account.wh.islr', 'Withholding', readonly=True, copy=False)
    amount_wh_islr = fields.Monetary(string='Importe de retención de ISLR (Company Currency)', copy=False, digits=dp.get_precision('Withhold'),
                                    readonly=True, store=True, compute='_compute_wh_islr', track_visibility='onchange')
    amount_islr = fields.Monetary(string='Importe de retención de ISLR', copy=False, digits=dp.get_precision('Withhold'),
                                    readonly=True, store=True, compute='_compute_islr', track_visibility='onchange')
    can_delete_islr = fields.Boolean('Puede eliminar la retención de ISLR',default=False,copy=False)
    
    @api.model #Crea los apunte contables
    def create_lines_retentions(self, wh_islr_obj):
        for rec in self:
            if not wh_islr_obj.asiento_islr:
                if rec.move_type == 'in_invoice':
                    vals = {
                        'date': fields.Datetime.now(),
                        'journal_id': rec.company_id.journal_islr.id,
                        'line_ids': False,
                        'state': 'draft',
                        'partner_id': rec.partner_id.id,
                        'move_type':'entry',
                        'currency_id': self.env.company.currency_id.parent_id.id,
                        'manual_currency_exchange_rate':rec.manual_currency_exchange_rate,
                        'apply_manual_currency_exchange':True,
                    }
                    move_apply_obj = self.env['account.move']
                    move_apply_id = move_apply_obj.create(vals)
                    wh_islr_obj.asiento_islr = move_apply_id.id
                    amount_currency = 0
                    if rec.currency_id == self.company_id.currency_id:
                        amount_currency = round(rec.amount_wh_islr * rec.manual_currency_exchange_rate,2)
                    else:
                        amount_currency = round(rec.amount_wh_islr * rec.manual_currency_exchange_rate,2)
                    move_advance = {
                        'account_id': rec.partner_id.property_account_receivable_id.id if rec.move_type in ('out_invoice', 'in_refund', 'out_receipt') else rec.partner_id.property_account_payable_id.id,
                        'company_id': self.env.company.id,
                        'currency_id': rec.currency_id.id if rec.currency_id != rec.company_id.currency_id else rec.currency_id.parent_id.id,
                        'date_maturity': False,
                        'ref': rec.ref,
                        'date': fields.Datetime.now(),
                        'partner_id': rec.partner_id.id,
                        'move_id': move_apply_id.id,
                        'name': 'Retención de ISLR Proveedor',
                        'journal_id': rec.journal_id.id,
                        'debit': rec.amount_wh_islr,
                        'credit': 0.0,
                        'amount_currency': amount_currency
                    }
                    asiento = move_advance
                    move_line_obj = self.env['account.move.line']
                    move_line_id1 = move_line_obj.with_context(check_move_validity=False).create(asiento)
                    asiento['account_id'] = rec.company_id.purchase_islr_ret_account_id.id
                    asiento['debit'] = 0.0
                    asiento['credit'] = rec.amount_wh_islr
                    asiento['amount_currency']  = (amount_currency) *-1
                    move_line_id2 = move_line_obj.create(asiento)
                    move_apply_id._onchange_manual_currency_rate()
                    move_apply_id.action_post()
                   #raise UserError(move_apply_id.mapped('line_ids').filtered(lambda x:x.account_id.user_type_id.type == 'payable').mapped('debit'))
                    rec.can_delete_islr = True
                elif rec.move_type == 'out_invoice':
                    vals = {
                        'date': fields.Datetime.now(),
                        'journal_id': rec.company_id.journal_islr.id,
                        'line_ids': False,
                        'state': 'draft',
                        'partner_id': rec.partner_id.id,
                        'move_type':'entry',
                        'currency_id': self.env.company.currency_id.parent_id.id,
                        'manual_currency_exchange_rate':rec.manual_currency_exchange_rate,
                        'apply_manual_currency_exchange':True,
                    }
                    move_apply_obj = self.env['account.move']
                    move_apply_id = move_apply_obj.create(vals)
                    wh_islr_obj.asiento_islr = move_apply_id.id
                    amount_currency = 0
                    if rec.currency_id == self.company_id.currency_id:
                        amount_currency = round(rec.amount_wh_islr * rec.manual_currency_exchange_rate,2)
                    else:
                        amount_currency = round(rec.amount_wh_islr * rec.manual_currency_exchange_rate,2)
                    move_advance = {
                        'account_id': rec.partner_id.property_account_receivable_id.id if rec.move_type in ('out_invoice', 'in_refund', 'out_receipt') else rec.partner_id.property_account_payable_id.id,
                        'company_id': self.env.company.id,
                        'currency_id': rec.currency_id.id if rec.currency_id != rec.company_id.currency_id else rec.currency_id.parent_id.id,
                        'date_maturity': False,
                        'ref': rec.ref,
                        'date': fields.Datetime.now(),
                        'partner_id': rec.partner_id.id,
                        'move_id': move_apply_id.id,
                        'name': 'Retención de ISLR Cliente',
                        'journal_id': rec.journal_id.id,
                        'credit': rec.amount_wh_islr,
                        'debit': 0.0,
                        'amount_currency': amount_currency *- 1
                    }
                    asiento = move_advance
                    move_line_obj = self.env['account.move.line']
                    move_line_id1 = move_line_obj.with_context(check_move_validity=False).create(asiento)
                    asiento['account_id'] = rec.company_id.sale_islr_ret_account_id.id
                    asiento['credit'] = 0.0
                    asiento['debit'] = rec.amount_wh_islr
                    asiento['amount_currency']  = (amount_currency) 
                    move_line_id2 = move_line_obj.create(asiento)
                    move_apply_id.action_post()
                    rec.can_delete_islr = True
                elif rec.move_type == 'in_refund':
                    vals = {
                        'date': fields.Datetime.now(),
                        'journal_id': rec.company_id.journal_islr.id,
                        'line_ids': False,
                        'state': 'draft',
                        'partner_id': rec.partner_id.id,
                        'move_type':'entry',
                        'currency_id': self.env.company.currency_id.parent_id.id,
                        'manual_currency_exchange_rate':rec.manual_currency_exchange_rate,
                        'apply_manual_currency_exchange':True,
                    }
                    move_apply_obj = self.env['account.move']
                    move_apply_id = move_apply_obj.create(vals)
                    wh_islr_obj.asiento_islr = move_apply_id.id
                    amount_currency = 0
                    if rec.currency_id == self.company_id.currency_id:
                        amount_currency = round(rec.amount_wh_islr * rec.manual_currency_exchange_rate,2)
                    else:
                        amount_currency = round(rec.amount_wh_islr * rec.manual_currency_exchange_rate,2)
                    move_advance = {
                        'account_id': rec.partner_id.property_account_receivable_id.id if rec.move_type in ('out_invoice', 'in_refund', 'out_receipt') else rec.partner_id.property_account_payable_id.id,
                        'company_id': self.env.company.id,
                        'currency_id': rec.currency_id.id if rec.currency_id != rec.company_id.currency_id else rec.currency_id.parent_id.id,
                        'date_maturity': False,
                        'ref': rec.ref,
                        'date': fields.Datetime.now(),
                        'partner_id': rec.partner_id.id,
                        'move_id': move_apply_id.id,
                        'name': 'Retención de ISLR Proveedor',
                        'journal_id': rec.journal_id.id,
                        'debit': rec.amount_wh_islr,
                        'credit': 0.0,
                        'amount_currency': amount_currency
                    }
                    asiento = move_advance
                    move_line_obj = self.env['account.move.line']
                    move_line_id1 = move_line_obj.with_context(check_move_validity=False).create(asiento)
                    asiento['account_id'] = rec.company_id.sale_islr_ret_account_id.id,
                    asiento['debit'] = 0.0
                    asiento['credit'] = rec.amount_wh_islr
                    asiento['amount_currency']  = (amount_currency) *-1
                    move_line_id2 = move_line_obj.create(asiento)
                    move_apply_id.action_post()
                    rec.can_delete_islr = True

   #Crea la retencion
    def create_retentions(self):
        for rec in self:
            lines = []
            ret_amount = 0
            ret_amount_bs = 0
            amount_base_bs = 0
            amount_base = 0
            sus_amount = 0
            valss_retention = {}
            tiene_servicio = False
            for lineas in rec.invoice_line_ids:
                wh_table_retention_line = lineas.get_islr_retentions_dates()
                if wh_table_retention_line:
                    tiene_servicio = True
            if tiene_servicio:
                if rec.move_type == 'in_invoice':
                    porcentaje = 0
                    id_table = False
                    for line in rec.invoice_line_ids:
                        wh_table_retention_line = line.get_islr_retentions_dates()
                        if porcentaje < wh_table_retention_line.percentage:
                            porcentaje = float(wh_table_retention_line.percentage)
                            id_table = wh_table_retention_line.id
                    wh_table_retention_line = self.env['account.withholding.rate.table.line'].search([('id','=',id_table)])
                    if float(rec.amount_untaxed) < float(wh_table_retention_line.apply_up_to):
                        raise UserError(('No aplica retención para facturas menores a: %s')%(float(wh_table_retention_line.apply_up_to)))
                    if rec.currency_id == self.env.company.currency_id:
                        amount_base = float(rec.amount_untaxed * wh_table_retention_line.percentage_amount_base/100)
                        amount_base_bs = float(rec.amount_untaxed * wh_table_retention_line.percentage_amount_base * rec.manual_currency_exchange_rate/100)
                    else:
                        amount_base_bs = float((rec.amount_untaxed * wh_table_retention_line.percentage_amount_base)/100)
                        amount_base = float((rec.amount_untaxed * wh_table_retention_line.percentage_amount_base) / rec.manual_currency_exchange_rate/100)
                    #raise UserError(amount_base_bs)
                    if wh_table_retention_line.sustraendo:
                        ret_amount_bs = float(amount_base_bs * wh_table_retention_line.percentage/100) - float((wh_table_retention_line.table_id.factor * wh_table_retention_line.table_id.tributary_unit.amount)*wh_table_retention_line.percentage)
                        ret_amount = ret_amount_bs / rec.manual_currency_exchange_rate
                        sus_amount = float((wh_table_retention_line.table_id.factor * wh_table_retention_line.table_id.tributary_unit.amount)*wh_table_retention_line.percentage)
                    if not wh_table_retention_line.sustraendo:
                        ret_amount_bs = float(amount_base_bs * wh_table_retention_line.percentage/100)
                        ret_amount = float(amount_base * wh_table_retention_line.percentage/100)
                        sus_amount = 0.00
                    if ret_amount > 0:
                        lines.append([0, False, {
                            'invoice_id': rec.id,  # factura
                            'amount_invoice': amount_base,
                            'amount_invoice_bs': amount_base_bs,
                            'base_tax': rec.amount_untaxed,
                            'porc_islr': porcentaje,
                            'code_withholding_islr': wh_table_retention_line.code,
                            'descripcion': wh_table_retention_line.concept.name,
                            'ret_amount': ret_amount,
                            'ret_amount_bs': ret_amount_bs,
                            'sus_amount': sus_amount,
                            'sustraendo': wh_table_retention_line.sustraendo,
                            'table_id': wh_table_retention_line.id,
                        }])
                    valss_retention = {
                        'name': rec.name,
                        'invoice_rel' : rec.id,
                        'partner_id': rec.partner_id.id,
                        'journal_id': rec.journal_id.id,
                        'date': fields.Datetime.now(),
                        'company_id': rec.company_id.id,
                        'account_id': rec.company_id.purchase_islr_ret_account_id.id,
                        'withholding_line': lines,
                        'move_type':'in_invoice',
                     }
                elif rec.move_type == 'out_invoice':
                    porcentaje = 0
                    id_table = False
                    for line in rec.invoice_line_ids:
                        wh_table_retention_line = line.get_islr_retentions_dates()
                        if porcentaje < wh_table_retention_line.percentage:
                            porcentaje = float(wh_table_retention_line.percentage)
                            id_table = wh_table_retention_line.id
                    wh_table_retention_line = self.env['account.withholding.rate.table.line'].search([('id','=',id_table)])
                    if float(rec.amount_untaxed) < float(wh_table_retention_line.apply_up_to):
                        raise UserError(('No aplica retención para facturas menores a: %s')%(float(wh_table_retention_line.apply_up_to)))
                    if rec.currency_id == self.env.company.currency_id:
                        amount_base = float(rec.amount_untaxed * wh_table_retention_line.percentage_amount_base/100)
                        amount_base_bs = float(rec.amount_untaxed * wh_table_retention_line.percentage_amount_base * rec.manual_currency_exchange_rate/100)
                    else:
                        amount_base_bs = float(rec.amount_untaxed * wh_table_retention_line.percentage_amount_base/100)
                        amount_base = float(rec.amount_untaxed * wh_table_retention_line.percentage_amount_base / rec.manual_currency_exchange_rate/100)
                    if wh_table_retention_line.sustraendo:
                        ret_amount_bs = float(amount_base_bs * wh_table_retention_line.percentage/100) - float((wh_table_retention_line.table_id.factor * wh_table_retention_line.table_id.tributary_unit.amount)*wh_table_retention_line.percentage)
                        ret_amount = ret_amount_bs / rec.manual_currency_exchange_rate
                        sus_amount = float((wh_table_retention_line.table_id.factor * wh_table_retention_line.table_id.tributary_unit.amount)*wh_table_retention_line.percentage)
                    if not wh_table_retention_line.sustraendo:
                        ret_amount_bs = float(amount_base_bs * wh_table_retention_line.percentage/100)
                        ret_amount = float(amount_base * wh_table_retention_line.percentage/100)
                        sus_amount = 0.00
                    if ret_amount > 0:
                        lines.append([0, False, {
                            'invoice_id': rec.id,  # factura
                            'amount_invoice': amount_base,
                            'amount_invoice_bs': amount_base_bs,
                            'base_tax': rec.amount_untaxed,
                            'porc_islr': wh_table_retention_line.percentage,
                            'code_withholding_islr': wh_table_retention_line.code,
                            'descripcion': wh_table_retention_line.concept.name,
                            'ret_amount': ret_amount,
                            'ret_amount_bs': ret_amount_bs,
                            'sus_amount': sus_amount,
                            'sustraendo': wh_table_retention_line.sustraendo,
                            'table_id': wh_table_retention_line.id,
                        }])
                    valss_retention = {
                        'name': rec.name,
                        'invoice_rel' : rec.id,
                        'partner_id': rec.partner_id.id,
                        'journal_id': rec.journal_id.id,
                        'date': fields.Datetime.now(),
                        'company_id': rec.company_id.id,
                        'account_id': rec.company_id.sale_islr_ret_account_id.id,
                        'withholding_line': lines,
                        'move_type': 'out_invoice',
                    }
                elif rec.move_type == 'in_refund':
                    porcentaje = 0
                    id_table = False
                    for line in rec.invoice_line_ids:
                        wh_table_retention_line = line.get_islr_retentions_dates()
                        if porcentaje < wh_table_retention_line.percentage:
                            porcentaje = float(wh_table_retention_line.percentage)
                            id_table = wh_table_retention_line.id
                    wh_table_retention_line = self.env['account.withholding.rate.table.line'].search([('id','=',id_table)])
                    if float(rec.amount_untaxed) < float(wh_table_retention_line.apply_up_to):
                        raise UserError(('No aplica retención para facturas menores a: %s')%(float(wh_table_retention_line.apply_up_to)))
                    if rec.currency_id == self.env.company.currency_id:
                        amount_base = float(rec.amount_untaxed * wh_table_retention_line.percentage_amount_base/100)
                        amount_base_bs = float(rec.amount_untaxed * wh_table_retention_line.percentage_amount_base * rec.manual_currency_exchange_rate/100)
                    else:
                        amount_base_bs = float(rec.amount_untaxed * wh_table_retention_line.percentage_amount_base/100)
                        amount_base = float(rec.amount_untaxed * wh_table_retention_line.percentage_amount_base / rec.manual_currency_exchange_rate/100)
                    if wh_table_retention_line.sustraendo:
                        ret_amount_bs = float(amount_base_bs * wh_table_retention_line.percentage/100) - float((wh_table_retention_line.table_id.factor * wh_table_retention_line.table_id.tributary_unit.amount)*wh_table_retention_line.percentage)
                        ret_amount = ret_amount_bs / rec.manual_currency_exchange_rate
                        sus_amount = float((wh_table_retention_line.table_id.factor * wh_table_retention_line.table_id.tributary_unit.amount)*wh_table_retention_line.percentage)
                    if not wh_table_retention_line.sustraendo:
                        ret_amount_bs = float(amount_base_bs * wh_table_retention_line.percentage/100)
                        ret_amount = float(amount_base * wh_table_retention_line.percentage/100)
                        sus_amount = 0.00
                    if ret_amount > 0:
                        lines.append([0, False, {
                            'invoice_id': rec.id,  # factura
                            'amount_invoice': amount_base,
                            'amount_invoice_bs': amount_base_bs,
                            'base_tax': rec.amount_untaxed,
                            'porc_islr': wh_table_retention_line.percentage,
                            'code_withholding_islr': wh_table_retention_line.code,
                            'descripcion': wh_table_retention_line.concept.name,
                            'ret_amount': ret_amount,
                            'ret_amount_bs': ret_amount_bs,
                            'sus_amount': sus_amount,
                            'sustraendo': wh_table_retention_line.sustraendo,
                            'table_id': wh_table_retention_line.id,
                        }])
                    valss_retention = {
                        'name': rec.name,
                        'invoice_rel' : rec.id,
                        'partner_id': rec.partner_id.id,
                        'journal_id': rec.journal_id.id,
                        'date': fields.Datetime.now(),
                        'company_id': rec.company_id.id,
                        'account_id': rec.company_id.sale_islr_ret_account_id.id,
                        'withholding_line': lines,
                        'move_type': 'in_refund',
                    }
                wh_islr_obj = self.env['account.wh.islr']
                result = wh_islr_obj.create(valss_retention)
                rec.withholding_id = result.id
                total_ret = 0
                for whl in result.withholding_line.filtered(lambda islr: islr.state != ['annulled','cancel']):
                    total_ret += round(whl.ret_amount,2)
                rec.amount_wh_islr = total_ret if total_ret > 0 else 0.0
            if not tiene_servicio:
                return {
                    'name': _('Advertencia !'),
                    'res_model': 'message.islr.warning',
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'context': {'default_warning': _('No se encontraron valores para la generación de retención de ISLR. Debera generarla de forma manual')},
                    'target':'new'
                }

    def action_post_islr(self):
        for inv in self:
            if inv.withholding_id and inv.withholding_id.state == 'draft':
                if inv.withholding_id.withholding_line:
                    for line in inv.withholding_id.withholding_line:
                        if line.state == 'draft':
                            line.write({'move_id':inv.id, 'state':'confirmed'})
                inv.withholding_id.state = 'confirmed'
                inv.create_lines_retentions(inv.withholding_id)
                if inv.withholding_id.state not in 'posted':
                    inv.withholding_id.action_confirm()

    def action_post(self):
        res = super(AccountMove, self).action_post()
        for rec in self:
            if rec.withholding_id and rec.withholding_id.state in ('draft','cancel'):
                rec.withholding_id.action_confirm()
                if rec.move_type not in 'entry':
                    rec.create_lines_retentions(rec.withholding_id)  # Crea los apuntes contables de retencion de islr
                    if rec.withholding_id.asiento_islr.state not in 'posted':
                        rec.withholding_id.asiento_islr.action_post()
        return res

    def button_draft(self):
        '''
        Este metodo se usa para pasar las retenciones a borrador cuando se pasa la factura de publicado a borrador (ISLR)
        :return:
        '''
        for hw in self:
            if hw.withholding_id.state == 'confirmed' or hw.withholding_id.state == 'cancel':
                hw.withholding_id.write({'state': 'draft'})
                hw.withholding_id.asiento_islr.button_draft()
                for hwl in hw.withholding_id.withholding_line:
                    hwl.write({'state': 'draft'})
                #if hw.withholding_id.number:
                #    raise UserError('No se puede eliminar una retención con un correlativo asociado')
                #hw.unlink_liness()
        return super(AccountMove, self).button_draft()

    def button_cancel(self):
        for hw in self:
            if hw.withholding_id.state == 'confirmed' or hw.withholding_id.state == 'draft':
                hw.withholding_id.write({'state': 'cancel'})
                hw.withholding_id.asiento_islr.button_cancel()
                for hwl in hw.withholding_id.withholding_line:
                    hwl.write({'state': 'cancel'})
        return super(AccountMove, self).button_cancel()

    def unlink_liness(self):
        '''
            Este metodo se usa para borrar las lineas de retenciones (ISLR)
            :return:
        '''
        for inv in self:
            if inv.move_type in ('in_invoice','in_refund'):
                lines_retent = inv.env['account.move.line'].search(
                    [('account_id', '=', self.company_id.purchase_islr_ret_account_id.id),
                     ('move_id', '=', inv.id)])
                line_payables = inv.line_ids.filtered(
                    lambda line: line.account_id.user_type_id.type in ('payable'))
            elif inv.move_type in ('out_invoice'):
                lines_retent = inv.env['account.move.line'].search(
                    [('account_id', '=', self.company_id.sale_islr_ret_account_id.id),
                     ('move_id', '=', inv.id)])
                line_payables = inv.line_ids.filtered(
                    lambda line: line.account_id.user_type_id.type == 'receivable')

            for line in lines_retent:
                line_payables.with_context(check_move_validity=False).write({
                    'credit': line_payables['credit'] + line['credit'] if self.move_type in (
                    'in_invoice') else 0.0,
                    'debit': line_payables['debit'] + line['debit'] if self.move_type not in (
                    'in_invoice') else 0.0,
                    })
            lines_retent.unlink()

    def print_withholding_receipt_xml(self): #Boton para crear el comprobante de retencion
        self.ensure_one()
        islr = self.env['account.wh.islr'].search([('id', '=', self.withholding_id.id)])
        return self.env['account.wh.islr'].search([('id', '=', self.withholding_id.id)]).env.ref(
            'l10n_ve_retencion_islr.account_withholding_receipt_report').report_action(islr)

    def delete_retentions(self):

        ret = self.env['account.wh.islr'].search([('id', '=', self.withholding_id.id)])
        if ret.number:
            raise UserError('No se puede eliminar una retención con un correlativo asociado')
        else:
            ret.unlink()
        # self.env['account.move'].search([('id', '=', self.line_ids.withholding_id)]).unlink()

        # (self.mapped('debit') + self.mapped('credit')).unlink()
        # return self.

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
    _inherit='account.move.line'

    def get_islr_retentions_dates(self):
        current_year = fields.Date.context_today(self).year
        wh_rate_table_line = False
        if self.move_id.move_type in ['in_invoice','in_refund']:
            wh_rate_table_line = self.env['account.withholding.rate.table.line'].search([('table_id.year','=',current_year),
                                                                                             ('concept','=',self.product_id.service_concept_retention.id),
                                                                                             ('residence_type','=',self.move_id.partner_id.residence_type),
                                                                                             ('company_type','=',self.move_id.partner_id.company_type),
                                                                                             # ('percentage_amount_base', '=',prueba)
                                                                                             ])
        elif self.move_id.move_type == 'out_invoice':
            wh_rate_table_line = self.env['account.withholding.rate.table.line'].search(
                                                                                        [('table_id.year', '=', current_year),
                                                                                         ('concept', '=', self.product_id.service_concept_retention.id),
                                                                                         ('residence_type', '=', 'D'),
                                                                                         ('company_type', '=', 'company'),
                                                                                         ])
        return wh_rate_table_line

class AccountPayment(models.Model):
    _inherit='account.payment'

    islr_entry = fields.Many2one('account.move',string="Pago de ISLR Relacionado")
    islr_entry_amount = fields.Monetary(string="Monto del Pago de ISLR Relacionado", related="islr_entry.amount_total")
