# -*- coding: utf-8 -*-

import logging
import werkzeug

import pytz
import datetime
from odoo import modules, tools
from odoo import api, fields, models, _, SUPERUSER_ID


from odoo import http, _
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.exceptions import UserError
from odoo.http import request

_logger = logging.getLogger(__name__)


class AuthSignupHome(AuthSignupHome):
    def do_signup(self, qcontext):

        """ Shared helper that creates a res.partner out of a token """
        if not qcontext.get('reset_present'):
            
            values = {key: qcontext.get(key) for key in ('name', 'cedula',  'phone', 
                                                         'street', 'ciudad', 'sector','login','password','state_id','country_id','city')}
            
            ciudades = False
            nombreciudad = False
            pais   = request.env['res.country'].sudo().search([('name', '=', 'Venezuela')], limit=1)
            estado=False
            if qcontext.get('sector'): #se agregaron s a este y ciudad
                values.update({'sector': int(qcontext.get('sector'))})
            # if qcontext.get('estado'):
            #     values.update({'estado': int(qcontext.get('estado'))})
            if qcontext.get('ciudad'):
                
                ciudades = request.env['res.partner.ciudad'].sudo().search([('id', '=', int(qcontext.get('ciudad')))], limit=1)
                estado   = request.env['res.country.state'].sudo().search([('id','=',ciudades.state_id.id)], limit=1) #pongan el nombre del estado
                values.update({'ciudad': int(qcontext.get('ciudad'))})
            if ciudades:
                for rec in ciudades:
                    nombreciudad = rec.name
            if nombreciudad:
                values.update({'city': str(nombreciudad)})
            if pais.id:
                values.update({'country_id': int(pais.id)})
            if not estado:
                    estado   = request.env['res.country.state'].sudo().search([('country_id','=',pais.id)], limit=1) #pongan el nombre del estado
            if estado.id:
                
                values.update({'state_id': int(estado.id)})
            
        else:
            values = {key: qcontext.get(key) for key in ('login','password')}
        if not values:
            raise UserError(_("The form was not properly filled in."))
        if values.get('password') != qcontext.get('confirm_password'):
            raise UserError(_("Passwords do not match; please retype them."))
        supported_lang_codes = [code for code, _ in request.env['res.lang'].get_installed()]
        lang = request.context.get('lang', '').split('_')[0]
        if lang in supported_lang_codes:
            values['lang'] = lang

        self._signup_with_values(qcontext.get('token'), values)
        
        
        request.env.cr.commit()


    # @http.route('/web/signup/ex45/addopn', type='http', auth='public', website=True, sitemap=False)
    # def web_auth_actualizardatos(self, values_name,val_dic,city_id):
    #     # user=request.env['res.users'].search([('id','=',request.session.uid)])
    #     raise UserError("asdawsdasd")
    #     for val in values_name:
            
    #         user.val=val_dic[values_name]
    #     user.city=request['res.partner.ciudad'].search([('id','=',city_id)]).name
            

    @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):
    
        qcontext = self.get_auth_signup_qcontext()
        qcontext.update(request.params.copy())
        # qcontext['estado'] = request.env['res.country.state'].sudo().search([])
        qcontext['sectors'] = request.env['res.partner.sectores'].sudo().search([])
        qcontext['ciudads'] = request.env['res.partner.ciudad'].sudo().search([])
        
        if not qcontext.get('token') and not qcontext.get('signup_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            
            try:
                self.do_signup(qcontext)
                # Send an account creation confirmation email
                if qcontext.get('token'):
                    user_sudo = request.env['res.users'].sudo().search([('login', '=', qcontext.get('login'))])
                    template = request.env.ref('auth_signup.mail_template_user_signup_account_created',
                                               raise_if_not_found=False)
                    if user_sudo and template:
                        template.sudo().with_context(
                            lang=user_sudo.lang,
                            auth_login=werkzeug.url_encode({'auth_login': user_sudo.email}),
                        ).send_mail(user_sudo.id, force_send=True)
                return self.web_login(*args, **kw)
            except UserError as e:
                qcontext['error'] = e.name or e.value
            except (SignupError, AssertionError) as e:
                if request.env["res.users"].sudo().search([("login", "=", qcontext.get("login"))]):
                    qcontext["error"] = _("Another user is already registered using this email address.")
                else:
                    _logger.error("%s", e)
                    qcontext['error'] = _("Could not create a new account.")

        response = request.render('auth_signup.signup', qcontext)
        response.headers['X-Frame-Options'] = 'DENY'
        return response
