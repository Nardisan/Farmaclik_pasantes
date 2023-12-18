# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2022-today Botspot Infoware Pvt. Ltd. <www.botspotinfoware.com>
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
#################################################################################
from odoo import api, fields, models, _
from datetime import datetime, date
from datetime import date, timedelta


class ProductProduct(models.Model):
    _inherit = "product.template"

    # default_code = fields.Char(string="Internal Reference")
    # name = fields.Char(string="Name")
    # product_template_attribute_values_id = fields.Many2many('product.template.attribute.value',
    #                                                         string="Attribute Value")
    # lst_price = fields.Float(string="Value Price")
    # standard_price = fields.Float(string="Cost")
    # qty_available = fields.Float(string="Quantity On Hand")
    virtual_available = fields.Float(string="Forecasted Quantity")
    minimum_quantity = fields.Float(string="Minimum Quantity")
    is_minimum_quantity_alert = fields.Boolean(string="Is Minimum Quantity Alert")
    responsible_user_id = fields.Many2one('res.users', string='Responsibles User')
    minimum_quantity_alert_time = fields.Date(string="Minimum Quantity Alert Time")
    
    location_id = fields.Many2many('stock.location','stock_location_rel','product_id','location_id', ondelete="cascade", required=True, domain=[('usage', '=', 'internal')])
    
    

    def run_cron(self):
        mail_dict = {}
        products = []
        dynamic_row = ""
        dates = fields.datetime.today().date()
        product_ids = self.env['product.product'].search([])
        for record in product_ids:
            if record.is_minimum_quantity_alert == True and record.qty_available < record.minimum_quantity:
                if dates == record.minimum_quantity_alert_time:
                    dynamic_row += "<tr><td>{0}</td><td>{1}</td><td>{2}</td></tr>".format(record.default_code,
                                                                                         str(record.minimum_quantity),
                                                                                         str(record.qty_available))
                    super_user = self.env['res.users'].browse(2)
                    mail_dict = {
                                 "subject": 'Sync Products minimum quantity',
                                 "email_from": super_user.partner_id.email_formatted,
                                 "email_to": record.responsible_user_id.name,
                                 "author_id": super_user.partner_id.id,
                                 "body_html": "<p>Hello! </p>" + record.responsible_user_id.name + "<br/> Available quantity is less than Minimum quantity<p>\
                        <br/><br/><table class='table table-sm o_main_table'><thead><tr>\
                        <td>Product Name</td><td>Minimum Quantity</td><td>Available Quantity</td></tr>\
                        </thead> "+dynamic_row + "<tbody></tbody></table>"
                        "<br></br><p> Thanks You </p>"
                                 }
        if mail_dict:
            mail_create = self.env['mail.mail'].create(mail_dict)
            mail_create.send()
