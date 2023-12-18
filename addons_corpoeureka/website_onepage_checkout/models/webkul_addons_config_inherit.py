# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################

from odoo import api, fields, models, _

class WebkulWebsiteAddons(models.TransientModel):
    _inherit = 'webkul.website.addons'


    
    def get_onepage_configuration_view(self):
        onepage_config_ids = self.env['onepage.checkout.config'].search([])
        ir_model_data = self.env['ir.model.data']
        action = ir_model_data.xmlid_to_object('website_onepage_checkout.action_onepage_checkout_config')
        list_view_id = ir_model_data.xmlid_to_res_id('website_onepage_checkout.onepage_checkout_config_tree')
        form_view_id = ir_model_data.xmlid_to_res_id('website_onepage_checkout.onepage_checkout_config_form')

        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form']],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }
        if len(onepage_config_ids) == 1:
            result['views'] = [(form_view_id, 'form')]
            result['res_id'] = onepage_config_ids[0].id
        return result
