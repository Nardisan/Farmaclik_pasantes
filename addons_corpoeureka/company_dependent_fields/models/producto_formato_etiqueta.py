from odoo import models

class ProductoFormatoEtiqueta(models.AbstractModel):
    _name = 'report.company_dependent_fields.productos_formato_etiqueta'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, productos):

        sheet = workbook.add_worksheet("Formato Etiqueta")
        sheet.set_paper(1)
        sheet.set_margins(left=0.19685, right=0.19685, top=0.19685, bottom=0.19685)
        fila = 0
        columna = 0
        # 0 4 8

        for producto in productos:
            # One sheet by partner
           
            formato1 = workbook.add_format({'bold': True, 'font_size': 36, 'align': 'left', 'bottom': 1, 'right': 1, 'top': 1})
            formato2 = workbook.add_format({'bold': True, 'font_size': 50, 'align': 'right', 'bottom': 1, 'left': 1, 'top': 1 })
            formato3 = workbook.add_format({'bold': True, 'font_size': 15, 'align': 'center', 'border': 1})
            sheet.set_row(fila, 20)
            sheet.set_row(fila+1, 64.5)
            sheet.set_column(columna, columna, 6.71)
            sheet.set_column(columna+1, columna+1, 14)
            sheet.set_column(columna+2, columna+2, 10)
            sheet.set_column(columna+3, columna+3, 1.57) 
            
            merge_format = workbook.add_format({'bold': True, 'font_size': 12, 'align': 'center', 'border': 1})
            sheet.merge_range(fila, columna, fila, columna+2,  producto.name[:24].upper(), merge_format)
            sheet.write(fila+1, columna, "Ref.", formato3)
            sheet.write(fila+1, columna+1,'{:.0f}'.format(round(producto.list_price * ( 1.16 if producto.taxes_id.name == 'IVA (16.0%) ventas' else 1 ), 2)), formato2)
            sheet.write(fila+1, columna+2, '{:.2f}'.format(round( (producto.list_price * ( 1.16 if producto.taxes_id.name == 'IVA (16.0%) ventas' else 1 ) ) % 1, 2)).replace('0.', ','), formato1)


            if columna == 8:
                fila = fila + 3
                columna = 0
            else:
                columna = columna + 4

            
           
            
            
