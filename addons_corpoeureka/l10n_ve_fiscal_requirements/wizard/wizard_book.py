# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError


class WizardExpiredContracts(models.TransientModel):
    _name = "wizard.book"

    date_from = fields.Date('Vence Desde', required=False)
    date_to = fields.Date('Vence Hasta', required=False)
    
    @api.model
    def report_print(self, data):
        print ("hola mundo")
        print ("hola mundo")
        data={
            'date_from': self.date_from,
            'date_to': self.date_to,
        }
        print ('data')
        print (data)
        print ('data')
        return self.env.ref('l10n_ve_fiscal_requirements.shooppin_book').report_action(self, data=data)
        
    @api.constrains('date_from','date_to')
    def _check_date(self):
        '''
        This method validated that the final date is not less than the initial date
        :return:
        '''
        if self.date_to < self.date_from:
            raise UserError(_("The end date cannot be less than the start date "))
