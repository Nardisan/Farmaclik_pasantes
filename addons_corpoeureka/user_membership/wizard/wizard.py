import datetime

from odoo import models, fields, api


class ProductWizard(models.TransientModel):
    _name = 'product.wizard'

    control_action = fields.Selection([("set", "Set Exclusive Products"), ("unset", "Unset Exclusive Products")],
                                      default="set", string="Action")
    msg = fields.Text("Message For Non Members")
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    public_categ_ids = fields.Many2many('product.public.category', string='Categories')
    user_membership_plan_ids = fields.Many2many('user.membership.plan', string='For Membership Plan',
                                                help='Allow all products in website')
    time = fields.Integer(string='Time(Hours)', default=1, help='Set time to unavailable the products')
    product_tmpl_ids = fields.Many2many('product.template', string="Exclusive Products",
                                        domain=[("is_membership", "=", False)])

    @api.onchange("control_action")
    def clear_selections(self):
        self.product_tmpl_ids = False
        self.user_membership_plan_ids = False
        self.msg = False
        self.public_categ_ids = False

    @api.onchange('user_membership_plan_ids')
    def onchange_user_membership_plan_ids(self):
        if self.user_membership_plan_ids:
            self.msg = 'Exclusively for ' + ", ".join(
                self.user_membership_plan_ids.mapped('name')) + ' customers'

            if self.control_action == "set":
                domain = []
                product_auto_fill_domain = []
                if self.product_tmpl_ids:
                    product_auto_fill_domain.append(("id", "in", self.product_tmpl_ids.ids))
                exclude_product_domain = [("user_membership_plan_ids", "in", self.user_membership_plan_ids.ids)]
                if self.public_categ_ids:
                    domain.append(("public_categ_ids", "child_of", self.public_categ_ids.ids))
                    product_auto_fill_domain.append(("public_categ_ids", "child_of", self.public_categ_ids.ids))
                    exclude_product_domain.append(("public_categ_ids", "child_of", self.public_categ_ids.ids))
                all_product_tmpl_ids = self.env['product.template'].search(domain)
                fill_product_tmpl_ids = self.env['product.template'].search(product_auto_fill_domain)
                exclude_product_tmpl_ids = self.env['product.template'].search(exclude_product_domain)
                valid_product_tmpl_ids = all_product_tmpl_ids - exclude_product_tmpl_ids
                auto_fill_product_tmpl_ids = fill_product_tmpl_ids - exclude_product_tmpl_ids
                if self.product_tmpl_ids:
                    self.product_tmpl_ids = auto_fill_product_tmpl_ids
                return {"domain": {
                    'product_tmpl_ids': [('id', 'in', valid_product_tmpl_ids.ids), ("is_membership", "=", False)]}}

            elif self.control_action == "unset":
                domain = [("user_membership_plan_ids", "in", self.user_membership_plan_ids.ids)]
                if self.public_categ_ids:
                    domain.append(("public_categ_ids", "child_of", self.public_categ_ids.ids))
                product_tmpl_ids = self.env['product.template'].search(domain)
                self.product_tmpl_ids = product_tmpl_ids
                return {
                    "domain": {'product_tmpl_ids': [('id', 'in', product_tmpl_ids.ids), ("is_membership", "=", False)]}}
        else:
            self.msg = ""
            return {"domain": {'product_tmpl_ids': [("is_membership", "=", False)]}}

    @api.onchange('public_categ_ids')
    def onchange_public_categ_ids(self):
        if self.control_action == "set":
            if self.public_categ_ids:
                domain = [("public_categ_ids", "child_of", self.public_categ_ids.ids)]
                exclude_product_domain = []
                if self.user_membership_plan_ids:
                    exclude_product_domain.append(("user_membership_plan_ids", "in", self.user_membership_plan_ids.ids))
                    exclude_product_domain.append(("public_categ_ids", "child_of", self.public_categ_ids.ids))
                product_tmpl_ids = self.env['product.template'].sudo().search(domain)
                if exclude_product_domain:
                    exclude_product_tmpl_ids = self.env['product.template'].sudo().search(exclude_product_domain)
                else:
                    exclude_product_tmpl_ids = self.env['product.template']
                valid_product_tmpl_ids = product_tmpl_ids - exclude_product_tmpl_ids

                self.product_tmpl_ids = valid_product_tmpl_ids
                return {"domain": {
                    'product_tmpl_ids': [('id', 'in', valid_product_tmpl_ids.ids), ("is_membership", "=", False)]}}
            else:
                if self.user_membership_plan_ids:
                    product_tmpl_ids = self.env['product.template'].sudo().search([])
                    exclude_product_tmpl_ids = self.env['product.template'].sudo().search([
                        ("user_membership_plan_ids", "in", self.user_membership_plan_ids.ids)])
                    valid_product_tmpl_ids = product_tmpl_ids - exclude_product_tmpl_ids

                    return {"domain": {
                        'product_tmpl_ids': [('id', 'in', valid_product_tmpl_ids.ids), ("is_membership", "=", False)]}}
                else:
                    return {"domain": {'product_tmpl_ids': [("is_membership", "=", False)]}}

        elif self.control_action == "unset":
            domain = []
            if self.public_categ_ids:
                domain.append(("public_categ_ids", "child_of", self.public_categ_ids.ids))
            if self.user_membership_plan_ids:
                domain.append(("user_membership_plan_ids", 'in', self.user_membership_plan_ids.ids))

            product_tmpl_ids = self.env['product.template'].sudo().search(domain)
            if domain:
                self.product_tmpl_ids = product_tmpl_ids
                return {
                    "domain": {'product_tmpl_ids': [('id', 'in', product_tmpl_ids.ids), ("is_membership", "=", False)]}}
            else:
                self.product_tmpl_ids = False
                return {"domain": {'product_tmpl_ids': [("is_membership", "=", False)]}}

    def wizard_submit(self):
        if self.control_action == 'set' and self.product_tmpl_ids:
            val = {
                'name': 'Cron for ' + ", ".join(self.user_membership_plan_ids.mapped('name')),
                'model_id': self.env.ref("product.model_product_template").id,
                'state': 'code',
                'active': True,
                'code': 'model.reset_wizard_action()',
                'user_id': self.user_id.id,
                'interval_number': self.time,
                'user_membership_plan_ids': self.user_membership_plan_ids.ids,
                'product_template_ids': self.product_tmpl_ids.ids,
                'interval_type': 'hours',
                'nextcall': datetime.datetime.now() + datetime.timedelta(hours=self.time),
                'numbercall': 1,
                'doall': False,
                'is_membership': True,
            }
            cron_id = self.env['ir.cron'].create(val)

            plans_to_set = [(4, plan_id, 0) for plan_id in self.user_membership_plan_ids.ids]

            for product_id in self.product_tmpl_ids:
                product_id.not_show_in_website = True
                set_later = True
                if not product_id.user_membership_plan_ids:
                    product_id.msg = self.msg
                    set_later = False

                product_id.user_membership_plan_ids = plans_to_set
                if set_later:
                    product_id.msg = 'Exclusively for ' + ", ".join(
                        product_id.user_membership_plan_ids.mapped('name')) + ' customers'

        elif self.control_action == 'unset' and self.product_tmpl_ids:
            plans_to_unset = [(3, plan_id, 0) for plan_id in self.user_membership_plan_ids.ids]

            for product_id in self.product_tmpl_ids:
                product_id.user_membership_plan_ids = plans_to_unset
                if not product_id.user_membership_plan_ids:
                    product_id.not_show_in_website = False
                    product_id.msg = ''
                else:
                    product_id.msg = 'Exclusively for ' + ", ".join(
                        product_id.user_membership_plan_ids.mapped('name')) + ' customers'
