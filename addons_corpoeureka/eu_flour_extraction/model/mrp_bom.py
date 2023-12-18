# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    @api.onchange('bom_line_ids','bom_line_ids.product_principal_id','bom_line_ids.emp_primary','bom_line_ids.emp_secondary')
    def comprobar_activos_primary(self):
        for rec in self:
            if len(rec.bom_line_ids.filtered(lambda x: x.product_principal_id == True)) >1:
                raise UserError(_('No puede seleccionar mas de un producto principal'))
            if len(rec.bom_line_ids.filtered(lambda x: x.emp_primary == True)) >1:
                raise UserError(_('No puede seleccionar mas de un producto como empaque primario'))


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    product_principal_id = fields.Boolean(string='Producto Principal', default=False)
    emp_primary = fields.Boolean(string='Empaque Primario', default=False)
    emp_secondary = fields.Boolean(string='Empaque Secundario', default=False)
    cinta_codificadora = fields.Boolean(string='Cinta Codificadora', default=False)
    teflon = fields.Boolean(string='Teflón', default=False)

    @api.onchange('emp_primary')
    def comprobar_activos_emp_primary(self):
        for rec in self:
            if rec.product_principal_id == True:
                rec.emp_primary = False
                raise UserError('No puede seleccionar ya que se encuentra como producto principal')

            if rec.emp_secondary == True:
                rec.emp_primary = False
                raise UserError('No puede seleccionar ya que esta asignado como producto de empaque secundario')

    @api.onchange('emp_secondary')
    def comprobar_activos_emp_secondary(self):
        for rec in self:
            if rec.product_principal_id == True:
                rec.emp_secondary = False
                raise UserError('No puede seleccionar ya que se encuentra como producto principal')

            if rec.emp_primary == True:
                rec.emp_secondary = False
                raise UserError('No puede seleccionar ya que esta asignado como producto de empaque primario')

    @api.onchange('product_principal_id')
    def comprobar_activos_product_principal_id(self):
        for rec in self:
            if rec.emp_primary == True or rec.emp_secondary == True:
                rec.product_principal_id = False
                raise UserError('No puede seleccionar ya que esta asignado como producto de empaque primario o producto de empaque secundario')
               
    
class StockMove(models.Model):
    _inherit = 'stock.move'

    product_principal_id = fields.Boolean(string='Producto Principal',default=False, store=True, force_save=True,compute="_compute_productos")
    emp_primary = fields.Boolean(string='Empaque Primario', default=False, store=True,force_save=True, compute="_compute_productos")
    emp_secondary = fields.Boolean(string='Empaque Secundario', default=False, store=True,force_save=True, compute="_compute_productos")
    cinta_codificadora = fields.Boolean(string='Cinta Codificadora', default=False, store=True,force_save=True, compute="_compute_productos")
    teflon = fields.Boolean( string='Teflón',default=False, store=True, force_save=True, compute="_compute_productos")

    @api.depends('bom_line_id')
    def _compute_productos(self):
        for rec in self:
            rec.product_principal_id = rec.bom_line_id.product_principal_id
            rec.emp_primary = rec.bom_line_id.emp_primary
            rec.emp_secondary = rec.bom_line_id.emp_secondary
            rec.cinta_codificadora = rec.bom_line_id.cinta_codificadora
            rec.teflon = rec.bom_line_id.teflon

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    extraction_flour = fields.Float(string='Porcentaje de Extracción', compute="_compute_extraction_flour", store=True )
    extraction_porcent = fields.Float(string='Margen de Tolerancia', compute="_compute_porcent", store=True )

    @api.depends('qty_producing','move_raw_ids','move_raw_ids.quantity_done')
    def _compute_extraction_flour(self):
        for rec in self:
            rec.extraction_flour = 0
            principal = sum(rec.move_raw_ids.filtered(lambda x: x.product_principal_id == True).mapped('quantity_done'))
            if principal > 0:
                rec.extraction_flour = (rec.qty_producing / principal)* 100

    @api.depends('qty_producing','move_raw_ids','move_raw_ids.quantity_done', 'move_byproduct_ids.quantity_done')
    def _compute_porcent(self):
        for rec in self:
            
            campos =  rec.move_raw_ids.filtered(lambda x: x.product_principal_id == True)
            principal = sum(rec.move_raw_ids.filtered(lambda x: x.product_principal_id == True).mapped('quantity_done'))            
            tot_principal = rec.qty_producing
            
            sum_byproducts = sum(rec.move_byproduct_ids.mapped('quantity_done'))
            resul = tot_principal + sum_byproducts
            if principal > 0:
                rec.extraction_porcent = (resul / principal) * 100

    def button_mark_done(self):
        res = super(MrpProduction, self).button_mark_done()
        principal = False
        for rec in self:
            principal = rec.move_raw_ids.filtered(lambda x: x.product_principal_id == True)
            if principal:
                if rec.extraction_porcent < 99.9:
                    raise UserError('No se puede procesar ya que el Margen de Tolerancia es menor al 99,9%')
                if rec.extraction_porcent > 100:
                    raise UserError('No se puede procesar ya que el Margen de Tolerancia supera el 100%')
        return res