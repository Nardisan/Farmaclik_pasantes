odoo.define('flexipharmacy.ReturnOrderScreen', function (require) {
    'use strict';

    const { useContext, useState } = owl.hooks;
    const { useListener } = require('web.custom_hooks');
    const ControlButtonsMixin = require('point_of_sale.ControlButtonsMixin');
    const NumberBuffer = require('point_of_sale.NumberBuffer');
    const Registries = require('point_of_sale.Registries');
    const ReturnOrderFetcher = require('flexipharmacy.ReturnOrderFetcher');
    const IndependentToOrderScreen = require('point_of_sale.IndependentToOrderScreen');
    const contexts = require('flexipharmacy.PosContext');
    const models = require('point_of_sale.models');

    class ReturnOrderScreen extends ControlButtonsMixin(IndependentToOrderScreen) {
        constructor() {
            super(...arguments);
            useListener('close-screen', this.close);
            useListener('set-numpad-mode', this._setNumpadMode);
            useListener('click-order', this._onClickOrder);
            useListener('next-page', this._onNextPage);
            useListener('prev-page', this._onPrevPage);
            useListener('search', this._onSearch);
            useListener('serialNumberPopup', this.OpenSerialNumberPopup);
            this.state = useState({orders:[], orderlines:[], ReturnAllProduct: false, SelectedLotSerialList: []})
            NumberBuffer.use({
                nonKeyboardInputEvent: 'numpad-click-input',
                useWithBarcode: true,
            });
            this.numpadMode = 'quantity';
            ReturnOrderFetcher.setComponent(this);
            ReturnOrderFetcher.setConfigId(this.env.pos.config_id);
            this.orderManagementContext = useContext(contexts.returnOrderManagement);
            this.orderManagementContext.selectedOrder = null
        }
        mounted() {
            ReturnOrderFetcher.on('update', this, this.render);
            const flexContainer = this.el.querySelector('.flex-container');
            const cpEl = this.el.querySelector('.control-panel');
            const headerEl = this.el.querySelector('.order-row.header');
            const val = Math.trunc(
                (flexContainer.offsetHeight - cpEl.offsetHeight - headerEl.offsetHeight) /
                    headerEl.offsetHeight
            );
            ReturnOrderFetcher.setNPerPage(val);

            setTimeout(() => ReturnOrderFetcher.fetch(), 0);
        }
        willUnmount() {
            ReturnOrderFetcher.off('update', this);
            this.env.pos.get('orders').off('add remove', null, this);
        }
        async OpenSerialNumberPopup(event) {
            var LineSerialNumber = []
            var SelectedLineSerialNumber = []
            _.each(event.detail.operation_lot_name, function(value,key) {
                var lot = {'id': key, 'name': value.lot_name}
                LineSerialNumber.push(lot)
            });
            const { confirmed, payload} = await this.showPopup(
                'SelectedSerialNumberPopup',
                {
                    title: this.env._t('Select Serial Number'),
                    numberlist: LineSerialNumber,
                }
            );

            if (confirmed) {
                _.each(payload, function(number) {
                    var lot = {lot_name: number.name}
                    SelectedLineSerialNumber.push(lot)
                });
                event.detail.line['select_operation_lot_name'] = SelectedLineSerialNumber
                event.detail.line['return_qty'] = SelectedLineSerialNumber.length
            }

        }
        get selectedClient() {
            const order = this.orderManagementContext.selectedOrder;
            return order ? order.get_client() : null;
        }
        get orders() {
            return ReturnOrderFetcher.get();
        }
        async _setNumpadMode(event) {
            const { mode } = event.detail;
            this.numpadMode = mode;
            NumberBuffer.reset();
        }
        _onNextPage() {
            ReturnOrderFetcher.nextPage();
        }
        _onPrevPage() {
            ReturnOrderFetcher.prevPage();
        }
        _onSearch({ detail: domain }) {
            ReturnOrderFetcher.setSearchDomain(domain);
            ReturnOrderFetcher.setPage(1);
            ReturnOrderFetcher.fetch();
        }
        async _onClickOrder({ detail: clickedOrder }) {
            var self = this;
            if (!clickedOrder || clickedOrder.locked){
                var params = {
                    model: 'pos.order',
                    method: 'export_for_ui_custom',
                    args: [clickedOrder.backendId],
                }
                var pos_order = await self.rpc(params, {async: false}).then(function(report_html){
                    return report_html
                });
                var lines = []
                for (let line of pos_order[0].lines) {
                    line[2]['return_qty'] = 0
                    lines.push(line[2]);
                }
                pos_order[0].lines = lines
                this.orderManagementContext.selectedOrder = pos_order[0];
            } else {
                this._setOrder(clickedOrder);
            }
        }
        _setOrder(order) {
            this.env.pos.set_order(order);
            if (order === this.env.pos.get_order()) {
                this.close();
            }
            // var posOrder = new models.Order({}, { pos: this.env.pos, json: order });
            // this.env.pos.set_order(posOrder);
        }
        orderIsEmpty(order) {
            var self = this;
            var currentOrderLines = order.get_orderlines();
            var lines_ids = []
            if(!order.is_empty()) {
                _.each(currentOrderLines,function(item) {
                    lines_ids.push(item.id);
                });
                _.each(lines_ids,function(id) {
                    order.remove_orderline(order.get_orderline(id));
                });
            }
        }
        ProcessReturnOrder() {
            var self = this
            this.state.orderlines = this.orderManagementContext.selectedOrder.lines
            this.state.orders = this.orderManagementContext.selectedOrder
            if (this.state.orderlines && this.state.orderlines.length > 0){
                var order = self.env.pos.get_order()
                var lines = order.get_orderlines();
                if(lines.length > 0){
                    self.orderIsEmpty(order);
                }
                var partner_id = this.env.pos.db.get_partner_by_id(this.state.orders.partner_id)
                this.env.pos.get_order().set_client(partner_id);
                _.each(this.state.orderlines, function (lines) {
                    if (lines.return_qty > 0){
                        var product_id = self.env.pos.db.get_product_by_id(lines.product_id)
                        var quantity = 0
                        if (lines.return_qty > lines.order_return_qty){
                            quantity = -lines.order_return_qty
                        }else{
                            quantity = -lines.return_qty
                        }
                        

                        var price_unit = lines.price_unit
                        if (lines.discount > 0){
                            price_unit = lines.price_unit - (lines.price_unit * (lines.discount / 100))
                        }
                        var uom_id = lines.uom_id[0]
                        if (quantity > 0){
                            if (lines.pack_lot_ids.length > 0){
                                const isAllowOnlyOneLot = product_id.isAllowOnlyOneLot();
                                if (lines.pack_lot_ids.length > 0 && !isAllowOnlyOneLot){
                                    self.state.SelectedLotSerialList = lines.select_operation_lot_name
                                }else{
                                    self.state.SelectedLotSerialList = lines.operation_lot_name
                                }
                                let draftPackLotLines
                                const modifiedPackLotLines = {}
                                var newPackLotLines = self.state.SelectedLotSerialList
                                draftPackLotLines = { modifiedPackLotLines, newPackLotLines };
                                draftPackLotLines
                                self.env.pos.get_order().add_product(product_id, {
                                    draftPackLotLines,
                                    quantity: quantity, 
                                    price: price_unit,
                                });
                                let orderLine = self.env.pos.get_order().get_selected_orderline();
                                orderLine.set_quantity(quantity);
                                orderLine.set_custom_uom_id(uom_id);
                            }else{
                                self.state.SelectedLotSerialList = lines.operation_lot_name
                            }
                            let draftPackLotLines
                            const modifiedPackLotLines = {}
                            var newPackLotLines = self.state.SelectedLotSerialList 
                            draftPackLotLines = { modifiedPackLotLines, newPackLotLines };
                            draftPackLotLines
                            self.env.pos.get_order().add_product(product_id, {
                                draftPackLotLines,
                                quantity: quantity, 
                                price: price_unit,
                            });
                            let orderLine = self.env.pos.get_order().get_selected_orderline();
                            orderLine.set_quantity(quantity);
                            orderLine.set_custom_uom_id(uom_id);
                        }else{
                            self.env.pos.get_order().add_product(product_id, {
                                quantity: quantity, 
                                price: price_unit,
                            });
                            self.env.pos.get_order().get_selected_orderline().set_custom_uom_id(uom_id);
                        }
                    }
                });
                this.env.pos.get_order().set_refund_ref_order(this.state.orders)
                if (this.env.pos.get_order().get_orderlines() && this.env.pos.get_order().get_orderlines().length > 0){
                    this.env.pos.get_order().set_refund_order(true)
                }
                this.showScreen('ProductScreen', {'refund_order': true, 'refund_ref_order': this.state.orders});
            }
        }
    }
    ReturnOrderScreen.template = 'ReturnOrderScreen';
    ReturnOrderScreen.hideOrderSelector = true;

    Registries.Component.add(ReturnOrderScreen);

    return ReturnOrderScreen;
});
