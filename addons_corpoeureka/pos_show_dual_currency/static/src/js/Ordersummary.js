odoo.define('pos_show_dual_currency.OrderSummaryMulti', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');

    class OrderSummaryMulti extends PosComponent {
        get total_sin() {
            return this.order ? this.order.get_total_with_tax() : 0;
        }
        get tax_sin() {
            return this.order ? this.order.get_total_tax() : 0;
        }
    }
    OrderSummaryMulti.template = 'OrderSummaryMulti';

    Registries.Component.add(OrderSummaryMulti);

    return OrderSummaryMulti;
});
