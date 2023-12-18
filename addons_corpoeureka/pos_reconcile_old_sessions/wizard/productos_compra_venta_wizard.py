import logging
import base64
from io import BytesIO
from odoo import models, fields, _
import xlsxwriter
from odoo.exceptions import Warning, UserError
from datetime import datetime, timedelta


class ProductosCompraVentaWizard(models.TransientModel):
	
	_name = "productos.compra.venta.wizard"
	_description = "Imforme primera compra ultima venta."
	_inherit = 'report.report_xlsx.abstract'
	
	fecha_de_busqueda = fields.Date(string='Fecha de Busqueda', required=True)
	file_name = fields.Char('Nombre De Informe', size=256)
	file = fields.Binary('Informe', readonly=True)
	
	def generar(self):

		file_data = BytesIO()
		workbook = xlsxwriter.Workbook(file_data)

		# try:
		format0 = workbook.add_format({ 'bold': True, 'align':'center', 'valign':'vcenter', 'font_size':10, 'border':1})
		format1 =  workbook.add_format({ 'bold': False, 'align':'center', 'valign':'vcenter', 'font_size':10, 'border':1})
		
		sheet = workbook.add_worksheet("Productos Compra - Última Venta")
		# sheet.write_merge(0, 0, 0, 3, 'Advance Bank Report', format0)
		sheet.set_column(0, 0, 20)
		sheet.set_column(0, 1, 20)
		sheet.set_column(0, 2, 20)
		sheet.set_column(0, 3, 20)
		sheet.set_column(0, 4, 20)

		sheet.write(0, 0, 'Fecha de Busqueda: ' + fields.Date.from_string(self.fecha_de_busqueda).strftime('%d-%m-%Y'), format0)
		sheet.write(1, 0, 'Producto', format0)
		sheet.write(1, 1, 'Fecha de Compra', format0)
		sheet.write(1, 2, 'Cantidad Comprada', format0)
		sheet.write(1, 3, 'Última Fecha de Venta', format0)
		sheet.write(1, 4, 'Días Transcurridos', format0)


		products = self.env['product.product'].search([('type', '=', 'product')])

		if products:

			fila = 2
			for product in products:
				product_id = product.id
				primera_compra = self.env['stock.move.line'].search([('location_id', '=', 4), ('location_dest_id', '=', 160), ('product_id', '=', product_id), ('date', '>=', self.fecha_de_busqueda)], limit = 1)
				if primera_compra:
					cantidad_comprada = primera_compra.qty_done
					todas_ventas =  self.env['stock.move.line'].search([('location_id', '=', 160), ('location_dest_id', '=', 5), ('product_id', '=', product_id), ('date', '>=', self.fecha_de_busqueda)], order='date asc')
					cantidad_todas_ventas = 0
					ids_todas_ventas = []
				
					for venta in todas_ventas:
						cantidad_todas_ventas = cantidad_todas_ventas + venta.qty_done
						if venta.qty_done > 0 :
							ids_todas_ventas.append(venta)
							if cantidad_todas_ventas == cantidad_comprada :
								break
						
					if int(cantidad_todas_ventas) == int(cantidad_comprada):
						sheet.write(fila, 0, product.display_name, format1)
						sheet.write(fila, 1,  fields.Date.from_string(primera_compra.date).strftime('%d-%m-%Y'), format1)
						sheet.write(fila, 2, primera_compra.qty_done, format1)
						sheet.write(fila, 3, fields.Date.from_string(ids_todas_ventas[-1].date).strftime('%d-%m-%Y'), format1)
						sheet.write(fila, 4, (ids_todas_ventas[-1].date - primera_compra.date).days, format1)
						fila = fila + 1
						# ids.append(primera_compra.id)
						# ids = ids + ids_todas_ventas




		# sheet.set_paper(1)
		# sheet.set_margins(left=0.19685, right=0.19685, top=0.19685, bottom=0.19685)

		workbook.close()

		self.write({'file': base64.encodestring(file_data.getvalue()), 'file_name': "productos_primera_compra_ultima_venta.xlsx"})
		file_data.close()
		
		return {
			'name': 'Productos Primera Compra - Última Venta',
			'view_mode': 'form',
			'view_type': 'form',
			'res_model': 'productos.compra.venta.wizard',
			'target': 'new',
			'res_id': self.id,
			'type': 'ir.actions.act_window'
		}
			
		# except:

		# 	raise UserError(_("Invalid file!"))

