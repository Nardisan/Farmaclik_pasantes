# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _, tools
from datetime import datetime
from odoo.exceptions import Warning, UserError,ValidationError
import operator

class IgtfWizard(models.TransientModel):
    _name = 'igtf.wizard'
    _description ='Reporte de IGTF'

    date_start = fields.Datetime('Fecha Inicio')
    date_end = fields.Datetime('Fecha Fin')
    partner_id = fields.Many2one('res.partner', string='Proveedor ')
    diario = fields.Many2one('account.journal', string="Diario Bancario", domain=[('type','in',('bank','cash'))])

    def report_igtf(self):
        final = []
        advance = []
        date_clause = ""
        query_params = []
        type_invoice_view = ''
        estatus_view = ''
        if self.date_start:
            date_clause += " AND asiento.date >= %s"
            query_params.append(self.date_start)
        if self.date_end:
            date_clause += " AND asiento.date <= %s"
            query_params.append(self.date_end)
        if self.partner_id:
            date_clause += " AND pagos.partner_id = %s"
            query_params.append(self.partner_id.id)
        if self.diario:
            date_clause += " AND asiento.journal_id = %s"
            query_params.append(self.diario.id)

        sql_payment = ("""
        SELECT pagos.amount as monto_pago, asiento.date as fecha,  asiento.amount_total as monto_igtf, 
        (SELECT account_journal.name 
        FROM  account_journal 
        WHERE asiento.journal_id = account_journal.id) as diario_pago,
        prov_cli.name as contacto, prov_cli.rif as rif  
        FROM account_payment as pagos 
        INNER JOIN account_move as asiento on asiento.id=pagos.move_itf_id
        INNER JOIN res_partner as prov_cli ON prov_cli.id = pagos.partner_id
        WHERE asiento.state = 'posted' {date_clause}
                                """.format(date_clause=date_clause))
       
        self.env.cr.execute(sql_payment, query_params)
        query_result = self.env.cr.dictfetchall()
        # sql_advance =("""
        # SELECT pagos.amount_advance as monto_pago, asiento.date as fecha,  asiento.amount_total as monto_igtf, 
        #         (SELECT account_journal.name 
        #         FROM  account_journal 
        #         WHERE asiento.journal_id = account_journal.id) as diario_pago,
        #         prov_cli.name as contacto, prov_cli.rif as rif 
        #         FROM account_advanced_payment as pagos  
        #         INNER JOIN account_move as asiento on asiento.id=pagos.move_itf_id
        #         INNER JOIN res_partner as prov_cli ON prov_cli.id = pagos.partner_id
        #         WHERE asiento.state = 'posted' {date_clause}
        #                             """.format(date_clause=date_clause))
        # self.env.cr.execute(sql_advance,query_params)
        # query_result2 = self.env.cr.dictfetchall()

        
        if len(query_result)>0:
            for row in query_result:

                final.append({
                    'rif': row['rif'],
                    'contacto': row['contacto'],
                    'diario_pago': row['diario_pago'],
                    'fecha': row['fecha'],
                    'monto_pago': row['monto_pago'],
                    'monto_igtf': row['monto_igtf'],
                    })
        # if len(query_result2)>0:
        #     for row in query_result2:

        #         advance.append({
        #             'rif': row['rif'],
        #             'contacto': row['contacto'],
        #             'diario_pago': row['diario_pago'],
        #             'fecha': row['fecha'],
        #             'monto_pago': row['monto_pago'],
        #             'monto_igtf': row['monto_igtf'],
        #             })
        
        if  not query_result:
            raise UserError(_("No hay datos para imprimir"))

        #advance = sorted(advance, key= operator.itemgetter('fecha'), reverse=False)
        final = sorted(final, key= operator.itemgetter('fecha'), reverse=False)

        data = {
            'ids': self.ids,
            'model': self._name,
            'diario': self.diario.name if self.diario.name else '',
            'final': final,
            #'advance': advance,
            'date_start': self.date_start.date() if self.date_start else '',
            'date_end': self.date_end.date() if self.date_end else '',
            'partner_id': self.partner_id.rif+' '+self.partner_id.name if self.partner_id else '',
        }

        return self.env.ref('eu_withholding_itf.igtf_report').report_action(self, data=data)

