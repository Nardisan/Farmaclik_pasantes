# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _, tools
from datetime import datetime
from odoo.exceptions import Warning, UserError,ValidationError
import pytz
import datetime

class IslrWizardArcv(models.TransientModel):
    _name = 'islr.wizard.arcv'

    date_start = fields.Date('Fecha Inicio',required = True)
    date_end = fields.Date('Fecha Fin',required = True)
    partner_id = fields.Many2one('res.partner', string='Proveedor o Cliente',required = True)
    move_type = fields.Selection([
        ('in_invoice', 'Cuentas Por Pagar'),
        ('out_invoice', 'Cuentas Por Cobrar'),
        ('in_refund', 'Notas de Credito'),
    ], string='Retenciones de ISLR', default='in_invoice', required=True,)

    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
        string="Compañia",
        readonly=True,
    )

    hora_actual = fields.Char(string="Hora actual",compute="_hora_pesaje")   
    
    def _hora_pesaje(self):
        self.hora_actual = (datetime.datetime.now()).astimezone(pytz.timezone(self.env.user.tz)).strftime('%I:%M %p')

    def report_islr_arcv(self):

        tipo_persona = ''
        documento = 'CEDULA DE IDENTIDAD'

        if self.partner_id.vat:
            if self.partner_id.vat.find('-'):
                vat = self.partner_id.vat.split('-')
                if vat[0] in ['J','G']:
                    documento = 'NUMERO DE RIF'
                if vat[0] in ['V','E']:
                    if len(vat[1]) > 8:
                        documento = 'NUMERO DE RIF'
                    else:
                        documento = 'CEDULA DE IDENTIDAD'
                if vat[0] == 'P':
                    documento = 'NUMERO DE PASAPORTE'

        if self.partner_id.residence_type == 'SR':
            tipo_persona = 'SIN RIF'
        elif self.partner_id.residence_type == 'R':
            tipo_persona = 'RESIDENCIADO'
        elif self.partner_id.residence_type == 'NR':
            tipo_persona = 'NO RESIDENCIADO'
        elif self.partner_id.residence_type == 'D':
            tipo_persona = 'DOMICILIADO'
        elif self.partner_id.residence_type == 'ND':
            tipo_persona = 'NO DOMICILIADO'

        account_wh_islr = self.env['account.wh.islr'].search([
            ('partner_id','=',self.partner_id.id),
            ('date','>=',self.date_start),
            ('date','<=',self.date_end),
            ('move_type','=',self.move_type),
            ('company_id','=',self.company_id.id),
        ], order='date ASC')

        final = []
            
        if account_wh_islr:
            for row in account_wh_islr:
                final.append({
                    #datos de la retencion
                    'comprobante': row.number[8:] if row.number else '',
                    'fecha': row.date,
                    'anio': row.date.year,
                    'mes': row.date.month,
                    'dia': row.date.day,
                    'monto_total': row.invoice_rel.amount_total,
                    'porcentaje_islr': sum(row.withholding_line.mapped('porc_islr')),
                    'monto_base': sum(row.withholding_line.mapped('base_tax')),
                    'monto_factura': sum(row.withholding_line.mapped('amount_invoice')),
                    'retenido': sum(row.withholding_line.mapped('ret_amount')),
                    'sustraendo': row.withholding_line.mapped('sustraendo'),
                    'monto_sustraendo': sum(row.withholding_line.mapped('sus_amount')),
                })
        else:
            raise UserError(_("No hay datos para imprimir"))

        data = {
            'ids': self.ids,
            'model': self._name,
            'final': final,
            'date_start': self.date_start if self.date_start else '',
            'date_end': self.date_end if self.date_end else '',
            'move_type': self.move_type,
            'hora_actual': self.hora_actual,
            #datos del cliente o proveedor
            'partner_name': self.partner_id.name if self.partner_id.name else '',
            'partner_rif': self.partner_id.rif if self.partner_id.rif else '',
            'partner_vat': self.partner_id.vat if self.partner_id.vat else '',
            'partner_street': self.partner_id.street if self.partner_id.street else '',
            'partner_residence_type': tipo_persona,
            'partner_pais': self.partner_id.country_id.code if self.partner_id.country_id else '',
            'partner_is_company': self.partner_id.is_company,
            'documento': documento,
            #datos de la compañia
            'company_id': self.company_id.id,
            'company_name': self.company_id.name if self.company_id.name else '',
            'company_rif': self.company_id.rif if self.company_id.rif else '',
            'anio_fiscal': self.company_id.fiscalyear_last_month,
            'dia_fiscal': self.company_id.fiscalyear_last_day,
            'direccion': self.company_id.street if self.company_id.street else '',
            'estado': self.company_id.state_id.name if self.company_id.state_id else '',
            'telefono': self.company_id.phone if self.company_id.phone else '',
            'firma': self.company_id.firma if self.company_id.firma else False,
        }

        return self.env.ref('eu_reporte_islr_arcv.islr_arcv_report').report_action(self, data=data)

