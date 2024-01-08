# -*- coding: utf-8 -*-

from odoo import models, fields, api


class add_invoice_number(models.Model):
    """
    Añade el campo de nro de proveedor a la factura de proveedor extendiendo el modelo account.move
    """
    _inherit = 'account.move'
    _description = 'add_invoice_number.add_invoice_number'

    vendor_invoice_number_inherit = fields.Char(related='vendor_invoice_number', string='Nro factura proveedor')
