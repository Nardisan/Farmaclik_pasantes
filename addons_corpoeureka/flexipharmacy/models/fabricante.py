# -*- coding: utf-8 -*-
#################################################################################
# Author      : Yorbel Perez
# Copyright(c): All Rights Reserved.
# 
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################
from odoo import fields, models


class Fabricante(models.Model):
    _name = 'fabricante'
    _description = 'Fabricante o laboratrio del producto'

    name = fields.Char('Nombre') 