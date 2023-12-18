from odoo import models

class OrdenDeVentaTalonario(models.AbstractModel):
    _name = 'report.company_dependent_fields.orden_de_venta_talonario'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, ordenes_de_venta):

        for orden_de_venta in ordenes_de_venta:

            sheet = workbook.add_worksheet("ORDEN DE VENTA: " + orden_de_venta.name)
            sheet.set_paper(5)
            sheet.set_margins(left=0.354331, right=0.0393701, top=0.23622, bottom=0.19685)
            fmt_ciudad = workbook.add_format({'bold': True, 'font_size': 12, 'align': 'center'})

            sheet.set_column(0, 0, 5.57)
            sheet.set_row(6, 32.5)
            sheet.set_column(1, 1, 8.14)
            sheet.set_column(2, 2, 3.17)
            sheet.set_column(2, 2, 3.17)

            sheet.write(6, 1, "NAGUANAGUA", fmt_ciudad)

            sheet.set_column(3, 3, 8.14)
            sheet.set_column(4, 4, 8.14)
            fmt_fecha = workbook.add_format({'bold': True, 'font_size': 12, 'align': 'center' })
            sheet.merge_range(6, 3, 6, 4,  "02     06     2023", fmt_fecha)

            sheet.set_column(5, 5, 8.14)
            sheet.set_column(6, 6, 8.14)
            sheet.set_column(7, 7, 11.43)
            sheet.set_column(8, 8, 8.14)
            sheet.set_column(9, 9, 3.43)
            sheet.set_column(10, 10, 15.29)
            sheet.set_row(7, 7.25)

            fmt_cliente_tag = workbook.add_format({'bold': True, 'font_size': 12, 'align': 'left' })
            sheet.merge_range(8,2, 8, 10, orden_de_venta.partner_id.name , fmt_cliente_tag)


