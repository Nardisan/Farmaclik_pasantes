# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    multi_serie     =   fields.Boolean(string="Multiserie company",invisible=True, related="company_id.multi_serie")
    account_serie   =   fields.Selection(
        [
        ('a', 'Serie A'), 
        ('b', 'Serie B'),
        ('c', 'Serie C')
        ], 
        string="Tipo de Serie",
        default="a",
        related="journal_id.account_serie",
        store=True)
    serie_sequence  =   fields.Char(string="Número Serie",readonly=True,default="/",copy=False)
    
    @api.model    
    def post(self):
        sequence_code = ''
        for rec in self:
            if rec.account_serie:
                if rec.serie_sequence == '/':
                    if rec.move_type=='out_invoice':
                        if rec.account_serie == 'a':
                            sequence_code = "account.serie.a.seq"
                        if rec.account_serie == 'b':
                            sequence_code = "account.serie.b.seq"
                        if rec.account_serie == 'c':
                            sequence_code = "account.serie.c.seq"
                    if rec.move_type=='out_refund':
                        if rec.account_serie == 'a':
                            sequence_code = "account.serie.ar.seq"
                        if rec.account_serie == 'b':
                            sequence_code = "account.serie.br.seq"
                        if rec.account_serie == 'c':
                            sequence_code = "account.serie.cr.seq"
                    rec.serie_sequence = self.env['ir.sequence'].next_by_code(sequence_code)
        return super(AccountMove, self).post()

    @api.onchange('partner_id')
    def _account_serie_change(self):
        for rec in self:
            rec.account_serie = rec.journal_id.account_serie



class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    account_serie = fields.Selection(related='move_id.account_serie',string="Tipo de Serie",store=True)