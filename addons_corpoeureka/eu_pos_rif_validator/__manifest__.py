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
    "name": "Validador de RIF en PoS",
    "version": "14.0.1.0",
    "author": "CorpoEureka",
    "category": "Localization",
    "description":
        """
Validador de RIF en PoS
     """,
    "website": "http://www.corpoeureka.com/",
	'images': ['static/description/icon.png'],
    "depends": ['base','point_of_sale','l10n_ve_fiscal_requirements'],
    "init_xml": [],
    "demo_xml": [],
    "data": [
        'views/point_of_sale.xml',
    ],
    "installable": True
}
