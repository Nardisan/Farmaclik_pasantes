# -*- coding: utf-8 -*-
from . import models
from odoo import api, SUPERUSER_ID
from datetime import datetime, timedelta

def post_init_check(cr, registry):
    """ Post init function """
    days_default = 30
    limit_date = datetime.now() - timedelta(days=days_default)

    env = api.Environment(cr, SUPERUSER_ID, {})
    sale_order_obj = env['sale.order']
    #Search Website Sales Team
    #ext_id = env['ir.model.data'].search([('name','=','sales_team.salesteam_website_sales')])
    #if ext_id:
        #website_sales_team = ext_id.res_id
    draft_sales = sale_order_obj.search([('state','in',['draft','sent']),('date_order','<=',limit_date)])
    for sale in draft_sales:
        sale.validity_date = sale.date_order + timedelta(days=days_default)
    sale_order_obj.autocancel_draft_sent_orders()
