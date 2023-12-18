# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, SUPERUSER_ID

_logger = logging.getLogger(__name__)

class ReconcileWizard(models.TransientModel):
	_name = "pos.reconcile.wizard"
	_description = "Wizard de conciliación de pos"

	filtered_by = fields.Selection([('all', 'Todo'), ('period', 'Período'), ('session', 'Sesión')], string='Filtrado por', default='all', required=True)
	session_ids = fields.Many2many('pos.session', string='Sesiones', domain="[('state', '=', 'closed')]")
	date_from = fields.Date(string='Desde')
	date_to = fields.Date(string='Hasta')

	def reconcile(self):
		self = self.with_user(SUPERUSER_ID)

		filtered_by = ''
		params = [self.env.company.id]

		if self.filtered_by == 'period':
			filtered_by = 'AND pos_order.date_order BETWEEN %s AND %s'
			params += [self.date_from, self.date_to]
		elif self.filtered_by == 'session':
			filtered_by = 'AND pos_order.session_id IN %s'
			params += [tuple(self.session_ids.ids)]

		self._cr.execute('''
			SELECT payment_id, ARRAY_AGG(invoice_id)
			FROM ( SELECT
				account_move_line.id AS invoice_id,
				account_move_line.balance AS invoice_balance, (
					SELECT aml.id
					FROM account_move_line aml
					JOIN pos_session ps ON ps.move_id = aml.move_id
					WHERE
						aml.parent_state = 'posted'
						AND aml.account_id = account_move_line.account_id
						AND aml.partner_id = account_move_line.partner_id
						AND aml.reconciled = FALSE
						AND ps.id = pos_order.session_id
				) AS payment_id, (
					SELECT aml.balance
					FROM account_move_line aml
					JOIN pos_session ps ON ps.move_id = aml.move_id
					WHERE
						aml.parent_state = 'posted'
						AND aml.account_id = account_move_line.account_id
						AND aml.partner_id = account_move_line.partner_id
						AND aml.reconciled = FALSE
						AND ps.id = pos_order.session_id
				) AS payment_balance
			FROM account_move_line
			JOIN account_account ON account_account.id = account_move_line.account_id
			JOIN pos_order ON pos_order.account_move = account_move_line.move_id
			WHERE
				account_move_line.parent_state = 'posted'
				AND account_account.internal_type IN ('receivable', 'payable')
				AND account_move_line.reconciled = FALSE
				AND pos_order.state = 'invoiced'
				AND pos_order.company_id = %s
				'''+ filtered_by +'''
			) AS rows
			GROUP BY payment_id, payment_balance
			HAVING (SUM(invoice_balance) + payment_balance) = 0
		''', params)

		rows = self._cr.fetchall()
		len_rows = len(rows)
		reconciled = 0

		_logger.info('reconciling account.move.line records. (%s / %s)' % (0, len_rows))

		for payment_id, invoice_ids in rows:

			(self.env['account.move.line'].browse(payment_id) + self.env['account.move.line'].browse(invoice_ids)).reconcile()
			reconciled += 1

			if reconciled % 1000 == 0:
				_logger.info('reconciling account.move.line records. (%s / %s)' % (reconciled, len_rows))
				self._cr.commit()

		_logger.info('Finished %s reconciled records.' % reconciled)