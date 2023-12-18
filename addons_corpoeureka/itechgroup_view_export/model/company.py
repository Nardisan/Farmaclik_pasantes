# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ResCompany(models.Model):
    _inherit = "res.company"

    with_header = fields.Boolean(
        string='With header',
        default=True
    )
    with_header_bar = fields.Boolean(
        string="With bar",
        default=True
    )
    header_bar_color = fields.Char(
        string='Header bar color'
    )
    table_theme = fields.Selection(
        string='Table theme',
        selection=[
            ('striped', 'Striped'),
            ('grid', 'Grid'),
            ('plain', 'Plain')
        ],
        default='striped'
    )
    with_footer = fields.Boolean(
        string='With footer',
        default=True
    )
    with_footer_bar = fields.Boolean(
        string="With bar",
        default=True
    )
    footer_bar_color = fields.Char(
        string='Footer bar color'
    )

    def get_datas(self):
        address_format = "%(street)s - %(street2)s\n%(city)s - %(state_code)s - %(zip)s - %(country_name)s"
        company = self.env.user.company_id.sudo()
        args = {
            'state_code': company.state_id.code or '',
            'country_name': company.country_id.name or '',
            'street': company.street or '',
            'street2': company.street2 or '',
            'zip': company.zip or '',
            'city': company.city or ''
        }
        return {
            'name': company.name or '',
            'email': company.email or '',
            'phone': company.phone or '',
            'website': company.website or '',
            'logo': company.logo,
            'vat': company.vat,
            'street': address_format % args,
            'with_header': company.with_header,
            'header_bar_color': company.header_bar_color,
            'with_header_bar': company.with_header_bar,
            'table_theme': company.table_theme or 'striped',
            'with_footer': company.with_footer,
            'footer_bar_color': company.footer_bar_color,
            'with_footer_bar': company.with_footer_bar
        }
