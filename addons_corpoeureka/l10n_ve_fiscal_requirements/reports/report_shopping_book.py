# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ReportAccountHashIntegrity(models.AbstractModel):
    _name = 'report.l10n_ve_fiscal_requirements.report_shooping_book'

    @api.model
    def _get_report_values(self, docids, data=None):
        print "AAAAAAAAAAAA"
        print "AAAAAAAAAAAA"
        print "AAAAAAAAAAAA"
        print "AAAAAAAAAAAA"
        print "AAAAAAAAAAAA"
        return {
            'doc_ids': ,
            'doc_model': 'account.move',
            'docs': ,
        }
