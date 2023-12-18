odoo.define('flexipharmacy.WarehouseScreen', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');
    var rpc = require('web.rpc');
    const { isRpcError } = require('point_of_sale.utils');
    const { useState } = owl.hooks;

    class WarehouseScreen extends PosComponent {
        // async connectionCheck(){
        //     var self = this;
        //     try {
        //         await rpc.query({
        //             model: 'pos.session',
        //             method: 'connection_check',
        //             args: [this.env.pos.pos_session.id],
        //         });
        //         self.state.is_connected = true
        //         self.env.pos.get_order().set_connected(true)
        //     } catch (error) {
        //         if (isRpcError(error) && error.message.code < 0) {
        //             self.env.pos.get_order().set_connected(false)
        //             self.state.is_connected = false
        //             this.showPopup('ErrorPopup', {
        //                 title: this.env._t('Network Error'),
        //                 body: this.env._t('Cannot access order management screen if offline.'),
        //             });
        //         } else {
        //             throw error;
        //         }
        //     }            
        // }
        async CreateInternalTransfer(event){
            var self = this
            // await this.connectionCheck()
            if (this.env.pos.get_order().get_connected()){
                var selectedOrder = this.env.pos.get_order();
                var currentOrderLines = selectedOrder.get_orderlines();
                // var currentOrderLines = [selectedOrder.get_selected_orderline()];
                let flag;
                _.each(currentOrderLines,function(item) {
                    if(item.product.type === "product"){
                        flag = true;
                        return;
                    }
                });
                if(!flag){
                    alert("No Storable Product Found!");
                    return;
                }
                const { confirmed, payload: popup_data} = await this.showPopup('internalTransferPopup',
                        {
                            title: this.env._t('Internal Transfer'),
                            defaultSource: event.id
                        });
                if (confirmed){
                    var moveLines = [];
                    _.each(currentOrderLines,function(item) {
                        if(item.product.type === "product"){
                            let product_name = item.product.default_code ?
                                        "["+ item.product.default_code +"]"+ item.product.display_name :
                                        item.product.display_name;

                            moveLines.push({
                                'product_id': item.product.id,
                                'name': product_name,
                                'product_uom_qty': item.quantity,
                                'location_id': Number(popup_data.SourceLocation),
                                'location_dest_id': Number(popup_data.DestLocation),
                                'product_uom': item.product.uom_id[0],
                            });
                        }
                    });

                    var move_vals = {
                        'picking_type_id': Number(popup_data.PickingType),
                        'location_src_id':  Number(popup_data.SourceLocation),
                        'location_dest_id': Number(popup_data.DestLocation),
                        'state': popup_data.stateOfPicking,
                        'moveLines': moveLines,
                    }
                    await rpc.query({
                        model: 'stock.picking',
                        method: 'internal_transfer',
                        args: [move_vals],
                    }).then(function (result) {
                        if(result && result[0] && result[0]){
                            var url = window.location.origin + '/web#id=' + result[0] + '&view_type=form&model=stock.picking';
                            const { confirmed, payload} = self.showPopup('PurchaseOrderCreate', {
                                title: self.env._t('Confirmation'),
                                SelectedProductList:[],
                                defination: 'Internal Transfer Created',
                                CreatedPurchaseOrder:'True',
                                CreatedInternalTransfer:'True',
                                order_name:result[1],
                                order_id:result[0],
                                url:url,
                            });
                            self.selectedProductList = [];
                        }
                    });
                }
            }
        }
    }

    WarehouseScreen.template = 'WarehouseScreen';

    Registries.Component.add(WarehouseScreen);

    return WarehouseScreen;
});
