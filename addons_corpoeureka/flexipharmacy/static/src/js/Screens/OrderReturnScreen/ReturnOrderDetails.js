odoo.define('flexipharmacy.ReturnOrderDetails', function (require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const { useState } = owl.hooks;
    const { useListener } = require('web.custom_hooks');
    
    /**
     * @props {models.Order} order
     */
    class ReturnOrderDetails extends PosComponent {
        constructor() {
            super(...arguments);
            this.state = useState({orders:[], orderlines:[], ReturnAllProduct: false, SelectedLotSerialList: []})
        }
        get order() {
            return this.props.order;
        }
        get orderlines() {
            var lines = []
            return this.order ? this.order.lines : [];
        }
        get total() {
            return this.env.pos.format_currency(this.order ? this.order.get_total_with_tax() : 0);
        }
        get tax() {
            return this.env.pos.format_currency(this.order ? this.order.get_total_tax() : 0)
        }
        ReturnAllProductQty() {
            if (this.state.ReturnAllProduct){
                for (let lines of this.order.lines) {
                    var product_id = this.env.pos.db.get_product_by_id(lines.product_id)
                    const isAllowOnlyOneLot = product_id.isAllowOnlyOneLot();
                    if (lines.pack_lot_ids.length > 0 && !isAllowOnlyOneLot){
                        lines['select_operation_lot_name'] = []
                        lines.return_qty = 0
                    }else if (lines.pack_lot_ids.length > 0 && isAllowOnlyOneLot){
                        this.state.SelectedLotSerialList = []
                        lines['select_operation_lot_name'] = []
                        lines.return_qty = 0
                    }else{
                        lines.return_qty = 0
                    }
                }
            }else{
                for (let lines of this.order.lines) {
                    var product_id = this.env.pos.db.get_product_by_id(lines.product_id)
                    const isAllowOnlyOneLot = product_id.isAllowOnlyOneLot();
                    if (lines.pack_lot_ids.length > 0 && !isAllowOnlyOneLot){
                        lines['select_operation_lot_name'] = lines.operation_lot_name
                        lines.return_qty = lines.operation_lot_name.length
                    }else if (lines.pack_lot_ids.length > 0 && isAllowOnlyOneLot){
                        this.state.SelectedLotSerialList = lines.operation_lot_name
                        lines['select_operation_lot_name'] = lines.operation_lot_name
                        lines.return_qty = lines.order_return_qty
                    }else{
                        lines.return_qty = lines.order_return_qty
                    }
                }
            }
        }
    }
    ReturnOrderDetails.template = 'ReturnOrderDetails';

    Registries.Component.add(ReturnOrderDetails);

    return ReturnOrderDetails;
});
