from odoo import models, fields, api, _
from odoo.exceptions import  ValidationError
from datetime import datetime

class MinMaxFarmacia(models.TransientModel):

    _name = "mim.max.farmacia"
    _description = "Establece los mín y máx por producto de cada almacén"

    
    fecha_inicial = fields.Date(string='Fecha Inicial Estadística', required=True)
    fecha_final = fields.Date(string='Fecha Final Estadística', required=True)

    solo_estos_product = fields.Many2one('lista.productos.min.max', string='Solo Estos Productos')
    excluyendo_estos_product = fields.Many2one('lista.productos.min.max', string='Excluyendo Estos Productos')

    solo_estos_product_ids = fields.Many2many('product.product', 'product_solo', 'product_id', 'solo_id', string='Solo Estos Productos', domain="[('type', '=', 'product')]",  help='Para todos los productos dejar esta lista vacia', default=[])
    excluyendo_estos_product_ids = fields.Many2many('product.product', 'product_excluyendo', 'product_id', 'excluyendo_id',  string='Excluyendo Estos Productos', domain="[('type', '=', 'product')]", default=[])
    
    elementos_por_lote = fields.Integer(string='Elementos por Lote', required=True, default = 2000 )
    lotes_total = fields.Integer(string='Lotes Total',  compute="calculo_lotes_total" )
    lote = fields.Integer(string='Lote', required=True)
    
    @api.depends('solo_estos_product', 'excluyendo_estos_product')
    def calculo_lotes_total(self):

        if len(self.solo_estos_product.lista_productos) == 0:
            productos = self.env['product.product'].search([('type', '=', 'product'), ('id', 'not in', self.excluyendo_estos_product.lista_productos.ids)])
        else:
            productos = self.env['product.product'].search([('type', '=', 'product'), ('id', 'in', self.solo_estos_product.lista_productos.ids), ('id', 'not in', self.excluyendo_estos_product.lista_productos.ids)])

        self.lotes_total = self.ceil(len(productos) / self.elementos_por_lote)


    def ceil(self, x):
        return int(x) + int((x>0) and (x - int(x)) > 0)

    def calcular_min_max_farmacia(self):

        if self.fecha_final < self.fecha_inicial:
            raise ValidationError(_('Fecha final de estadística debe ser mayor o igual a fecha inicial de estadística'))
        
        self.solo_estos_product_ids = self.solo_estos_product.lista_productos
        self.excluyendo_estos_product_ids = self.excluyendo_estos_product.lista_productos

        if self.env.company.id == 50:
            return self.calcular_min_max_farmagangas()
        if self.env.company.id == 1:
            return self.calcular_min_max_paseo_paraparal()

    def calcular_min_max_farmagangas(self):

        fgg_id = 160
        ubicacion_cliente_id = 5
        fecha_de_calculo_min_max = datetime.today().strftime("%Y-%m-%d")

        if len(self.solo_estos_product_ids) == 0:
            productos = self.env['product.product'].search([('type', '=', 'product'), ('id', 'not in', self.excluyendo_estos_product_ids.ids)], limit = self.elementos_por_lote, offset=self.elementos_por_lote*(self.lote-1))
        else:
            productos = self.env['product.product'].search([('type', '=', 'product'), ('id', 'in', self.solo_estos_product_ids.ids), ('id', 'not in', self.excluyendo_estos_product_ids.ids)], limit = self.elementos_por_lote, offset=self.elementos_por_lote*(self.lote-1))


        fecha_anterior_fgg = ""
        suma_mes_fgg = 0
        suma_ventas_fgg = 0
        min_fgg = 0
        max_fgg = 0
        
        for producto in productos:

            fecha_anterior_fgg = ""
            suma_mes_fgg = 0
            suma_ventas_fgg = 0
            min_fgg = 0
            max_fgg = 0

            product_id = producto.id

            movimientos_fgg_clientes = self.env['stock.move.line'].search([('product_id','=', product_id), ('location_id','=', fgg_id), ('location_dest_id','=', ubicacion_cliente_id), ('date', '>=', self.fecha_inicial), ('date', '<=',  self.fecha_final) ], order="date asc")
    
            for movimiento in movimientos_fgg_clientes:
            
                fecha_movimiento = datetime.strptime(str(movimiento.date),"%Y-%m-%d %H:%M:%S").strftime('%Y-%m')
                
                suma_ventas_fgg = suma_ventas_fgg + movimiento.qty_done
                
                if fecha_movimiento != fecha_anterior_fgg:
                    suma_mes_fgg = suma_mes_fgg + 1
                    fecha_anterior_fgg = fecha_movimiento

            if suma_mes_fgg > 0:
                min_fgg = suma_ventas_fgg / ( suma_mes_fgg * 30) * 7 
                max_fgg = suma_ventas_fgg / ( suma_mes_fgg * 30) * 20
            else:
                min_fgg = 0
                max_fgg = 0
        
            regla_minimo_maximo_fgg = self.env['stock.warehouse.orderpoint'].search([ ('product_id','=', product_id), ('location_id','=', fgg_id) ], limit=1)
            
            if regla_minimo_maximo_fgg:
                regla_minimo_maximo_fgg.write({'product_min_qty': self.ceil(min_fgg), 'product_max_qty': self.ceil(max_fgg), 'qty_multiple': 1 })
            else:
                self.env['stock.warehouse.orderpoint'].create({ 'trigger': 'manual', 'product_id' : product_id, 'location_id' : fgg_id, 'product_min_qty': self.ceil(min_fgg), 'product_max_qty': self.ceil(max_fgg), 'qty_multiple': 1 })
            
            producto.product_tmpl_id.write({'fecha_de_calculo_min_max_farmagangas': fecha_de_calculo_min_max })
  
        action = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Establecer Mín y Máx Farmacia',
                'type': 'success',
                'message': 'Mínimos y Máximos establecidos en Farmagangas',
                'sticky': True,
            }
        }

        return action

    def calcular_min_max_paseo_paraparal(self):

        pp_id = 8
        pp_consignaciones_id = 44
        eg_id = 20
        gu_id = 28
        ubicacion_cliente_id = 5
        fecha_de_calculo_min_max = datetime.today().strftime("%Y-%m-%d")

        if len(self.solo_estos_product_ids) == 0:
            productos = self.env['product.product'].search([('type', '=', 'product'), ('id', 'not in', self.excluyendo_estos_product_ids.ids)], limit = self.elementos_por_lote, offset=self.elementos_por_lote*(self.lote-1))
        else:
            productos = self.env['product.product'].search([('type', '=', 'product'), ('id', 'in', self.solo_estos_product_ids.ids), ('id', 'not in', self.excluyendo_estos_product_ids.ids)], limit = self.elementos_por_lote, offset=self.elementos_por_lote*(self.lote-1))

        fecha_anterior_pp = ""
        suma_mes_pp = 0
        suma_ventas_pp = 0
        min_pp = 0
        max_pp = 0

        fecha_anterior_eg = ""
        suma_mes_eg = 0
        suma_ventas_eg = 0
        min_eg = 0
        max_eg = 0

        fecha_anterior_gu = ""
        suma_mes_gu = 0
        suma_ventas_gu = 0
        min_gu = 0
        max_gu = 0
    
        for producto in productos:
            
            
            product_id = producto.id
        
            # >>>>>>>>>>>>>>>>>>>>> PP 
            
            fecha_anterior_pp = ""
            suma_mes_pp = 0
            suma_ventas_pp = 0
            min_pp = 0
            max_pp = 0
            
            movimientos_pp_clientes = self.env['stock.move.line'].search([ ('product_id','=', product_id), ('location_id','in', [pp_id, pp_consignaciones_id]), ('location_dest_id','=', ubicacion_cliente_id), ('date', '>=', self.fecha_inicial), ('date', '<=',  self.fecha_final) ], order="date asc")
            
            for movimiento in movimientos_pp_clientes:
            
                fecha_movimiento = datetime.strptime(str(movimiento.date),"%Y-%m-%d %H:%M:%S").strftime('%Y-%m')
                
                suma_ventas_pp = suma_ventas_pp + movimiento.qty_done
                
                if fecha_movimiento != fecha_anterior_pp:
                    suma_mes_pp = suma_mes_pp + 1
                    fecha_anterior_pp = fecha_movimiento
            
            
            if suma_mes_pp > 0:
                min_pp = suma_ventas_pp / ( suma_mes_pp * 30 ) * 7
                max_pp = suma_ventas_pp / ( suma_mes_pp * 30 ) * 20
            else:
                min_pp = 0
                max_pp = 0

            # >>>>>>>>>>>>>>>>>>>>> EG
            
            fecha_anterior_eg = ""
            suma_mes_eg = 0
            suma_ventas_eg = 0
            min_eg = 0
            max_eg = 0

            movimientos_eg_clientes = self.env['stock.move.line'].search([ ('product_id','=', product_id), ('location_id','=', eg_id), ('location_dest_id','=', ubicacion_cliente_id), ('date', '>=', self.fecha_inicial), ('date', '<=',  self.fecha_final) ], order="date asc")
            
            for movimiento in movimientos_eg_clientes:
            
                fecha_movimiento = datetime.strptime(str(movimiento.date),"%Y-%m-%d %H:%M:%S").strftime('%Y-%m')
                
                suma_ventas_eg = suma_ventas_eg + movimiento.qty_done
                
                if fecha_movimiento != fecha_anterior_eg:
                    suma_mes_eg = suma_mes_eg + 1
                    fecha_anterior_eg = fecha_movimiento
            
            
            if suma_mes_eg > 0:
                min_eg = suma_ventas_eg / ( suma_mes_eg * 30 ) * 7
                max_eg = suma_ventas_eg / ( suma_mes_eg * 30 ) * 20
            else:
                min_eg = 0
                max_eg = 0
            
            # >>>>>>>>>>>>>>>>>>>>> GU
            
            fecha_anterior_gu = ""
            suma_mes_gu = 0
            suma_ventas_gu = 0
            min_gu = 0
            max_gu = 0

            movimientos_gu_clientes = self.env['stock.move.line'].search([ ('product_id','=', product_id), ('location_id','=', gu_id), ('location_dest_id','=', ubicacion_cliente_id), ('date', '>=', self.fecha_inicial), ('date', '<=',  self.fecha_final) ], order="date asc")
            
            for movimiento in movimientos_gu_clientes:
                
                fecha_movimiento = datetime.strptime(str(movimiento.date),"%Y-%m-%d %H:%M:%S").strftime('%Y-%m')
               
                suma_ventas_gu = suma_ventas_gu + movimiento.qty_done
            
                if fecha_movimiento != fecha_anterior_gu:
                    suma_mes_gu = suma_mes_gu + 1
                    fecha_anterior_gu = fecha_movimiento
            
            if suma_mes_gu > 0:
                min_gu = suma_ventas_gu / ( suma_mes_gu * 30) * 7 
                max_gu = suma_ventas_gu / ( suma_mes_gu * 30) * 20
            else:
                min_gu = 0
                max_gu = 0
            
            
            regla_minimo_maximo_pp = self.env['stock.warehouse.orderpoint'].search([ ('product_id','=', product_id), ('location_id','=', pp_id) ], limit=1)
            if regla_minimo_maximo_pp:
                regla_minimo_maximo_pp.write({'product_min_qty': self.ceil(min_pp), 'product_max_qty': self.ceil(max_pp), 'qty_multiple': 1 })
            else:
                self.env['stock.warehouse.orderpoint'].create({ 'trigger': 'manual', 'product_id' : product_id, 'location_id' : pp_id, 'product_min_qty': self.ceil(min_pp), 'product_max_qty': self.ceil(max_pp), 'qty_multiple': 1 })
            
            regla_minimo_maximo_eg = self.env['stock.warehouse.orderpoint'].search([ ('product_id','=', product_id), ('location_id','=', eg_id) ], limit=1)
            if regla_minimo_maximo_eg:
                regla_minimo_maximo_eg.write({'product_min_qty': self.ceil(min_eg), 'product_max_qty': self.ceil(max_eg), 'qty_multiple': 1 })
            else:
                self.env['stock.warehouse.orderpoint'].create({ 'trigger': 'manual', 'product_id' : product_id, 'location_id' : eg_id, 'product_min_qty': self.ceil(min_eg), 'product_max_qty': self.ceil(max_eg), 'qty_multiple': 1 })
            
            regla_minimo_maximo_gu = self.env['stock.warehouse.orderpoint'].search([ ('product_id','=', product_id), ('location_id','=', gu_id) ], limit=1)
            if regla_minimo_maximo_gu:
                regla_minimo_maximo_gu.write({'product_min_qty': self.ceil(min_gu), 'product_max_qty': self.ceil(max_gu), 'qty_multiple': 1 })
            else:
                self.env['stock.warehouse.orderpoint'].create({ 'trigger': 'manual', 'product_id' : product_id, 'location_id' : gu_id, 'product_min_qty': self.ceil(min_gu), 'product_max_qty': self.ceil(max_gu), 'qty_multiple': 1 })
            
            producto.write({'fecha_de_calculo_min_max': fecha_de_calculo_min_max })

        action = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Establecer Mín y Máx Farmacia',
                'type': 'success',
                'message': 'Mínimos y Máximos establecidos en Paseo Paraparal',
                'sticky': True,
            }
        }

        return action
        
    