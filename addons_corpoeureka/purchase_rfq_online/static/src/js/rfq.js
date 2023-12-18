odoo.define('purchase_rfq_online.rfq', function (require) {
'use strict';

var publicWidget = require('web.public.widget');

publicWidget.registry.MyPOUpdateLineButton = publicWidget.Widget.extend({
    selector: '.o_portal_purchase_sidebar a.js_update_line_json',
    events: {
        'click': '_onClick',
    },
    /**
     * @override
     */
    start: function () {
        var self = this;
        return this._super.apply(this, arguments).then(function () {
            self.elems = self._getUpdatableElements();
            self.elems.$linePriceUnit.change(function (ev) {
                var price = parseFloat(this.value);
                self._onChangePriceUnit(price);
            });
        });
    },
    /**
     * Process the change in line price unit
     *
     * @private
     * @param {Int} price unit, the new price unit of the line
     *    If not present it will increment/decrement the existing price unit
     */
    _onChangePriceUnit: function (price) {
        var href = this.$el.attr("href");
        var orderID = href.match(/my\/purchase\/([0-9]+)/);
        var lineID = href.match(/update_line\/([0-9]+)/);
        var params = {
                'line_id': parseInt(lineID[1]),
                'remove': this.$el.is('[href*="remove"]'),
                'unlink': this.$el.is('[href*="unlink"]'),
                'input_price': price >= 0 ? price : false,
        };
            var token = href.match(/token=([\w\d-]*)/)[1];
        if (token) {
            params['access_token'] = token;
        }

        orderID = parseInt(orderID[1]);
        this._callUpdateLineRoute(orderID, params).then(this._updateOrderValues.bind(this));
    },
    /**
     * Reacts to the click on the -/+ buttons
     *
     * @param {Event} ev
     */
    _onClick: function (ev) {
        ev.preventDefault();
        return this._onChangePriceUnit();
    },
    /**
     * Calls the route to get updated values of the line and order
     * when the quantity of a product has changed
     *
     * @private
     * @param {integer} order_id
     * @param {Object} params
     * @return {Deferred}
     */
    _callUpdateLineRoute: function (order_id, params) {
        var url = "/my/purchase/" + order_id + "/update_line_dict";
        return this._rpc({
            route: url,
            params: params,
        });
    },
    /**
     * Processes data from the server to update the UI
     *
     * @private
     * @param {Object} data: contains order and line updated values
     */
    _updateOrderValues: function (data) {
        if (!data) {
            window.location.reload();
        }

        var orderAmountTotal = data.order_amount_total;
        var orderAmountUntaxed = data.order_amount_untaxed;
        var orderTotalsTable = $(data.order_totals_table);

        var linePriceUnit = data.order_line_price_unit;
        var linePriceTotal = data.order_line_price_total;
        var linePriceSubTotal = data.order_line_price_subtotal;

        this.elems.$linePriceUnit.val(linePriceUnit);

        if (this.elems.$linePriceTotal.length && linePriceTotal !== undefined) {
            this.elems.$linePriceTotal.text(linePriceTotal);
        }
        if (this.elems.$linePriceSubTotal.length && linePriceSubTotal !== undefined) {
            this.elems.$linePriceSubTotal.text(linePriceSubTotal);
        }

        if (orderAmountUntaxed !== undefined) {
            this.elems.$orderAmountUntaxed.text(orderAmountUntaxed);
        }

        if (orderAmountTotal !== undefined) {
            this.elems.$orderAmountTotal.text(orderAmountTotal);
        }

        if (orderTotalsTable) {
            this.elems.$orderTotalsTable.find('table').replaceWith(orderTotalsTable);
        }
    },
    /**
     * Locate in the DOM the elements to update
     * Mostly for compatibility, when the module has not been upgraded
     * In that case, we need to fall back to some other elements
     *
     * @private
     * @return {Object}: Jquery elements to update
     */
    _getUpdatableElements: function () {
        var $parentTr = this.$el.parents('tr:first');
        var $linePriceTotal = $parentTr.find('.oe_order_line_price_total .oe_currency_value');
        var $linePriceSubTotal = $parentTr.find('.oe_order_line_price_subtotal .oe_currency_value');

        if (!$linePriceTotal.length && !$linePriceSubTotal.length) {
            $linePriceTotal = $linePriceSubTotal = $parentTr.find('.oe_currency_value').last();
        }

        var $orderAmountUntaxed = $('[data-id="total_untaxed"]').find('span, b');
        var $orderAmountTotal = $('[data-id="total_amount"]').find('span, b');

        if (!$orderAmountUntaxed.length) {
            $orderAmountUntaxed = $orderAmountTotal.eq(1);
            $orderAmountTotal = $orderAmountTotal.eq(0).add($orderAmountTotal.eq(2));
        }

        return {
            $linePriceUnit: this.$el.closest('.input-group').find('.js_po_line_price_unit'),
            $linePriceSubTotal: $linePriceSubTotal,
            $linePriceTotal: $linePriceTotal,
            $orderAmountUntaxed: $orderAmountUntaxed,
            $orderAmountTotal: $orderAmountTotal,
            $orderTotalsTable: $('#total'),
        };
    }
});
});
