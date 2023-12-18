# -*- coding: utf-8 -*-
#############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import re

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class AccountTaxTemplate(models.Model):
    _inherit = "account.tax.template"

    aliquot_type = fields.Selection([('reduced', 'Reduced'),
                                     ('general', 'General'),
                                     ('additional','Additional')],string="Tipo de alicuota", required=False)

class AccountTax(models.Model):
    _inherit = "account.tax"

    aliquot_type = fields.Selection([('reduced', 'Reduced'),
                                     ('general', 'General'),
                                     ('additional','Additional')],string="Tipo de alicuota", required=False)