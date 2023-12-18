import logging
import base64
from io import BytesIO
from odoo import models, fields, _
import xlsxwriter
from odoo.exceptions import Warning, UserError
from datetime import datetime, timedelta


class ProductosValoracionMercanciaVendida(models.TransientModel):
	
	_name = "productos.valoracion.mercancia.vendida"
	_description = "Imforme valoración mercancía vendida."
	_inherit = 'report.report_xlsx.abstract'
	
	
	ubicacion = fields.Many2one('stock.location', string='Ubicación', required=True)
	fecha_inicial_de_venta = fields.Date(string='Fecha Inicial de Venta', required=True)
	fecha_final_de_venta = fields.Date(string='Fecha Final de Venta', required=True)
	
	file_name = fields.Char('Nombre De Informe', size=256)
	file = fields.Binary('Informe', readonly=True)
	
	def generar(self):

		file_data = BytesIO()
		workbook = xlsxwriter.Workbook(file_data)
		# try:
		format0 = workbook.add_format({ 'bold': True, 'align':'center', 'valign':'vcenter', 'font_size':10, 'border':1})
		format1 =  workbook.add_format({ 'bold': False, 'align':'center', 'valign':'vcenter', 'font_size':10, 'border':1})
		
		
		sheet = workbook.add_worksheet("Valoración Mercancía Vendida")
		# sheet.write_merge(0, 0, 0, 3, 'Advance Bank Report', format0)
		sheet.set_column(0, 0, 20)
		sheet.set_column(0, 1, 20)
		sheet.set_column(0, 2, 20)
		sheet.set_column(0, 3, 20)

        
		sheet.write(0, 1, 'Fecha Inicial de Venta: ' + fields.Date.from_string(self.fecha_inicial_de_venta).strftime('%d-%m-%Y'), format0)
		sheet.write(0, 2, 'Fecha Final de Venta: ' + fields.Date.from_string(self.fecha_final_de_venta).strftime('%d-%m-%Y'), format0)
		sheet.write(0, 0, 'Ubicación: ' + self.ubicacion.complete_name, format0)
		
		sheet.write(2, 0, 'Producto', format0)
		sheet.write(2, 1, 'Vendido', format0)
		sheet.write(2, 2, 'Coste Unitario', format0)
		sheet.write(2, 3, 'Coste Total', format0)
		
		
		ubicacion_cliente = self.env['stock.location'].search([('usage', '=', 'customer')], limit = 1)
		salidas = self.env['stock.move.line'].search([('location_id', '=', self.ubicacion.id), ('location_dest_id', '=', ubicacion_cliente.id ), ('date', '>=', self.fecha_inicial_de_venta ), ('date', '<=', self.fecha_final_de_venta )])
		
		if salidas:

			fila = 3
			productos_cantidad_vendida = {}
			suma_coste  = 0
			
			for salida in salidas:
							
				if str(salida.product_id.id) in productos_cantidad_vendida:
					productos_cantidad_vendida[str(salida.product_id.id)] = { "producto": productos_cantidad_vendida[str(salida.product_id.id)]["producto"], "coste" : productos_cantidad_vendida[str(salida.product_id.id)]["coste"], "cantidad": productos_cantidad_vendida[str(salida.product_id.id)]["cantidad"] +  salida.qty_done }
				else:
					productos_cantidad_vendida[str(salida.product_id.id)] = { "producto": salida.product_id.display_name, "coste" : salida.product_id.standard_price, "cantidad" : salida.qty_done}
					
            
			for producto_cantidad_vendida in productos_cantidad_vendida.values():
				
				sheet.write(fila, 0, producto_cantidad_vendida["producto"], format1)
				sheet.write(fila, 1,  producto_cantidad_vendida["cantidad"], format1)
				sheet.write(fila, 2,  producto_cantidad_vendida["coste"], format1)
				sheet.write(fila, 3,  producto_cantidad_vendida["cantidad"] * producto_cantidad_vendida["coste"], format1)
				suma_coste = suma_coste + producto_cantidad_vendida["cantidad"] * producto_cantidad_vendida["coste"]
				fila = fila + 1
				
			sheet.write(fila, 3, suma_coste, format0)       

		
		workbook.close()

		self.write({'file': base64.encodestring(file_data.getvalue()), 'file_name': "productos_valoracion_mercancia_vendida.xlsx"})
		file_data.close()
		
		return {
			'name': 'Productos Valoración Mercancía Vendida',
			'view_mode': 'form',
			'view_type': 'form',
			'res_model': 'productos.valoracion.mercancia.vendida',
			'target': 'new',
			'res_id': self.id,
			'type': 'ir.actions.act_window'
		}
			
		# except:

		# 	raise UserError(_("Invalid file!"))

