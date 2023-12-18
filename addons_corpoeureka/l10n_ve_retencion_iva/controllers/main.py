# -*- coding: utf-8 -*-
import base64
import odoo
from odoo import http
from odoo import fields
from odoo.http import request
from odoo.exceptions import UserError

class AccountIvaTxt(http.Controller):
        
    @http.route('/IvaTXTreports/<int:declarateIva>', type='http', auth="public", website=True, multilang=False)
    def report_txt_massive(self,declarateIva,**kwargs):
        headers = [('Content-Type', 'text/plain')]
        declarateIvaObj = request.env['account.wh.iva.declared'].sudo().search([('id','=',int(declarateIva))])
        wh_iva_obj = request.env['account.wh.iva']
        wh_iva = wh_iva_obj.sudo().search([('id','in',list(map(lambda x: x.id, declarateIvaObj.wh_ids)))])
        content = wh_iva_obj.sudo().act_getfile(wh_iva,declarateIvaObj.period)
        txt = base64.b64decode(content)
        headers.append(('Content-Length', len(txt)))
        response = request.make_response(txt, headers)
        response.headers.add('Content-Disposition', 'attachment; filename=TXT_consulta.txt;')
        return response
    
    @http.route('/reportTxtDeclarate/<int:declarateIva>', type='http', auth="public", website=True, multilang=False)
    def report_txt_declarate(self,declarateIva,**kwargs):
        headers = [('Content-Type', 'text/plain')]
        declarateIvaObj = request.env['account.wh.iva.declared'].search([('id','=',int(declarateIva))])
        wh_iva_obj = request.env['account.wh.iva']
        company_id = request.env.company
        wh_iva = wh_iva_obj.sudo().search([('id','in',list(map(lambda x: x.id, declarateIvaObj.wh_ids)))])
        content = wh_iva_obj.sudo().act_getfile(wh_iva,declarateIvaObj.period)
        attach_id = wh_iva_obj.sudo().create_attachment(content,company_id)
        value = {}
        value['file_txt_id'] = [[6, False, [attach_id.id]]]
        value['state'] = 'declared'
        value['period'] = declarateIvaObj.period
        if wh_iva:
            for wh in wh_iva:
                wh.write(value)
                for whl in wh.wh_lines:
                    if whl.state != 'annulled':
                        whl.write({'state':'declared'})
        txt = base64.b64decode(content)
        headers.append(('Content-Length', len(txt)))
        response = request.make_response(txt, headers)
        response.headers.add('Content-Disposition', 'attachment; filename=TXT_declarión.txt;')
        return response
