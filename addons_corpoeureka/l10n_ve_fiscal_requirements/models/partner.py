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

class ResPartner(models.Model):
    _inherit = "res.partner"

    rif = fields.Char(string="RIF", required=False)
    vd_rif = fields.Integer(string="Dígito Validador RIF",compute="_compute_vd_rif")
    cedula = fields.Char(string="Cédula o RIF",size=10)
    street = fields.Char(required=True)
    city = fields.Char(required=True)
    state_id = fields.Many2one(required=True)
    country_id = fields.Many2one(required=True)
    residence_type = fields.Selection([('SR','Sin RIF'),
                                      ('R', 'Residenciado'),
                                      ('NR', 'No residenciado'),
                                      ('D', 'Domiciliado'),
                                      ('ND', 'No domiciliado')], help='This is the Supplier Type')

    
    # @api.constrains('rif')
    # def _check_rif(self):
    #     if self.rif:
    #         if self.is_company:
    #             formate = (r"[JG]{1}[-]{1}[0-9]{8}")
    #         else:
    #             formate = (r"[PVE]{1}[-]{1}[0-9]{8}")
    #         form_rif = re.compile(formate)
    #         records = self.env['res.partner']
    #         rif_exist = records.search_count([('cedula', '=', self.rif),('id', '!=', self.id)])
    #         for partner in self:
    #             if not form_rif.match(partner.cedula):
    #                 if self.is_company:
    #                     raise ValidationError(("El formato del RIF es incorrecto por favor introduzca un RIF de la forma J-123456789 (utilice solo las letras J y G)"))
    #                 else:
    #                     raise ValidationError(("El formato del RIF es incorrecto por favor introduzca un RIF de la forma V-123456789 (utilice solo las letras V y E)"))
    #             #verificar si no existe un registro con el mismo rif
    #             elif rif_exist > 0:
    #                 raise ValidationError(
    #                     ("Ya existe un registro con este rif"))
    #             else:
    #                 return True
    @api.onchange('rif','cedula')
    def _onchange_rif_to_vat(self):
        if self.cedula:
            self.vat = self.cedula.upper()
            self.cedula = self.cedula.upper()
        if self.rif:
            self.vat = self.rif.upper()
            self.rif = self.rif.upper()


    @api.constrains('cedula')
    def _check_cedula(self):
        if self.cedula:
            formate = (r"[JGPVE]{1}[-]{1}[0-9]{8}")
            form_ci = re.compile(formate)
            records = self.env['res.partner']
            cedula_exist = records.search_count([('cedula', '=', self.cedula),('id', '!=', self.id)])
            for partner in self:
                if not form_ci.match(partner.cedula):
                    raise ValidationError(("El formato de la cedula es incorrecto. Por favor introduzca una cédula de la forma V-12345678"))
                elif cedula_exist > 0:
                    raise ValidationError(("Ya existe un registro con este número de cédula"))
                else:
                    return True

    @api.depends('cedula')
    def _compute_vd_rif(self):
        for rec in self:
            rec.vd_rif= 0
            if rec.cedula:
                cedula = rec.cedula.replace('-','')
                base = {'V': 4, 'E': 8, 'J': 12, 'G': 20}
                oper = [0, 3, 2, 7, 6, 5, 4, 3, 2]
                val = 0
                for i in range(len(cedula[:9])):
                    val += base.get(cedula[0], 0) if i == 0 else oper[i] * int(cedula[i])
                digit = 11 - (val % 11)
                digit = digit if digit < 10 else 0
                rec.vd_rif = digit
                rec.rif = str(cedula[0]) + '-' +  str(cedula[1:]) + str(digit)


