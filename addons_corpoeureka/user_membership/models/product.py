# -*- coding: utf-8 -*-

import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    not_show_in_website = fields.Boolean(copy=False)
    user_membership_plan_ids = fields.Many2many('user.membership.plan', string='Exclusively Available For', copy=False)
    msg = fields.Char("Message For Non Members", copy=False)
    is_membership = fields.Boolean(string='Membership', copy=False)
    user_membership_plan_id = fields.Many2one('user.membership.plan', string='Membership Plan', copy=False)

    def website_publish_button(self):
        self.ensure_one()
        res = super(ProductTemplate, self).website_publish_button()
        return res

    @api.constrains('user_membership_plan_id')
    def _check_plan_constraint(self):
        """ Plan must be unique """
        for product in self.filtered(lambda p: p.user_membership_plan_id):
            domain = [('id', '!=', product.id), ('user_membership_plan_id', '=', product.user_membership_plan_id.id)]
            if self.search(domain):
                raise ValidationError(
                    _('This membership plan is already assigned to some other product!\n'
                      'Select a different plan or create a new plan.'))

    def reset_wizard_action(self):
        cron_id = self.env.context.get('cron_id', False)
        if cron_id:
            cron_id = self.env['ir.cron'].sudo().search([('id', '=', cron_id)], )
        if cron_id:
            plans_to_unset = [(3, plan_id, 0) for plan_id in cron_id.user_membership_plan_ids.ids]
            for product_id in cron_id.product_template_ids:
                product_id.user_membership_plan_ids = plans_to_unset
                if not product_id.user_membership_plan_ids:
                    product_id.not_show_in_website = False
                    product_id.msg = ''
                else:
                    product_id.msg = 'Exclusively for ' + ", ".join(
                        product_id.user_membership_plan_ids.mapped('name')) + ' customers'

            # cron_id.active = False
            # cron_id.product_template_ids = False
            # cron_id.user_membership_plan_ids = False

    def write(self, vals):
        if "user_membership_plan_id" in vals and not vals.get('user_membership_plan_id'):
            self.user_membership_plan_id.product_template_id = False
        if "is_membership" in vals:
            if not vals.get("is_membership"):
                self.user_membership_plan_id.product_template_id = False
                vals['user_membership_plan_id'] = False
        res = super(ProductTemplate, self).write(vals)
        if vals.get('user_membership_plan_id'):
            self.user_membership_plan_id.product_template_id = self.id

        if "website_published" in vals:
            if self.website_published:
                self.user_membership_plan_id.write({'website_published': True})
            else:
                self.user_membership_plan_id.write({'website_published': False})
        return res

    @api.model
    def create(self, values):
        if "is_membership" in values:
            if not values.get("is_membership"):
                values['user_membership_plan_id'] = False
        res = super(ProductTemplate, self).create(values)
        if values.get('user_membership_plan_id'):
            res.user_membership_plan_id.product_template_id = res.id
        return res


class ProductProduct(models.Model):
    _inherit = 'product.product'

    is_membership = fields.Boolean(string='Membership', related='product_tmpl_id.is_membership', copy=False)
    duration_range = fields.Selection([('month', 'Month')],default='month', copy=False)
    duration_value = fields.Integer(copy=False)
    mem_priority = fields.Integer(string='Priority', copy=False)
    amount_pr_month = fields.Monetary(compute='compute_amount_pr_month', copy=False)

    @api.depends('duration_range', 'duration_value', 'lst_price')
    def compute_amount_pr_month(self):
        for rec in self:
            rec.amount_pr_month = rec.lst_price / (rec.duration_value if rec.duration_value else 1)


class InheritPricelist(models.Model):
    _inherit = "product.pricelist"

    pricelist_prime_id = fields.Many2one("product.pricelist", "Lista prime")
    is_prime_pricelist = fields.Boolean("Es lista de precio prime")

    @api.onchange("is_prime_pricelist")
    def _onchange_is_prime_pricelist(self):
        for rec in self:
            if rec.is_prime_pricelist:
                rec.pricelist_prime_id = rec.selectable = False

    @api.constrains("is_prime_pricelist")
    def _check_is_prime_pricelist(self):
        for rec in self:
            if not rec.is_prime_pricelist:
                if self.env["user.membership.plan"].search_count([('pricelist_id', '=', rec.id)]):
                    raise ValidationError("Hay planes de membresía con esta lista de precio")

                if self.search_count([('pricelist_prime_id', '=', rec.id)]):
                    raise ValidationError("Hay listas de precio que usan ésta como prime")


    def _compute_price_rule(self, products_qty_partner, date=False, uom_id=False):
        res = super(InheritPricelist, self)._compute_price_rule(products_qty_partner, date, uom_id)
        if uom_id:
            products = [item[0].with_context(uom=uom_id) for item in products_qty_partner]
        else:
            products = [item[0] for item in products_qty_partner]
        is_product_template = products[0]._name == "product.template"
        if is_product_template:
            product_ids = self.env['product.template'].sudo().search([('id', 'in', list(res.keys()))])
            for product_id in product_ids:
                if product_id.is_membership:
                    res.update({
                        product_id.id: (product_id.lst_price, False)
                    })
        else:
            product_ids = self.env['product.product'].sudo().search([('id', 'in', list(res.keys()))])
            for product_id in product_ids:
                if product_id.product_tmpl_id.is_membership:
                    res.update({
                        product_id.id: (product_id.lst_price, False)
                    })
        return res