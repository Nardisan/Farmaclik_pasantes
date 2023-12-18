# -*- coding: utf-8 -*-
#############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import models, fields, api
from odoo.exceptions import ValidationError,UserError

class AccountInvoice(models.Model):
    _inherit = 'account.move'

    vendor_invoice_number = fields.Char(string='Nro factura proveedor',
        copy=False,
        help='El número de factura generado por el proveedor' )
    nro_control = fields.Char(string='Nro de Control',
        copy=False,
        help='Nro de control de la factura de proveedor', required=False)
    transaction_type = fields.Selection(([('01-reg','Registro'),
                                          ('02-complemento', 'Complemento'),
                                          ('03-anulacion', 'Anulación'),
                                          ('04-ajuste', 'Ajuste')]), string='Transaction Type', readonly=False,
                                            states={'draft': [('readonly', False)]},
                                            help='This is transaction type', compute='_compute_transaction_type')
    ajust_date = fields.Date(string='Fecha de Ajuste',readonly=False,
                                            states={'draft': [('readonly', False)]})
    
    deductible  =   fields.Boolean('¿No Deducible?')

    @api.depends('move_type', 'state')
    def _compute_transaction_type(self):
        for move in self:
            if move.move_type in ('out_refund','in_refund') and move.state != 'cancel':
                move.transaction_type = '02-complemento'
            elif move.state == 'cancel':
                move.transaction_type = '03-anulacion'
            elif move.debit_origin_id.id != False:
                move.transaction_type = '02-complemento'
            else:
                move.transaction_type = '01-reg'

    @api.constrains('nro_control')
    def _check_control_number(self):
        records = self.env['account.move']
        if self.nro_control:
            invoice_exist = records.search_count([('nro_control', '=', self.nro_control),('id', '!=', self.id),('move_type','in',('out_refund','out_invoice'))])
            if invoice_exist > 0 and self.move_type in ('out_refund','out_invoice'):
                raise ValidationError(("Ya existe una factura con este Número de Control"))
            if self.vendor_invoice_number:
                invoice_exist = records.search_count([('nro_control', '=', self.nro_control),('id', '!=', self.id),('move_type','in',('in_refund','in_invoice')),('partner_id','=',self.partner_id.id),('vendor_invoice_number','=',self.vendor_invoice_number),('state','!=','cancel')])
                if invoice_exist > 0 and self.move_type in ('in_refund','in_invoice'):
                    raise ValidationError(("Ya existe una factura con este Número de Control"))
            return True


    # def action_post(self):
    #     if not self.nro_control and self.move_type != 'entry':
    #         raise UserError('Debe asignarle un número de control a la factura antes de publicarla')
    #     res = super(AccountInvoice, self).action_post()
    #     return res