# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import re

skip_modules = ["bus.presence", "mail.*", "ir.translation", "ir.default", "ir.module.module", "base.module*",
                "user_actions_notifier*", "ir.property", "ir.attachment"]


def save_notifier_record(self, report_type: str):
    """
    Metodo que crea el registro de la accion realizada por el usuario solo si esta monitoreada
    """
    try:

        model_name = ""

        if hasattr(self, "model") and self.model is not False and self.model is not None:
            model_name = self.model
        elif hasattr(self, "_name"):
            model_name = self._name
        elif hasattr(self, "_inherit"):
            model_name = self._inherit

        # omitir modulos en skip_modules
        for module in skip_modules:
            if re.match(module, model_name):
                return

        user_id = self.env.user.id

        actions = self.env["user_actions_notifier.user_actions"] \
            .search([("name", "ilike", report_type)])
        actions_ids = actions.mapped("id")
        company_id = self.env.user.company_id
        monitor = (self.env["user_actions_notifier.monitor"]
                   .search([("users", "in", [user_id]), ("actions", "in", actions_ids)]))

        if len(monitor) > 0:
            self.env["user_actions_notifier.notifier"] \
                .sudo().create({
                "user": user_id,
                "action": actions_ids[0],
                "model": model_name,
                "company": company_id.id,
                "monitor": monitor.id
            })
    except Exception as e:
        # print("ERROR")
        # print(e.__str__())
        return


class UserAction(models.Model):
    """
    Tabla que contiene las acciones que puede realizar un usuario
    """
    _name = 'user_actions_notifier.user_actions'
    _description = 'Acciones que puede realizar un usuario'
    _disable_action_monitor = True

    # Action name
    name = fields.Char(string="Accion", required=True, unique=True)
    # Action description
    description = fields.Char(string="Descripcion", optional=True)


class UserActionsNotifier(models.Model):
    """
    Tabla que contiene los registros de las acciones monitoreadas de los usuarios
    """
    _name = 'user_actions_notifier.notifier'
    _description = 'Registro de acciones de usuarios monitoreadas'
    _disable_action_monitor = True

    _rec_name = "monitor"
    # reference to user
    user = fields.Many2one('res.users', string="Usuario", required=True, relation='notifier_res_user_rel',
                           ondelete="cascade"
                           )
    # reference to action
    action = fields.Many2one(
        'user_actions_notifier.user_actions', string="Accion", required=True, relation='notifier_user_actions_rel',
        ondelete="cascade"
    )
    # model where action was made
    model = fields.Char(string="Modelo", required=True)
    # company where the user is
    company = fields.Many2one('res.company', string="Compañia", required=True)

    monitor = fields.Many2one('user_actions_notifier.monitor', string="Regla relacionada", required=True,
                              relation="notifier_monitor_rel", ondelete="cascade")

    @api.model
    def create(self, vals):
        """
        Metodo que crea el registro de la accion realizada por el usuario solo si esta monitoreada
        """
        record = super().create(vals)
        action_id = vals['action']
        user_id = vals['user']
        monitor = self.env['user_actions_notifier.monitor'] \
            .search([('users', 'in', [user_id]), ('actions', 'in', [action_id])])
        # este campo nunca devuelve resultados a pesar de que hay un usuario y una action que coincide

        # if the user and the action are monitored, then create the record
        if monitor is not None and len(monitor) > 0:
            return record

    def __str__(self):
        return f"""
        user: {self.user}
        action: {self.action}
        model: {self.model}
        company: {self.company}
        monitor: {self.monitor}
        """


# tabla seguimiento de acciones

class UserActionsMonitor(models.Model):
    """
    Tabla que contiene los usuarios y las acciones que se van a monitorear
    """
    _name = 'user_actions_notifier.monitor'

    _description = 'Seguimiento de acciones de usuarios'

    _disable_action_monitor = True

    name = fields.Char(string="Nombre regla", required=True)

    users = fields.Many2many('res.users', required=True, relation='monitor_res_user_rel',
                             ondelete="cascade"
                             )

    entries = fields.One2many('user_actions_notifier.notifier', 'monitor', string="Entradas registradas",
                              required=True)

    actions = fields.Many2many(
        'user_actions_notifier.user_actions', required=False, relation='monitor_user_actions_rel',
        ondelete="cascade"
    )

    @api.constrains("users", "actions")
    def _check_users_actions(self):
        """
        Solo puede haber un usuario asignado a la misma regla. No se pueden repetir reglas para un mismo usuario pero
        si pueden haber varias reglas y usuarios repetidos siempre y cuando no se repita la accion para el mismo usuario
        """
        for record in self:
            users_ids = record.users.ids
            actions_ids = record.actions.ids
            monitor = self.env['user_actions_notifier.monitor'] \
                .search([('users', 'in', users_ids), ('actions', 'in', actions_ids), ('id', 'not in', record.ids)])

            """
            monitor_info = [(m.name, u.name, a.name) for m in monitor for u in m.users for a in m.actions]

            record_info = [(record.name, u.name, a.name) for u in record.users for a in record.actions]

            intersection = set(monitor_info).intersection(set(record_info))
            """

            monitor_info = [(m.name, u.name, a.name) for m in monitor for u in m.users for a in m.actions]

            if len(monitor) > 0 and monitor.ids[0] != record.ids[0]:
                monitor_str = "\n".join([", ".join(info) for info in monitor_info])
                raise ValidationError("Hay conflictos entre los siguientes monitores, usuarios y acciones:\n{}"
                                      .format(monitor_str))


class ReportWithRecords(models.Model):
    _inherit = 'ir.actions.report'

    def _get_rendering_context(self, docids, data):
        save_notifier_record(self, "imprimir")

        return super(ReportWithRecords, self)._get_rendering_context(docids, data)


class BaseWithReportRecords(models.AbstractModel):
    """
    Clase abstracta que hereda de base y que se encarga de monitorear las acciones de los usuarios.
    La idea es guardar registros sobre las creaciones, modificaciones y eliminaciones de los registros de los modelos.
    Esta clase sobreescribe los metodos create, write y unlink en todos los modelos de odoo.
    """
    _inherit = 'base'
    _disable_action_monitor = False

    @api.model
    def create(self, vals):
        record = super().create(vals)

        save_notifier_record(self, "crear")

        return record

    @api.model
    def write(self, vals):
        record = super().write(vals)

        save_notifier_record(self, "modificar")

        return record

    def unlink(self, *args):
        save_notifier_record(self, "eliminar")

        return super(BaseWithReportRecords, self).unlink()
