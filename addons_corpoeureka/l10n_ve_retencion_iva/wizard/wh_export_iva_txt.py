# -*- coding: utf-8 -*-
import base64
import contextlib
from io import StringIO
from odoo import api, fields, models, tools, _

NEW_LANG_KEY = '__new__'

class AccountIvaTxtExport(models.TransientModel):
    _name = "account.iva.txt.export"

    name = fields.Char('File Name', readonly=True)
    format = fields.Selection([('csv','CSV File'), ('txt','PO File'), ('tgz', 'TGZ Archive')],
                              string='File Format', default='txt')
    data = fields.Binary('File', readonly=True)
    state = fields.Selection([('choose', 'choose'), ('get', 'get')],
                             default='get')

