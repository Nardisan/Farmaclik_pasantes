# -*- coding: utf-8 -*-

from odoo import fields, models  # noqa


class TributaryUnit(models.Model):
    _name = "tributary.unit"
    _description = "Tributary Unit in Venezuela"
    _order = "name desc"

    name = fields.Date(
        string="Gazette Date",
        required=True,
        index=True,
        default=lambda self: fields.Date.today(),
    )
    gazette = fields.Char(string="Official Gazette Nº", required=True)
    amount = fields.Float(string="Amount", required=True)
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )

    _sql_constraints = [
        (
            "unique_tributary_date",
            "unique (name,company_id)",
            "Only one tributary unit per date allowed!",
        ),
        ("amount_check", "CHECK (amount>0)", "The amount must be strictly positive."),
    ]

    def name_get(self):
        # Prefetch the fields used by the `name_get`, so `browse` doesn't fetch other fields
        self.browse(self.ids).read(['name', 'amount'])
        return [(template.id, '%s%s' % (template.amount and 'Monto: %s Fecha: ' % template.amount or '', template.name))
                for template in self]