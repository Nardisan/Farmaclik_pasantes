# -*- coding: utf-8 -*-

##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

{
    "name": "Localización Venezolana: Municipios y Parroquias",
    "version": "10.0.2",
    'author': 'Kiran Kantesariya',
    'skype': 'kiran.backup0412@gmail.com',
    "category": "Localization",
    "description":
        """
Localización Venezolana: Municipios y Parroquias
================================================

Basado en información del INE del año 2013, añade los campos de municipio y parroquia en el modelo `res.partner` de
manera que queden disponibles en todos los campos de dirección en modelos derivados como `res.users` o `res.company`.
     """,
    "JPV": "BachacoVE",
	'images': ['static/description/icon.png'],
    "depends": [
            'base', 
            'contacts'],
    "init_xml": [],
    "demo_xml": [],
    "data": [

        'query.sql',
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/l10n_ve_dpt_view.xml',
        'views/res_partner.xml',
        'views/res_company.xml',
        'data/res_country_state.xml',
        'data/res_country_state_city.xml',
        'data/update.sql',
        'data/res_country_state_municipality.xml',
        'data/res_country_state_municipality_parish.xml',


    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
