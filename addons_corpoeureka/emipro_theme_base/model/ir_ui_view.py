from odoo import api, fields, models, _

class View(models.Model):
    _inherit = "ir.ui.view"
    
    #Assign correct inherited_id of duplicated view_id for a customize views when customize_show going to switched 
    @api.multi
    def toggle(self):
        super(View,self).toggle()
        current_website_id = self._context.get('website_id')
        duplicated_view=self.env['ir.ui.view'].sudo().search([('active','=',True),('website_id','=',self._context.get('website_id')),('key','=',self.key)])
        for view in duplicated_view.inherit_children_ids :
            if view.website_id.id != current_website_id and view.theme_template_id:
                view.write({'inherit_id': self.id})
    
    #Assign a copied view's inherited id , if view edited from the website            
    @api.multi
    def write(self, vals):
        if self and self[0].theme_template_id and vals.get('inherit_id'):
            if self[0].inherit_id and self[0].inherit_id.website_id == self[0].website_id:
                vals['inherit_id'] = self[0].inherit_id.id
        return super(View, self).write(vals=vals)