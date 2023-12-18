# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _, tools
from datetime import datetime
from odoo.exceptions import Warning, UserError,ValidationError

class IvaWizard(models.TransientModel):
    _name = 'iae.wizard'
    _description="Report IVA"

    date_start = fields.Datetime('Fecha Inicio')
    date_end = fields.Datetime('Fecha Fin')
    partner_id = fields.Many2one('res.partner', string='Proveedor o Cliente')
    state = fields.Selection([
        ('posted', 'Publicado'),
        ('declared', 'Declarado'),
        ('done', 'Pagado'),
    ], string='Estatus de la retención')

    type_invoice = fields.Selection([
        ('in_invoice', 'Cuentas Por Pagar'),
        ('out_invoice', 'Cuentas Por Cobrar'),
    ], string='Retenciones de IAE', default='in_invoice', required=True,)

    def report_iae(self):
        final = []
        date_clause = ""
        query_params = []
        type_invoice_view = ''
        estatus_view = ''
        if self.date_start:
            date_clause += " AND municipality_tax.transaction_date >= %s"
            query_params.append(self.date_start)
        if self.date_end:
            date_clause += " AND municipality_tax.transaction_date <= %s"
            query_params.append(self.date_end)
        if self.partner_id:
            date_clause += " AND res_partner.partner_id = %s"
            query_params.append(self.partner_id.id)
        if self.state:
            date_clause += " AND municipality_tax.state = %s"
            query_params.append(self.state)
            if self.state == 'posted':
                estatus_view = 'Publicado'
            elif self.state == 'declared':
                estatus_view = 'Declarado'
            elif self.state == 'done':
                estatus_view = 'Pagado'

        if self.type_invoice:
            date_clause += " AND municipality_tax.move_type = %s"
            query_params.append(self.type_invoice)
            if self.type_invoice == 'in_invoice':
                type_invoice_view = 'Cuentas Por Pagar'
            else:
                type_invoice_view = 'Cuentas Por Cobrar'

        sql_iae = ("""

           SELECT municipality_tax.name as comprobante ,
            municipality_tax.transaction_date as fecha_comp,
            account_move.vendor_invoice_number as nro_fact,
            account_move.name as nro_facv,
            res_partner.name as proveedor,
            account_move.amount_total as monto_total,
            account_move.amount_untaxed as base_imponible,
            municipality_tax_line.aliquot as alicuota,
            municipality_tax_line.porcentaje_alic as porcentaje,
            municipality_tax.amount as monto_retenido,
            municipality_tax.state as state
            FROM municipality_tax, municipality_tax_line, res_partner, account_move 
            WHERE municipality_tax_line.municipality_tax_id=municipality_tax.id AND
            municipality_tax.partner_id=res_partner.id AND
            account_move.id=municipality_tax.invoice_id AND
            municipality_tax.state != 'cancel' AND municipality_tax.state != 'draft' {date_clause}
            """.format(date_clause=date_clause))

        self.env.cr.execute(sql_iae, query_params)
        query_result = self.env.cr.dictfetchall()
            
        if len(query_result)>0:
            for row in query_result:

                final.append({
                    'comprobante': row['comprobante'],
                    'fecha': row['fecha_comp'],
                    'nro_fac': row['nro_fact'],
                    'nro_facv': row['nro_facv'],
                    'proveedor': row['proveedor'],
                    'monto_total': row['monto_total'],
                    'base_imponible': row['base_imponible'],
                    'alicuota': row['alicuota'],
                    'porcentaje': row['porcentaje'],
                    'monto': row['monto_retenido'],
                    'estatus': row['state'],
                    })
        else:
            raise UserError(_("No hay datos para imprimir"))

        data = {
            'ids': self.ids,
            'model': self._name,
            'state': estatus_view if self.state else '',
            'type_invoice': type_invoice_view if self.type_invoice else '',
            'final': final,
            'date_start': self.date_start.date() if self.date_start else '',
            'date_end': self.date_end.date() if self.date_end else '',
            'partner_id': self.partner_id.rif+' '+self.partner_id.name if self.partner_id else '',
        }

        return self.env.ref('municipality_tax.iae_report').report_action(self, data=data)

