# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class MessageWarning(models.TransientModel):
    _name = "message.islr.warning"
    _description = "Advertencia !"
    

    
    warning = fields.Char()
                
    def action_create_islr_retention_manual(self):
        invoice_id = self.env['account.move'].browse(self._context.get('active_id'))
        withholding_id = fields.Many2one('account.wh.islr', 'Withholding', readonly=True, copy=False)
        lines=[]
        lines.append([0, False, {
            'invoice_id': invoice_id.id,  # factura
            'amount_invoice': invoice_id.amount_total,
            'base_tax':invoice_id.amount_untaxed,
            'descripcion': '',
            'edit_amount': True,
            'porc_islr': 0.00,
            'code_withholding_islr': '',
            'ret_amount': 0,
        }])
        valss_retention = {
            'name': invoice_id.name,
            'partner_id': invoice_id.partner_id.id,
            'journal_id': invoice_id.journal_id.id,
            'date': invoice_id.date,
            'company_id': invoice_id.company_id.id,
            'account_id': invoice_id.company_id.sale_islr_ret_account_id.id if invoice_id.move_type == 'out_invoice'else invoice_id.company_id.purchase_islr_ret_account_id.id,
            'move_type': invoice_id.move_type,
            # 'move_type': invoice_id.filtered(lambda invoice: invoice.move_type in ('in_invoice')),
            'withholding_line': lines,
        }
        wh_islr_obj = self.env['account.wh.islr']
        res_id = wh_islr_obj.create(valss_retention)
        return {
            'name': _('Crear Retención de ISLR'),
            'res_model': 'account.wh.islr',
            'res_id': res_id.id,
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'form',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">
                                                       Click to Create for New Documents
                                                    </p>'''),
            'context': {
                    'default_invoice_id': invoice_id.id,
                    'default_partner_id': invoice_id.partner_id.id,
                    'default_name': invoice_id.name,
                    'default_move_type': invoice_id.move_type,
                    'default_withholding_line': lines,
                        },
            'target': 'new',
        }
