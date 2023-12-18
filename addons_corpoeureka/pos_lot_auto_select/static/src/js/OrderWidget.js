odoo.define('pos_lot_auto_select.OrderWidget', function(require){
	var core = require('web.core');
	var models = require('point_of_sale.models');
	var QWeb = core.qweb;
	const Registries = require('point_of_sale.Registries');
	const ProductScreen = require('point_of_sale.ProductScreen');
	const OrderWidget = require('point_of_sale.OrderWidget');
	const EditListPopup = require('point_of_sale.EditListPopup');

	const OrderWidgetExtend = (OrderWidget) =>
		class extends OrderWidget {
			constructor() {
				super(...arguments);
			}
			async _editPackLotLines(event) {

				const orderline = event.detail.orderline;

				if (this.env.pos.config.allow_pos_lot && this.env.pos.config.allow_auto_select_lot) {
					const payload = this._autoSelectLot(orderline.product);
					if (payload.length>0) {

						const newPackLotLines = payload;
						const modifiedPackLotLines = [];
						orderline.setPackLotLines({ modifiedPackLotLines, newPackLotLines });

					}

				}else{

					const isAllowOnlyOneLot = orderline.product.isAllowOnlyOneLot();
					const packLotLinesToEdit = orderline.getPackLotLinesToEdit(isAllowOnlyOneLot);

					const { confirmed, payload } = await this.showPopup('EditListPopup1', {
						title: this.env._t('Manual Lot/Serial Number Selection'),
						isSingleItem: isAllowOnlyOneLot,
						array: packLotLinesToEdit,
						product: orderline.product
					});
					if (confirmed) {
						// Segregate the old and new packlot lines
						const modifiedPackLotLines = Object.fromEntries(
							payload.newArray.filter(item => item.id).map(item => [item.id, item.text])
						);
						const newPackLotLines = payload.newArray
							.filter(item => !item.id)
							.map(item => ({ lot_name: item.text , prod_qty : item.qty}));
						orderline.setPackLotLines({ modifiedPackLotLines, newPackLotLines });
					}
				}
				this.order.select_orderline(event.detail.orderline);
			}


			 _autoSelectLot(product) {
	 			var self = this;
	 			let order = this.env.pos.get_order();
	 			let orderline = order.selected_orderline;

	 			// var qty  =  orderline.get_quantity() || 1;
	 			var qty  =  1;
	 			if (orderline && orderline.product.id == product.id) {
	 				qty = orderline.get_quantity();
	 			}


	 			var product_lot = [];
	 			var lot_list = this.env.pos.db.list_lot_num;


 				for(var i=0;i<lot_list.length;i++){
 					if(lot_list[i].product_id[0] == product.id && lot_list[i].total_available_qty > 0){
 						// lot_list[i]['temp_qty'] =  lot_list[i].product_qty
 						lot_list[i]['temp_qty'] =  lot_list[i].total_available_qty
 						product_lot.push(lot_list[i]);
 					}
 				}
 				product_lot.sort((a, b) => (a.expiration_date > b.expiration_date) ? 1 : -1);

 				let selected_lots = [];
 				if (product_lot.length>0) {
 					// console.log("skald",product_lot[0]);
 					// product_lot[0]['temp_qty']-=1;
 					var qty_temp = qty;
 					var i =0;


 					while (qty_temp>0  ) {
 						if (product_lot.length<= i) {
 							alert("Not enough Lot");
 							break;
 						}
 						let obj = {};

 						if(product_lot[i]['temp_qty'] >= qty_temp){
 							// lot_list[i]['temp_qty'] =  lot_list[i].product_qty
 							// obj[product_lot[i].id] = qty_temp;
 							obj = {id: product_lot[i].id ,name:product_lot[i].name ,qty : qty_temp}
 							qty_temp =0;
 						}else if (product_lot[i]['temp_qty']<qty_temp) {
 							obj = {id: product_lot[i].id ,name:product_lot[i].name ,qty : product_lot[i]['temp_qty']}
 							qty_temp -=product_lot[i]['temp_qty'];
 							// obj[product_lot[i].id] = product_lot[i]['temp_qty'];
 						}
 						i+=1;
 						selected_lots.push(obj);
 					}

 					for (var j = 0; j < selected_lots.length; j++) {
 						for(var i=0;i<lot_list.length;i++){
 							if(lot_list[i].id == selected_lots[j].id ){
 								// lot_list[i]['temp_qty'] =  lot_list[i].product_qty
 								lot_list[i]['temp_qty'] -=selected_lots[j].qty
 							}
 						}
 					}

 					var newPackLotLines = [];
 					for (var j = 0; j < selected_lots.length; j++) {
 						for (var i = 0; i < selected_lots[j].qty; i++) {

 							let obj = { lot_name: selected_lots[j].name  , prod_qty : 1};
 							newPackLotLines.push(obj);
 						}
 					}

 					return newPackLotLines;
 				}
 				else {
 					alert("Not enough qty");
 				}


	 			return [];
	 		}
		};
	Registries.Component.extend(OrderWidget, OrderWidgetExtend);

	return OrderWidget;
});
