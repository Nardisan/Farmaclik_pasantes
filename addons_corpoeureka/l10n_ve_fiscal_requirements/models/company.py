# -*- coding: utf-8 -*-
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################
import re

from odoo import api, fields, models, tools
from odoo.exceptions import ValidationError

class ResCompany(models.Model):
    _inherit = 'res.company'

    #Columns
    rif = fields.Char(string='RIF', required=True)
    currency_id_ref = fields.Many2one('res.currency',string="Monedas de las Retenciones",default=lambda self: self.env['res.currency'].search(['|',('name', '=', 'VES'),('name', '=', 'VEF')], limit=1))

    @api.constrains('rif')
    def _check_rif(self):
        formate = (r"[JG]{1}[-]{1}[0-9]{9}")
        form_rif = re.compile(formate)
        records = self.env['res.company']
        rif_exist = records.search_count([('rif', '=', self.rif),('id', '!=', self.id)])
        for company in self:
            if not form_rif.match(company.rif):
                raise ValidationError(("El formato del RIF es incorrecto por favor introduzca un RIF de la forma J-123456789 (utilice solo las letras J y G)"))
            #elif rif_exist > 0:
            #    raise ValidationError(("Ya existe un registro con este RIF"))
            else:
                return True
