# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from itertools import groupby
from collections import Counter


class StockPicking(models.Model):
    _inherit='stock.picking'



    def _create_move_from_pos_order_lines(self, lines):
        print("SALDASKLDJWQ")
        print("SALDAsfadsfsdfsdfsfSKLDJWQ")
        print("SALDASdfsgfdgfsgKLDJWQ")
        print("SALDASdfsgfdgfsgKLDJWQ")
        print("SALDASdfsgfdgfsgKLDJWQ")
        print("SALDASKLDJWQ")
        self.ensure_one()
        lines_by_product = groupby(sorted(lines, key=lambda l: (l.product_id.id,l.product_uom_id.id)), key=lambda l: (l.product_id.id,l.product_uom_id.id))
        for product, lines in lines_by_product:
            order_lines = self.env['pos.order.line'].concat(*lines)
            first_line = order_lines[0]
            current_move = self.env['stock.move'].create(
                self._prepare_stock_move_vals(first_line, order_lines)
            )
            confirmed_moves = current_move._action_confirm()
            for move in confirmed_moves:
                if first_line.product_id == move.product_id and first_line.product_id.tracking != 'none':
                    if self.picking_type_id.use_existing_lots or self.picking_type_id.use_create_lots:
                        for line in order_lines:
                            sum_of_lots = 0
                            print("((((line.pack_lot_ids))))")
                            print(line.pack_lot_ids)
                            print(line.pack_lot_ids.filtered(lambda l: l.lot_name))
                            pack_lots = []
                            for value in line.pack_lot_ids.filtered(lambda l: l.lot_name):
                                print(value.lot_name)
                                pack_lots.append(value.lot_name)
                            print(Counter(pack_lots))
                            # pack_lots = set(pack_lots)
                            # for lot in line.pack_lot_ids.filtered(lambda l: l.lot_name):
                            for lot in Counter(pack_lots):
                                print(lot)
                                # if line.product_id.tracking == 'serial':
                                #     qty = 1
                                # else:
                                #     qty = abs(line.qty)
                                ml_vals = move._prepare_move_line_vals()
                                ml_vals.update({'qty_done':abs(Counter(pack_lots)[lot])})
                                if self.picking_type_id.use_existing_lots:
                                    existing_lot = self.env['stock.production.lot'].search([
                                        ('company_id', '=', self.company_id.id),
                                        ('product_id', '=', line.product_id.id),
                                        ('name', '=', lot)
                                    ])
                                    if not existing_lot and self.picking_type_id.use_create_lots:
                                        existing_lot = self.env['stock.production.lot'].create({
                                            'company_id': self.company_id.id,
                                            'product_id': line.product_id.id,
                                            'name': lot,
                                        })
                                    ml_vals.update({
                                        'lot_id': existing_lot.id,
                                    })
                                else:
                                    ml_vals.update({
                                        'lot_name': lot,
                                    })
                                print("ml_vals here")
                                print(ml_vals)
                                self.env['stock.move.line'].create(ml_vals)
                                sum_of_lots += abs(Counter(pack_lots)[lot])
                            if abs(line.qty) != sum_of_lots:
                                difference_qty = abs(line.qty) - sum_of_lots
                                ml_vals = current_move._prepare_move_line_vals()
                                if line.product_id.tracking == 'serial':
                                    ml_vals.update({'qty_done': 1})
                                    for i in range(int(difference_qty)):
                                        print("ooi")
                                        print(ml_vals)
                                        self.env['stock.move.line'].create(ml_vals)
                                else:
                                    ml_vals.update({'qty_done': difference_qty})
                                    print("hgjh  -")
                                    print(ml_vals)
                                    self.env['stock.move.line'].create(ml_vals)
                    else:
                        move._action_assign()
                        sum_of_lots = 0
                        for move_line in move.move_line_ids:
                            move_line.qty_done = move_line.product_uom_qty
                            sum_of_lots += move_line.product_uom_qty
                        if float_compare(move.product_uom_qty, move.quantity_done, precision_rounding=move.product_uom.rounding) > 0:
                            remaining_qty = move.product_uom_qty - move.quantity_done
                            ml_vals = move._prepare_move_line_vals()
                            ml_vals.update({'qty_done':remaining_qty})
                            print("guiyuy")
                            print(ml_vals)
                            self.env['stock.move.line'].create(ml_vals)

                else:
                    move.quantity_done = move.product_uom_qty
