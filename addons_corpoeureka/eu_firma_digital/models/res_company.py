# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError

class ResCompany(models.Model):
    _inherit = 'res.company'

    #def _get_firma(self):
    #    return base64.b64encode(open(os.path.join(tools.config['root_path'], 'addons', 'base', 'static', 'img', 'res_company_firma.png'), 'rb') .read())

    firma = fields.Binary(string="Firma", store=True, attachment=False)
