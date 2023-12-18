# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import odoo
from odoo import http
from odoo import fields
from odoo.http import request
import xml.etree.ElementTree as ET
from io import StringIO, BytesIO


class AccountIslr(http.Controller):
        
    @http.route('/printReportIslr/<int:withholding>', type='http', auth="public", website=True, multilang=False)
    def print_report_inslr(self,withholding,**kwargs):
        withholding_obj = request.env['account.wh.islr']
        withholding = withholding_obj.sudo().search([('id','=',int(withholding))])
        arbol=withholding_obj.sudo().generate_file_xml(withholding)
        f = BytesIO()
        arbol.write(f, encoding="ISO-8859-1", xml_declaration=True)
        f.seek(0)
        file=f.read()
        xlshttpheaders = [('Content-Type', 'application/xml'), ('Content-Length', len(file))]
        response=request.make_response(file, headers=xlshttpheaders)
        response.headers.add('Content-Disposition', 'attachment; filename=Pago_ISLR.xml;')
        return response
        
    @http.route('/printReportIslrMassive/<int:declarateIslr>', type='http', auth="public", website=True, multilang=False)
    def print_report_inslr_massive(self,declarateIslr,**kwargs):
        declarateIslrObj = request.env['account.declarate.islr'].sudo().search([('id','=',int(declarateIslr))])
        withholding_obj = request.env['account.wh.islr']
        withholding = withholding_obj.sudo().search([('id','in',list(map(lambda x: x.id, declarateIslrObj.withholding_ids)))])
        arbol=withholding_obj.sudo().generate_file_xml(withholding,declarateIslrObj.period)
        f = BytesIO()
        arbol.write(f, encoding="ISO-8859-1", xml_declaration=True)
        f.seek(0)
        file=f.read()
        xlshttpheaders = [('Content-Type', 'application/xml'), ('Content-Length', len(file))]
        response=request.make_response(file, headers=xlshttpheaders)
        response.headers.add('Content-Disposition', 'attachment; filename=Pago_ISLR.xml;')
        return response
        
        
        
        
        
        
        
    
        
