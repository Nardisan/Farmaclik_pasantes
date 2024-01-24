from lxml import etree

from odoo.addons.stock_bids.helpers.get_previous_months_helpers import get_previous_months_helper
from odoo import models, fields, api


class ProductTemplateSalesResume(models.Model):
    _name = 'stock_bids.product_resume'

    _description = 'stock_bids.product_resume'

    product = fields.Many2one('product.template', string='Product', required=True)

    # Campos

    barcode = fields.Char(string='Codigo de barras', related='product.barcode')

    default_code = fields.Char(string='Codigo interno', related='product.default_code')

    product_name = fields.Char(string='Product Name', related='product.name')

    categ_id = fields.Many2one(string='Categoria', related='product.categ_id', store=True)

    rotacion_4f = fields.Selection(string='Rotación 4F', related='product.rotacion_4f')

    lst_price = fields.Float(string='Precio de venta', related='product.lst_price')

    standard_price = fields.Float(string='Costo', related='product.standard_price')

    utilidad = fields.Float(string='Utilidad', related='product.utilidad')

    active_ingredient_ids = fields.Many2many(string="Principio activo", related='product.active_ingredient_ids')

    fabricantes_ids = fields.Many2many(string="Fabricantes", related='product.fabricantes_ids')

    # Meses ( 6 meses de reporte )

    ventas_mes_1 = fields.Char(string='Mes 1', store=True)

    ventas_mes_2 = fields.Char(string='Mes 2', store=True)

    ventas_mes_3 = fields.Char(string='Mes 3', store=True)

    ventas_mes_4 = fields.Char(string='Mes 4', store=True)

    ventas_mes_5 = fields.Char(string='Mes 5', store=True)

    ventas_mes_6 = fields.Char(string='Mes 6', store=True)

    ventas_promedio = fields.Float(string='Promedio Ventas', store=True)

    meses_existencia = fields.Float(string='Meses Existencia', store=True)

    ventas_total = fields.Integer(string='Total Ventas', store=True, compute='calcular_ventas')

    # Estadisticas por farmacia

    # PP
    stock_pp = fields.Float(string='Stock PP', readonly=True, related='product.stock_pp')
    min_stock_pp = fields.Float(string='Min PP', readonly=True, related='product.min_stock_pp')
    max_stock_pp = fields.Float(string='Max PP', readonly=True, related='product.max_stock_pp')
    diferencia_pp = fields.Float(string='Dif PP', readonly=True, related='product.diferencia_pp')
    comprar_pp = fields.Float(string='Comprar PP', readonly=True, compute='get_comprar_pp')

    # EG
    stock_eg = fields.Float(string='Stock EG', readonly=True, related='product.stock_eg')
    min_stock_eg = fields.Float(string='Min EG', readonly=True, related='product.min_stock_eg')
    max_stock_eg = fields.Float(string='Max EG', readonly=True, related='product.max_stock_eg')
    diferencia_eg = fields.Float(string='Dif EG', readonly=True, related='product.diferencia_eg')
    comprar_eg = fields.Float(string='Comprar EG', readonly=True, compute='get_comprar_eg')

    # GU
    stock_gu = fields.Float(string='Stock GU', readonly=True, related='product.stock_gu')
    min_stock_gu = fields.Float(string='Min GU', readonly=True, related='product.min_stock_gu')
    max_stock_gu = fields.Float(string='Max GU', readonly=True, related='product.max_stock_gu')
    diferencia_gu = fields.Float(string='Dif GU', readonly=True, related='product.diferencia_gu')
    comprar_gu = fields.Float(string='Comprar GU', readonly=True, compute='get_comprar_gu')

    # FGG
    stock_fgg = fields.Float(string='Stock FGG', readonly=True, related='product.stock_fgg')
    min_stock_fgg = fields.Float(string='Min FGG', readonly=True, related='product.min_stock_fgg')
    max_stock_fgg = fields.Float(string='Max FGG', readonly=True, related='product.max_stock_fgg')
    diferencia_fgg = fields.Float(string='Dif FGG', readonly=True, related='product.diferencia_fgg')
    comprar_fgg = fields.Float(string='Comprar FGG', readonly=True, compute='get_comprar_fgg')

    # Estadisticas totalidad

    comprar_total = fields.Float(string='Comprar Total', readonly=True, compute='get_comprar_total')

    pv = fields.Float(string='PV', readonly=True, compute='get_pv')

    @api.depends('stock_pp', 'max_stock_pp')
    def get_comprar_pp(self):
        for record in self:
            record.comprar_pp = self._calcular_cantidad_comprar(record.max_stock_pp, record.stock_pp)

    @api.depends('stock_pp', 'max_stock_pp')
    def get_comprar_eg(self):
        for record in self:
            record.comprar_eg = self._calcular_cantidad_comprar(record.max_stock_eg, record.stock_eg)

    @api.depends('stock_eg', 'max_stock_eg')
    def get_comprar_gu(self):
        for record in self:
            record.comprar_gu = self._calcular_cantidad_comprar(record.max_stock_gu, record.stock_gu)

    @api.depends('stock_gu', 'max_stock_gu')
    def get_comprar_fgg(self):
        for record in self:
            record.comprar_fgg = self._calcular_cantidad_comprar(record.max_stock_fgg, record.stock_fgg)

    @api.depends('product')
    def calcular_ventas(self):

        print("CALCULANDO VENTAS")

        query = """
        SELECT id, sq.mes, sq.total
        FROM product_product AS pp
        INNER JOIN (
            SELECT product_id, to_char(pol.create_date, 'TMMonth YYYY') as mes, sum(pol.qty) as total
                   -- average of pol.qty
            FROM pos_order_line as pol
            WHERE create_date >= date_trunc('month', current_date - INTERVAL '6 months')
            GROUP BY mes, product_id
        ) AS sq ON pp.id = sq.product_id
        WHERE pp.default_code=%s;
        """

        params = [self.default_code, ]

        self.env.cr.execute(query, params)

        result = self.env.cr.dictfetchall()

        promedio_ventas = 0

        total_ventas = 0

        meses_existencia = 0

        for record in self:
            index = 0
            prev_months = get_previous_months_helper(record.create_date)
            for m in prev_months:
                found = False
                for r in result:
                    if r['mes'].startswith(m.month_name) and m.is_available:
                        setattr(record, 'ventas_mes_' + str(index + 1), '-')
                        found = True
                        break
                    elif r['mes'].startswith(m.month_name):
                        # meses_modelo[index] = r['total']
                        setattr(record, 'ventas_mes_' + str(index + 1), r['total'])
                        total_ventas += r['total']
                        meses_existencia += 1
                        found = True
                        break
                if not found:
                    setattr(record, 'ventas_mes_' + str(index + 1), 0)
                index += 1

            record.ventas_total = total_ventas

            if meses_existencia == 0:
                record.ventas_promedio = 0
            else:
                record.ventas_promedio = total_ventas / meses_existencia

    @api.depends('comprar_pp', 'comprar_eg', 'comprar_gu', 'comprar_fgg')
    def get_comprar_total(self):
        for record in self:
            record.comprar_total = record.comprar_pp + record.comprar_eg + record.comprar_gu + record.comprar_fgg

    @api.depends('comprar_total', 'standard_price')
    def get_pv(self):
        for record in self:
            record.pv = record.comprar_total * record.standard_price

    def _calcular_cantidad_comprar(self, s2, r2) -> float:
        """
        Obtener cantidad a comprar por farmacia.
        """
        if s2 > r2:
            return s2 - r2
        else:
            return 0

    def mes(self, n_mes):
        pass

    def actualizar_mes_actual_cron(self):
        pass
        # self.env['products_sales_resume.product_resume'].search([])

    def actualizar_todos_hook(self):
        pass
        # self.env['products_sales_resume.product_resume'].search([])

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):

        res = super(ProductTemplateSalesResume, self).fields_view_get(view_id=view_id, view_type=view_type,
                                                                      toolbar=toolbar, submenu=submenu)
        if view_type == 'tree':
            # Obtener el id de la vista de formulario
            view_id = self.env.ref('stock_bids.product_resume_tree_view').id
            # Obtener el XML de la vista
            doc = etree.XML(res['arch'])

            # meses previos ( 6 meses de reporte ). Solo los nombres de los meses (ej: Enero, Febrero, Marzo, etc)

            previous_months = get_previous_months_helper()

            print(previous_months)

            # Crear un diccionario con los nuevos labels
            new_labels = {
                'ventas_mes_1': previous_months[0].month_name,
                'ventas_mes_2': previous_months[1].month_name,
                'ventas_mes_3': previous_months[2].month_name,
                'ventas_mes_4': previous_months[3].month_name,
                'ventas_mes_5': previous_months[4].month_name,
                'ventas_mes_6': previous_months[5].month_name,
            }
            # Recorrer los campos y cambiar el atributo string por el valor del diccionario
            for field in doc.xpath("//field"):
                field_name = field.get('name')
                if field_name in new_labels:
                    field.set('string', new_labels[field_name])
            # Actualizar el XML de la vista
            res['arch'] = etree.tostring(doc)
        return res
