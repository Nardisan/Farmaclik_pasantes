# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2007 PRONEXO.COM  (https://www.pronexo.com)
#    All Rights Reserved.
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
# 
{
    'name': 'Additional Fields Signup Form',
    'version': '13.0.1.0.0',
    'category': 'Website',
    'summary': 'Formulario de registro de autenticación con campos adicionales / Auth signup form with extra fields',
    'description': """
        Este módulo agrega número de teléfono, dirección y fecha de nacimiento a la página de registro de autenticación
        * Teléfono
        * Celular
        * Dirección
        * Fecha de nacimiento

        This module add phone number, address and birth date to auth sign up page
        * Phone Number
        * Mobile
        * Address
        * Birth date
    """,
    'sequence': 1,
    'author': "pronexo.com",
    'website': 'https://www.pronexo.com',
    'depends': ['auth_signup','base','contacts','sale','account','website_onepage_checkout','emipro_theme_base','portal'],
    'data': [
        'views/auth_signup_extend_views.xml',
        'views/res_partner_ciudad_view.xml',
        'views/res_partner_sector_view.xml',
        'views/res_partner_view.xml',
        'views/sale_order_view.xml',
        'views/account_move_view.xml',
        'views/stock_picking_view.xml',
        'security/ir.model.access.csv',
        'views/assets.xml',
    ],
    'images': [
        'static/description/auth_signup_banner.png',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3'
}
