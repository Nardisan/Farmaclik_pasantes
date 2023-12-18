# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from pytz import timezone
from odoo.exceptions import UserError


class AccountMoveCreditMotivo(models.Model):
    _name = 'account.move.credit.motivo'
    _description = 'Motivo de Nota de Crédito'
    _order = 'id desc'

    name = fields.Char(
        string='Nombre',
        index=True,
    )


class AccountMove(models.Model):
    _inherit = 'account.move'

    parent_id = fields.Many2one('account.move', string='Factura Padre', index=True)
    children_ids = fields.One2many('account.move','parent_id', string='Factura Hijas', index=True)
    num_credit = fields.Char(string="Número de Nota de Crédito")
    ref_credit = fields.Char(string="Nro Control Nota de Crédito")
    motivos = fields.Many2one('account.move.credit.motivo', string='Motivo', index=True)
    with_nc = fields.Boolean(string='¿Tiene Nota de Crédito?', default=False,readonly=True)
    parent_count = fields.Integer("Notas de Crédito", compute='_compute_payment_count')

    def show_parent_invoice(self):
        return {
            'name': _('Nota de Crédito'),
            'view_mode': 'tree',
            'res_model': 'account.move',
            'view_id': False,
            'views': [(self.env.ref('account.view_move_tree').id, 'tree')],
            'type': 'ir.actions.act_window',
            'domain': [('parent_id', '=', self.id)],
            'context': {'create': False},
        }
    def _compute_payment_count(self):
        for move in self:
            move.parent_count = self.env['account.move'].search_count([('parent_id', '=', move.id)])

class AccountMoveReversal(models.TransientModel):
    """
    Account move reversal wizard, it cancel an account move by reversing it.
    """
    _inherit = 'account.move.reversal'

    def reverse_moves(self):
        moves = self.env['account.move'].browse(self.env.context['active_ids']) if self.env.context.get('active_model') == 'account.move' else self.move_id

        # Create default values.
        default_values_list = []
        for move in moves:
            default_values_list.append({
                'ref': _('Reversal of: %s, %s') % (move.name, self.reason) if self.reason else _('Reversal of: %s') % (move.name),
                'date': self.date or move.date,
                'invoice_date': move.is_invoice(include_receipts=True) and (self.date or move.date) or False,
                'journal_id': self.journal_id and self.journal_id.id or move.journal_id.id,
                'invoice_payment_term_id': None,
                'auto_post': True if self.date > fields.Date.context_today(self) else False,
                'parent_id': move.id,
            })
            move.with_nc = True

        # Handle reverse method.
        if self.refund_method == 'cancel':
            if any([vals.get('auto_post', False) for vals in default_values_list]):
                new_moves = moves._reverse_moves(default_values_list)
            else:
                new_moves = moves._reverse_moves(default_values_list, cancel=True)
        elif self.refund_method == 'modify':
            moves._reverse_moves(default_values_list, cancel=True)
            moves_vals_list = []
            for move in moves.with_context(include_business_fields=True):
                moves_vals_list.append(move.copy_data({
                    'invoice_payment_ref': move.name,
                    'date': self.date or move.date,
                    'parent_id': move.id,
                })[0])
            new_moves = self.env['account.move'].create(moves_vals_list)
        elif self.refund_method == 'refund':
            new_moves = moves._reverse_moves(default_values_list)
        else:
            return

        # Create action.
        action = {
            'name': _('Reverse Moves'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
        }
        if len(new_moves) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': new_moves.id,
            })
        else:
            action.update({
                'view_mode': 'tree,form',
                'domain': [('id', 'in', new_moves.ids)],
            })
        return action
