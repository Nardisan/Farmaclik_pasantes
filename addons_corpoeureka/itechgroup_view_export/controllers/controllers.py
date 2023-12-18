# -*- coding: utf-8 -*-

import json
import odoo.http as http
from odoo.http import request
from odoo import SUPERUSER_ID
from odoo.addons.web.controllers.main import ExcelExport, CSVExport

def _foramt_data(data):
    data = json.loads(data)
    model = data.get('model', [])
    columns_headers = data.get('headers', [])
    rows = data.get('rows', [])
    return model, columns_headers, rows


class ExcelExportView(ExcelExport):

    def filename(self, base):
        return base.replace('.', '_') + '.xls'

    @http.route('/web/export/xls_view', type='http', auth='user')
    def export_xls_view(self, data, token):
        if not request.env.user.has_group(
            'itechgroup_view_export.group_can_export_view_to_excel') and \
                request.env.uid != SUPERUSER_ID:
            return request.make_response(
                {},
                headers=[],
                cookies={'fileToken': token}
            )

        model, columns_headers, rows = _foramt_data(data)

        return request.make_response(
            self.from_data(columns_headers, rows),
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"'
                 % self.filename(model)),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken': token}
        )


class CSVExportView(CSVExport):

    def filename(self, base):
        return base.replace('.', '_') + '.csv'

    @http.route('/web/export/csv_view', type='http', auth='user')
    def export_xls_view(self, data, token):
        if not request.env.user.has_group(
            'itechgroup_view_export.group_can_export_view_to_csv') and \
                request.env.uid != SUPERUSER_ID:
            return request.make_response(
                {},
                headers=[],
                cookies={'fileToken': token}
            )

        model, columns_headers, rows = _foramt_data(data)

        return request.make_response(
            self.from_data(columns_headers, rows),
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"'
                 % self.filename(model)),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken': token}
        )
