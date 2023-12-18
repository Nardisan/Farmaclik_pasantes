from odoo import api, fields, models

class ir_module_module(models.Model):
    _inherit = "ir.module.module"
    
    # Assign correct inherited_id of duplicated view_id for a customize views when theme going to be update
    def _update_records(self, model_name, website):
        super(ir_module_module,self)._update_records(model_name, website)
        
        theme_view_in = self.env['ir.ui.view'].sudo().search([('inherit_id.customize_show','=',True),('theme_template_id','!=',None),('website_id','=',website.id)])
        for cus_view in theme_view_in:
            diplicated_view=self.env['ir.ui.view'].sudo().search([('active','=',True),('key','=',cus_view.inherit_id.key),('website_id','=',website.id)])
            if diplicated_view:
                cus_view.sudo().write({'inherit_id':diplicated_view[0].id})
                