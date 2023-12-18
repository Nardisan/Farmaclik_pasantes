# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import date

class AccountMove(models.Model):
    _inherit = 'account.move'

    #Manejo de conversiones en la factura 

    #MONTO TOTAL DE REFERENCIA EN BS (recorre las lineas de los productos tomando el precio correcto sin conversion)
    @api.depends('amount_total','manual_currency_exchange_rate')
    def _amount_all_usd(self):
        for record in self:
            record[("amount_ref")]    = record['amount_total']

            domain = 'price_subtotal_ref' 
                
            total = sum(record[("invoice_line_ids")].mapped(domain)) 
            total += record[("amount_tax")] *  record[("manual_currency_exchange_rate")] if record[("currency_id")].name == self.company.currency_id else record[("amount_tax")] /  record[("manual_currency_exchange_rate")] 
               
            record [("amount_ref")] = total

            #if record.manual_currency_exchange_rate != 0:
            #    record[("amount_ref")]    = record['amount_total']*record.manual_currency_exchange_rate
            record[("tasa_del_dia")]     = 1*record.manual_currency_exchange_rate
            record[("tasa_del_dia_two")] = 1/record.manual_currency_exchange_rate


#class AccountMoveLine(models.Model):
 #   _inherit = 'account.move.line'

  #  @api.depends('price_unit','move_id.manual_currency_exchange_rate')
   # def _compute_price_unit_ref(self):
    #    for record in self:
     #       record[("price_unit_ref")] = record['price_unit']
      #      if record.move_id.manual_currency_exchange_rate != 0 and record.display_type == False:
       #         record[("price_unit_ref")] = record['price_unit']*record.move_id.manual_currency_exchange_rate 
                #if record[("currency_id")] == self.env.company.currency_id else record[("price_unit")] /  record[("manual_currency_exchange_rate")] 