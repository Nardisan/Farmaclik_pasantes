# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################
import ast
import copy
#import barcode
from odoo import fields, models, api, _
from datetime import datetime, date, timedelta
from itertools import groupby
from odoo.exceptions import ValidationError



class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_packaging = fields.Boolean("Is Packaging")
    alternate_product_ids = fields.Many2many('product.product', string="Alternative Product")
    suggestive_product_ids = fields.Many2many('product.product', 'cross_selling_products', 'template_id', 'product_id',
                                              string="Cross Selling Product")
    active_ingredient_ids = fields.Many2many('active.ingredient', string="Active Ingredient")
    fabricantes_ids = fields.Many2many('fabricante', string="Fabricante")

    is_material_monitor = fields.Boolean("Material Monitor")
    material_monitor_qty = fields.Float("Alert Stock Qty")

    codigo_interno_cobeca = fields.Char('Código Interno Cobeca')
    codigo_interno_drovencentro = fields.Char('Código Interno Drovencentro')
    codigo_interno_dronena = fields.Char('Código Interno Dronena')
    codigo_interno_nivica = fields.Char('Código Interno Nivica')
    codigo_interno_drotaca = fields.Char('Código Interno Drotaca')


    precio_cobeca = fields.Float('Precio Cobeca')
    precio_drovencentro = fields.Float('Precio Drovencentro')
    precio_dronena = fields.Float('Precio Dronena')
    precio_nivica = fields.Float('Precio Nivica')
    precio_drotaca = fields.Float('Precio Drotaca')


    fecha_de_calculo_min_max = fields.Date(string='Fecha Min Max Paseo Paraparal', default = "2023-05-26")
    fecha_de_calculo_min_max_farmagangas = fields.Date(string='Fecha Min Max Farmagangas', default = "2023-05-26")
    # rotacion = fields.Selection([('Baja', 'Baja'), ('Media', 'Media'), ('Alta', 'Alta')], string='Rotación', help='Indique rotación segun las ventas.')


    compania_activa_id = fields.Integer(string='Compania Activa', compute='get_id_compania_activa', readonly=True, store=False)

    stock_pp = fields.Float(string='Stock PP', compute='get_calculo_stock_pp', readonly=True, store=True )
    min_stock_pp = fields.Float(string='Min PP', compute='get_calculo_stock_min_pp', readonly=True, store=True )
    max_stock_pp = fields.Float(string='Max PP', compute='get_calculo_stock_max_pp', readonly=True, store=True )
    diferencia_pp = fields.Float(string='Dif PP', compute='get_calculo_stock_diff_pp', readonly=True, store=True )

    stock_eg = fields.Float(string='Stock EG', compute='get_calculo_stock_eg', readonly=True, store=True )
    min_stock_eg = fields.Float(string='Min EG', compute='get_calculo_stock_min_eg', readonly=True, store=True )
    max_stock_eg = fields.Float(string='Max EG', compute='get_calculo_stock_max_eg', readonly=True, store=True )
    diferencia_eg = fields.Float(string='Dif EG', compute='get_calculo_stock_diff_eg', readonly=True, store=True )

    stock_gu = fields.Float(string='Stock GU', compute='get_calculo_stock_gu', readonly=True, store=True )
    min_stock_gu = fields.Float(string='Min GU', compute='get_calculo_stock_min_gu', readonly=True, store=True )
    max_stock_gu = fields.Float(string='Max GU', compute='get_calculo_stock_max_gu', readonly=True, store=True )
    diferencia_gu = fields.Float(string='Dif GU', compute='get_calculo_stock_diff_gu', readonly=True, store=True )

    stock_fgg = fields.Float(string='Stock FGG', compute='get_calculo_stock_fgg', readonly=True, store=True )
    min_stock_fgg = fields.Float(string='Min FGG', compute='get_calculo_stock_min_fgg', readonly=True, store=True )
    max_stock_fgg = fields.Float(string='Max FGG', compute='get_calculo_stock_max_fgg', readonly=True, store=True )
    diferencia_fgg = fields.Float(string='Dif FGG', compute='get_calculo_stock_diff_fgg', readonly=True, store=True )

    # GENERAL

    stock_general_4f = fields.Float(string='Stock 4F', compute='get_calculo_stock', readonly=True, store=True )
    min_general_4f = fields.Float(string='Min 4F', compute='get_calculo_stock_min', readonly=True, store=True )
    max_general_4f = fields.Float(string='Max 4F', compute='get_calculo_stock_max', readonly=True, store=True )
    diferencia_general_4f = fields.Float(string='Dif 4F', compute='get_calculo_stock_diff', readonly=True, store=True )

    utilidad = fields.Float(string='Utilidad %', compute='get_utilidad_coste_precio_de_venta', inverse='get_coste_precio_de_venta_de_utilidad', )


    @api.model
    def create(self, vals):
        res = super(ProductTemplate, self).create(vals)
        param_obj = self.env['ir.config_parameter'].sudo()
        gen_barcode = param_obj.get_param('gen_barcode')
        barcode_selection = param_obj.get_param('barcode_selection')
        gen_internal_ref = param_obj.get_param('gen_internal_ref')

        if not vals.get('barcode') and gen_barcode:
            barcode_code = False
            if barcode_selection == 'code_39':
                barcode_code = barcode.codex.Code39(str(res.id) + datetime.now().strftime("%S%M%H%d%m%y"))
            if barcode_selection == 'code_128':
                barcode_code = barcode.codex.Code39(str(res.id) + datetime.now().strftime("%S%M%H%d%m%y"))
            if barcode_selection == 'ean_13':
                barcode_code = barcode.ean.EuropeanArticleNumber13(
                    str(res.id) + datetime.now().strftime("%S%M%H%d%m%y"))
            if barcode_selection == 'ean_8':
                barcode_code = barcode.ean.EuropeanArticleNumber8(str(res.id) + datetime.now().strftime("%S%M%H%d%m%y"))
            if barcode_selection == 'isbn_13':
                barcode_code = barcode.isxn.InternationalStandardBookNumber13(
                    '978' + str(res.id) + datetime.now().strftime("%S%M%H%d%m%y"))
            if barcode_selection == 'isbn_10':
                barcode_code = barcode.isxn.InternationalStandardBookNumber10(
                    str(res.id) + datetime.now().strftime("%S%M%H%d%m%y"))
            if barcode_selection == 'issn':
                barcode_code = barcode.isxn.InternationalStandardSerialNumber(
                    str(res.id) + datetime.now().strftime("%S%M%H%d%m%y"))
            if barcode_selection == 'upca':
                barcode_code = barcode.upc.UniversalProductCodeA(str(res.id) + datetime.now().strftime("%S%M%H%d%m%y"))

            if barcode_selection == 'issn':
                res.write({'barcode': barcode_code})
            else:
                res.write({'barcode': barcode_code.get_fullcode()})
        # generate_product_barcode_view.xml internal reference
        if not vals.get('default_code') and gen_internal_ref:
            res.write({'default_code': (str(res.id).zfill(6) + str(datetime.now().strftime("%S%M%H")))[:8]})
        return res
    
    @api.depends('list_price', 'standard_price')
    def get_utilidad_coste_precio_de_venta(self):
        
        for rec in self:
            rec.utilidad = ( (rec.list_price / rec.standard_price) -1 ) * 100 if rec.standard_price > 0 else 0

    def get_coste_precio_de_venta_de_utilidad(self):

        for rec in self:
            rec.with_company(self.env.company.id).list_price = rec.standard_price * ( 1 + ( rec.utilidad / 100 ) )
            rec.with_company(self.env.company.id).standard_price = rec.list_price / ( 1 +  ( rec.utilidad / 100 )  )
    
    def get_id_compania_activa(self):
        
        for rec in self:
            rec.compania_activa_id = self.env.company.id

    @api.depends('qty_available')
    def get_calculo_stock_pp(self):

        for rec in self: 

            rec.stock_pp = rec.with_context({ 'location': 8 }).qty_available
    
    @api.depends('fecha_de_calculo_min_max')
    def get_calculo_stock_min_pp(self):

        for rec in self: 

            producto = self.env['product.product'].search([('product_tmpl_id', '=', rec.id)], limit=1)

            regla_min_max_pp = self.env['stock.warehouse.orderpoint'].search(['&',('product_id', '=', producto.id),('location_id', '=', 8)])
            
            if regla_min_max_pp:
                rec.min_stock_pp = regla_min_max_pp[0].product_min_qty
            else:
                rec.min_stock_pp = None

    @api.depends('fecha_de_calculo_min_max')        
    def get_calculo_stock_max_pp(self):

        for rec in self: 

            producto = self.env['product.product'].search([('product_tmpl_id', '=', rec.id)], limit=1)

            regla_min_max_pp = self.env['stock.warehouse.orderpoint'].search(['&',('product_id', '=', producto.id),('location_id', '=', 8)])
          
            if regla_min_max_pp:
                rec.max_stock_pp = regla_min_max_pp[0].product_max_qty
            else:
                rec.max_stock_pp = None

    @api.depends('qty_available','fecha_de_calculo_min_max')
    def get_calculo_stock_diff_pp(self):

        for rec in self:
            
            rec.diferencia_pp = rec.max_stock_pp - rec.stock_pp

    

    @api.depends('qty_available')
    def get_calculo_stock_eg(self):

        for rec in self: 

            rec.stock_eg = rec.with_context({ 'location': 20 }).qty_available

    @api.depends('fecha_de_calculo_min_max')
    def get_calculo_stock_min_eg(self):

        for rec in self:
            
            producto = self.env['product.product'].search([('product_tmpl_id', '=', rec.id)], limit=1)

            regla_min_max_eg = self.env['stock.warehouse.orderpoint'].search(['&', ('product_id', '=', producto.id),('location_id', '=', 20)])
             
            if regla_min_max_eg:
                rec.min_stock_eg = regla_min_max_eg[0].product_min_qty             
            else:
                rec.min_stock_eg = None
               
    @api.depends('fecha_de_calculo_min_max')
    def get_calculo_stock_max_eg(self):

        for rec in self: 

            producto = self.env['product.product'].search([('product_tmpl_id', '=', rec.id)], limit=1)

            regla_min_max_eg = self.env['stock.warehouse.orderpoint'].search(['&',('product_id', '=', producto.id),('location_id', '=', 20)])
                
            if regla_min_max_eg:
                rec.max_stock_eg = regla_min_max_eg[0].product_max_qty             
            else:
                rec.max_stock_eg = None

    @api.depends('qty_available','fecha_de_calculo_min_max')
    def get_calculo_stock_diff_eg(self):

        for rec in self: 
       
            rec.diferencia_eg = rec.max_stock_eg - rec.stock_eg

    
    
    @api.depends('qty_available')
    def get_calculo_stock_gu(self):

        for rec in self: 

            rec.stock_gu = rec.with_context({ 'location': 28 }).qty_available

    @api.depends('fecha_de_calculo_min_max')
    def get_calculo_stock_min_gu(self):

        for rec in self:

            producto = self.env['product.product'].search([('product_tmpl_id', '=', rec.id)], limit=1)
           
            regla_min_max_gu = self.env['stock.warehouse.orderpoint'].search(['&',('product_id', '=', producto.id),('location_id', '=', 28)])
            
            if regla_min_max_gu:
                rec.min_stock_gu = regla_min_max_gu[0].product_min_qty            
            else:
                rec.min_stock_gu = None
                

    @api.depends('fecha_de_calculo_min_max')
    def get_calculo_stock_max_gu(self):

        for rec in self:

            producto = self.env['product.product'].search([('product_tmpl_id', '=', rec.id)], limit=1)

            regla_min_max_gu = self.env['stock.warehouse.orderpoint'].search(['&',('product_id', '=', producto.id),('location_id', '=', 28)])
            
            if regla_min_max_gu:
                rec.max_stock_gu = regla_min_max_gu[0].product_max_qty
            else:
                rec.max_stock_gu = None


    @api.depends('qty_available','fecha_de_calculo_min_max')
    def get_calculo_stock_diff_gu(self):

        for rec in self: 
          
            rec.diferencia_gu = rec.max_stock_gu - rec.stock_gu


   


    # FARMAGANGAS

    @api.depends('qty_available')
    def get_calculo_stock_fgg(self):

        for rec in self: 

            rec.stock_fgg = rec.with_context({ 'location': 160 }).qty_available
    
    @api.depends('fecha_de_calculo_min_max_farmagangas')
    def get_calculo_stock_min_fgg(self):

        for rec in self: 

            producto = self.env['product.product'].search([('product_tmpl_id', '=', rec.id)], limit=1)

            regla_min_max_fgg = self.env['stock.warehouse.orderpoint'].search(['&',('product_id', '=', producto.id),('location_id', '=', 160)])
            
            if regla_min_max_fgg:
                rec.min_stock_fgg = regla_min_max_fgg[0].product_min_qty
            else:
                rec.min_stock_fgg = None

    @api.depends('fecha_de_calculo_min_max_farmagangas')        
    def get_calculo_stock_max_fgg(self):

        for rec in self: 

            producto = self.env['product.product'].search([('product_tmpl_id', '=', rec.id)], limit=1)

            regla_min_max_fgg = self.env['stock.warehouse.orderpoint'].search(['&',('product_id', '=', producto.id),('location_id', '=', 160)])
          
            if regla_min_max_fgg:
                rec.max_stock_fgg = regla_min_max_fgg[0].product_max_qty
            else:
                rec.max_stock_fgg = None

    @api.depends('qty_available','fecha_de_calculo_min_max_farmagangas')
    def get_calculo_stock_diff_fgg(self):

        for rec in self:
            
            rec.diferencia_fgg = rec.max_stock_fgg - rec.stock_fgg


    # GENERAL

    @api.depends('qty_available')
    def get_calculo_stock(self):

        for rec in self: 

            rec.stock_general_4f = rec.stock_fgg + rec.stock_pp + rec.stock_eg + rec.stock_gu

    @api.depends('fecha_de_calculo_min_max', 'fecha_de_calculo_min_max_farmagangas')
    def get_calculo_stock_min(self): 
         
         for rec in self: 

            rec.min_general_4f = rec.min_stock_fgg + rec.min_stock_pp + rec.min_stock_eg + rec.min_stock_gu

    @api.depends('fecha_de_calculo_min_max', 'fecha_de_calculo_min_max_farmagangas')
    def get_calculo_stock_max(self): 
         
         for rec in self: 

            rec.max_general_4f = rec.max_stock_fgg + rec.max_stock_pp + rec.max_stock_eg + rec.max_stock_gu
           
    @api.depends('qty_available','fecha_de_calculo_min_max', 'fecha_de_calculo_min_max_farmagangas')
    def get_calculo_stock_diff(self): 
         
         for rec in self: 

            rec.diferencia_general_4f = rec.max_general_4f -  rec.stock_fgg - rec.stock_pp - rec.stock_eg - rec.stock_gu


    


class ProductProduct(models.Model):
    _inherit = "product.product"

    near_expire = fields.Integer(string='Near Expire', compute='check_near_expiry')
    expired = fields.Integer(string='Expired', compute='check_expiry')
    pos_product_commission_ids = fields.One2many('pos.product.commission', 'product_id', string='Product Commission ')
    utilidad = fields.Float(string='Utilidad')

    @api.onchange("tracking")
    def _onchange_tracking(self):
        for rec in self:
            rec.use_expiration_date = rec.tracking == "lot"

    @api.constrains('pos_product_commission_ids', 'pos_product_commission_ids.commission')
    def _check_commission_values(self):
        if self.pos_product_commission_ids.filtered(
                lambda line: line.calculation == 'percentage' and line.commission > 100 or line.commission < 0.0):
            raise Warning(_('Commission value for Percentage type must be between 0 to 100.'))

    def broadcast_product_qty_data(self, product_by_id, stock_location_id):
        notifications = []
        location_product_ids = self.search([('available_in_pos', '=', True), ('is_material_monitor', '=', True)])
        quant_vals = {}
        product_detail_id = []
        for location_product_id in location_product_ids:
            product_id = location_product_id.with_context({'location': stock_location_id, 'compute_child': False})
            quant_vals = {
                'location_id': stock_location_id,
                'product_id': product_id.id,
                'quantity': product_id.qty_available,
            }
            product_detail_id.append(quant_vals)
        user_ids = self.env['res.users'].sudo().search([]).filtered(
            lambda user: user.has_group('flexipharmacy.group_material_monitor_user'))
        for user_id in user_ids:
            notifications.append(
                [(self._cr.dbname, 'customer.display', user_id.id), {'updeted_location_vals_qty': product_detail_id}])
        self.env['bus.bus'].sendmany(notifications)
        return True

    def get_near_expiry(self):
        expiry_lot_ids = self.env['stock.production.lot'].search([('product_id', 'in', self.ids)])
        return expiry_lot_ids.filtered(lambda l: l.product_expiry_reminder)

    def get_expiry(self):
        expiry_lot_ids = self.env['stock.production.lot'].search([('product_id', 'in', self.ids)])
        return expiry_lot_ids.filtered(lambda l: l.product_expiry_alert)

    def check_near_expiry(self):
        stock_production_lot_obj = self.get_near_expiry()
        self.near_expire = len(stock_production_lot_obj)

    def check_expiry(self):
        stock_production_lot_obj = self.get_expiry()
        self.expired = len(stock_production_lot_obj)

    def nearly_expired(self):
        stock_production_lot_obj = self.get_near_expiry()
        action = self.env.ref('stock.action_production_lot_form').read()[0]
        action['domain'] = [('id', 'in', [each_lot.id for each_lot in stock_production_lot_obj])]
        return action

    def product_expired(self):
        stock_production_lot_obj = self.get_expiry()
        action = self.env.ref('stock.action_production_lot_form').read()[0]
        action['domain'] = [('id', 'in', [each_lot.id for each_lot in stock_production_lot_obj])]
        return action
    
    @api.model
    def search_product_expiry(self):
        today = datetime.today()
        today_end_date = datetime.strftime(today, "%Y-%m-%d 23:59:59")
        today_date = datetime.strftime(today, "%Y-%m-%d 00:00:00")
        
        company_id = self.env.user.company_id.id
        categ_nearexpiry_data = self.category_expiry(company_id)
        location_obj = self.env['stock.location']
        location_detail = location_obj.get_location_detail(company_id)
        warehouse_detail = location_obj.get_warehouse_expiry_detail(company_id)
        exp_in_day = {}
        product_expiry_days_ids = self.env['product.expiry.config'].search([('active', '=', True)])
        if product_expiry_days_ids:
            for each in product_expiry_days_ids:
                exp_in_day[int(each.no_of_days)] = 0
        exp_in_day_detail = copy.deepcopy(exp_in_day)
        date_add = datetime.today() + timedelta(days=1)
        today_date_exp = datetime.strftime(date_add, "%Y-%m-%d 00:00:00")
        today_date_end_exp = datetime.strftime(date_add, "%Y-%m-%d 23:59:59")
        for exp_day in exp_in_day:
            product_id_list = []
            exp_date = datetime.today() + timedelta(days=exp_day)
            today_exp_date = datetime.strftime(exp_date, "%Y-%m-%d 23:59:59")
            if today_date_end_exp == today_exp_date:
                today_expire_data_id = """
                    SELECT 
                        sq.lot_id
                    FROM 
                        stock_quant sq
                        LEFT JOIN stock_production_lot spl on spl.id = sq.lot_id
                    WHERE 
                        spl.expiration_date >= '%s' AND
                        spl.expiration_date <= '%s' AND 
                        sq.company_id = %s AND
                        sq.state_check = 'Near Expired'
                    GROUP BY 
                        sq.lot_id;
                """ % (today_date_exp, today_exp_date, company_id)
                self._cr.execute(today_expire_data_id)
            else:
                today_expire_data_id = """
                    SELECT 
                        sq.lot_id
                    FROM 
                        stock_quant sq
                        LEFT JOIN stock_production_lot spl on spl.id = sq.lot_id
                    WHERE 
                        spl.expiration_date >= '%s' AND
                        spl.expiration_date <= '%s' AND 
                        sq.company_id = %s AND
                        sq.state_check = 'Near Expired'
                    GROUP BY 
                        sq.lot_id;
                """ % (today_date, today_exp_date, company_id)
                self._cr.execute(today_expire_data_id)
            result = self._cr.fetchall()
        
            for each in result:
                for each_in in each:
                    product_id_list.append(each_in)
            product_config_color_id = self.env['product.expiry.config'].search([('no_of_days', '=',exp_day),('active', '=', True)], limit=1)
            exp_in_day_detail[exp_day] = {'product_id': product_id_list, 'color': product_config_color_id.block_color, 'text_color': product_config_color_id.text_color}
            exp_in_day[exp_day] = len(result)

        category_list = copy.deepcopy(categ_nearexpiry_data)
        category_res = []
        key = lambda x: x['categ_name']

        for k, v in groupby(sorted(category_list, key=key), key=key):
            qty = 0
            stock_lot = []
            for each in v:
                qty += float(each['quantity'])
                stock_lot.append(each['lot_id'])
            category_res.append({'categ_name': k, 'qty': qty, 'id': stock_lot})

        exp_in_day['expired'] = self.env['stock.production.lot'].search_count([('state_check', '=', 'Expired')])
        exp_in_day['today_expired'] = self.env['stock.production.lot'].search_count([('state_check', '=', 'Expired'), ('expiration_date', '<=', today_end_date), ('expiration_date', '>=', today_date)])
        list_near_expire = []
        quant_sql = '''
            SELECT 
                sq.lot_id as lot_id
            FROM 
                stock_quant sq
                LEFT JOIN stock_production_lot spl on spl.id = sq.lot_id
            WHERE 
                sq.state_check = 'Near Expired' AND 
                sq.company_id = %s AND 
                spl.expiration_date >= '%s' AND 
                spl.expiration_date <= '%s' 
        ''' % (company_id, today_date, today_end_date)
        self._cr.execute(quant_sql)
        quant_detail = self._cr.dictfetchall()

        for each_quant in quant_detail:
            list_near_expire.append(each_quant.get('lot_id'))
        exp_in_day['day_wise_expire'] = exp_in_day_detail
        exp_in_day['near_expired'] = len(set(list_near_expire))
        exp_in_day['near_expire_display'] = list_near_expire
        exp_in_day['category_near_expire'] = category_res
        exp_in_day['location_wise_expire'] = location_detail
        exp_in_day['warehouse_wise_expire'] = warehouse_detail
        return exp_in_day

    def category_expiry(self, company_id):
        quant_sql = '''
        SELECT 
            pt.name as product_name, 
            sq.quantity as quantity, 
            pc.name as categ_name, 
            spl.id as lot_id
        FROM 
            stock_quant sq
            LEFT JOIN stock_production_lot spl on spl.id = sq.lot_id
            LEFT JOIN product_product pp on pp.id = sq.product_id
            LEFT JOIN product_template pt on pt.id = pp.product_tmpl_id
            LEFT JOIN product_category pc on pc.id = pt.categ_id
        WHERE 
            pt.tracking != 'none' AND 
            spl.expiration_date is not NULL  AND 
            sq.state_check = 'Near Expired' AND 
            sq.company_id = %s AND 
            spl.expiration_date::Date >= current_date;
        ''' % (company_id)
        self._cr.execute(quant_sql)
        result = self._cr.dictfetchall()
        return result

    def graph_date(self, start, end):
        company_id = self.env.user.company_id.id
        graph_data_list = []
        start_date = datetime.strptime(start, '%Y-%m-%d').date()
        new_start_date = datetime.strftime(start_date, "%Y-%m-%d %H:%M:%S")
        end_date = datetime.strptime(end, '%Y-%m-%d').date()
        new_end_date = datetime.strftime(end_date, "%Y-%m-%d 23:59:59")

        sql = '''
            SELECT 
                pt.name as product_name, 
                sum(sq.quantity) AS qty
            FROM 
                stock_quant sq
                LEFT JOIN stock_production_lot spl on spl.id = sq.lot_id
                LEFT JOIN product_product AS pp ON pp.id = spl.product_id
                LEFT JOIN product_template AS pt ON pt.id = pp.product_tmpl_id
            WHERE 
                sq.company_id = %s AND 
                sq.state_check is NOT NULL AND 
                pt.tracking != 'none' AND 
                spl.expiration_date BETWEEN '%s' AND '%s'
            GROUP BY 
                pt.name;
        ''' % (company_id, new_start_date, new_end_date)
        self._cr.execute(sql)
        data_res = self._cr.dictfetchall()
        return data_res

    @api.model
    def expiry_product_alert(self):
        email_notify_date = None
        notification_days = self.env['ir.config_parameter'].sudo().get_param(
            'aspl_product_expiry_alert.email_notification_days')

        if notification_days:
            email_notify_date = date.today() + timedelta(days=int(notification_days))
            start_email_notify_date = datetime.strftime(date.today(), "%Y-%m-%d %H:%M:%S")
            end_email_notify_date = datetime.strftime(email_notify_date, "%Y-%m-%d 23:59:59")

            res_user_ids = ast.literal_eval(
                self.env['ir.config_parameter'].sudo().get_param('aspl_product_expiry_alert.res_user_ids'))

            SQL = """
                SELECT 
                    sl.name AS stock_location, 
                    pt.name AS Product,pp.id AS product_id, 
                    CAST(lot.expiration_date AS DATE),lot.name lot_number, 
                    sq.quantity AS Quantity
                FROM 
                    stock_quant AS sq
                    INNER JOIN stock_production_lot AS lot ON lot.id = sq.lot_id 
                    INNER JOIN stock_location AS sl ON sl.id = sq.location_id
                    INNER JOIN product_product AS pp ON pp.id = lot.product_id
                    INNER JOIN product_template AS pt ON pt.id = pp.product_tmpl_id
                WHERE 
                    sl.usage = 'internal' AND 
                    pt.tracking != 'none' AND 
                    lot.expiration_date BETWEEN '%s' AND '%s'
            """ %(start_email_notify_date,end_email_notify_date)
            self._cr.execute(SQL)
            near_expiry_data_list = self._cr.dictfetchall()
            email_list = []
            template_id = self.env.ref('aspl_product_expiry_alert.email_template_product_expiry_alert')
            res_user_ids = self.env['res.users'].browse(res_user_ids)
            email_list = [x.email for x in res_user_ids if x.email]
            email_list_1 = ', '.join(map(str, email_list))
            company_name = self.env['res.company']._company_default_get('your.module')
            if res_user_ids and template_id and near_expiry_data_list:
                # template_id.send_mail(int(near_expiry_data_list[0]['product_id']), force_send=True)
                template_id.with_context({'company': company_name,'email_list': email_list_1, 'from_dis': True,
                                          'data_list': near_expiry_data_list}).send_mail(int(near_expiry_data_list[0]['product_id']), force_send=True)
        return True


class PosProductCommission(models.Model):
    _name = 'pos.product.commission'
    _description = "Point of Sale Product Commission"

    doctor_id = fields.Many2one('res.partner', string='Doctor', domain="[('is_doctor', '=', True)]")
    calculation = fields.Selection([
        ('percentage', 'Percentage'),
        ('fixed_price', 'Fixed Price')
    ], string='Calculation')
    commission = fields.Float(string='Commission')
    product_id = fields.Many2one('product.product')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
