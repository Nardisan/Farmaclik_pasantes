odoo.define('flexipharmacy.ReturnOrderRow', function (require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');

    /**
     * @props {models.Order} order
     * @props columns
     * @emits click-order
     */
    class ReturnOrderRow extends PosComponent {
        get order() {
            return this.props.order;
        }
        get highlighted() {
            const highlightedOrder = this.props.highlightedOrder;
            return !highlightedOrder ? false : highlightedOrder.backendId === this.props.order.backendId;
        }

        // Column getters //

        get name() {
            return this.order.get_name();
        }
        get date() {
            return moment(this.order.validation_date).format('YYYY-MM-DD hh:mm A');
        }
        get customer() {
            const customer = this.env.pos.db.get_partner_by_id(this.order.partner_id);
            return customer ? customer.name : null;
        }
        get total() {
            return this.env.pos.format_currency(this.order.amount_total);
        }
    }
    ReturnOrderRow.template = 'ReturnOrderRow';

    Registries.Component.add(ReturnOrderRow);

    return ReturnOrderRow;
});
