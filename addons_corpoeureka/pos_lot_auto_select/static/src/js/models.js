odoo.define('pos_lot_auto_select.models', function(require){
	// var screens = require('point_of_sale.screens');
	var core = require('web.core');
	// var gui = require('point_of_sale.gui');
	var models = require('point_of_sale.models');
	// var PopupWidget = require('point_of_sale.popups');
	var QWeb = core.qweb;
	const Registries = require('point_of_sale.Registries');
	const ProductScreen = require('point_of_sale.ProductScreen');
	const OrderWidget = require('point_of_sale.OrderWidget');
	const EditListPopup = require('point_of_sale.EditListPopup');

	var utils = require('web.utils');

	var round_di = utils.round_decimals;
	var round_pr = utils.round_precision;
	models.load_fields('product.product', 'use_expiration_date');

	models.load_models([
		{
			model: 'stock.production.lot',
			fields: ['id','name','product_id','product_qty','total_available_qty','product_uom_id','expiration_date'],
			domain: function(self){
				// var current_date = moment(new Date()).locale('en').format("YYYY-MM-DD HH:mm:ss");
				var from_lot_expire_days = moment(new Date()).add(self.config.lot_expire_days,'d').format("YYYY-MM-DD HH:mm:ss");
				if(self.config.allow_pos_lot){
					return [['product_qty','>',0]];
					// return [['expiration_date','>',from_lot_expire_days],['product_qty','>',0]];
					// return [['create_date','>=',from],['total_available_qty','>',0]];
				}
				else{
					return [['id','=',0]];
				}
			},
			loaded: function(self,list_lot_num){
				self.db.list_lot_num = [];
				self.list_lot_num_by_id ={};
				self.list_lot_num_by_product_id ={};
				var from_lot_expire_days = moment(new Date()).add(self.config.lot_expire_days,'d').format("YYYY-MM-DD HH:mm:ss");
				list_lot_num.forEach(function(lot){
					var product = self.db.get_product_by_id(lot.product_id[0]);
					if (product.use_expiration_date) {
						if (lot.expiration_date>from_lot_expire_days) {
							self.db.list_lot_num.push(lot);
						}
					}else {
						self.db.list_lot_num.push(lot);
					}

					if (lot.total_available_qty > 0) {
						self.list_lot_num_by_id[lot.id] = lot;
						if(lot.product_id[0] in self.list_lot_num_by_product_id){
							self.list_lot_num_by_product_id[lot.product_id[0]].push(lot);
						}else {
							self.list_lot_num_by_product_id[lot.product_id[0]]=[lot,];
						}
					}
				});
			},
		},{
				model: 'pos.pack.operation.lot',
				fields: ['id','pos_order_line_id', 'lot_name'],
				loaded: function(self, pack_lot_lines) {
						self.db.pos_pack_lot_by_line_id = {};
						pack_lot_lines.forEach(function(pack_lot){
								if(pack_lot.pos_order_line_id[0] in self.db.pos_pack_lot_by_line_id){
									self.db.pos_pack_lot_by_line_id[pack_lot.pos_order_line_id[0]].push(pack_lot);
								}else {
									self.db.pos_pack_lot_by_line_id[pack_lot.pos_order_line_id[0]]=[pack_lot,];
								}

						});

				},
		},

	 ], {
			'after': 'product.product'
	});

	// models.load_models();

	var PacklotlineCollection2 = Backbone.Collection.extend({
		model: models.Packlotline,
		initialize: function(models, options) {
			this.order_line = options.order_line;
		},

		get_empty_model: function(){
			return this.findWhere({'lot_name': null});
		},

		remove_empty_model: function(){
			this.remove(this.where({'lot_name': null}));
		},

		get_valid_lots: function(){
			return this.filter(function(model){
				return model.get('lot_name');
			});
		},

		set_quantity_by_lot: function() {
			if (this.order_line.product.tracking == 'serial' || this.order_line.product.tracking == 'lot') {
				var valid_lots = this.get_valid_lots();
				this.order_line.set_quantity(valid_lots.length);
			}
		}
	});

	var OrderlineSuper = models.Orderline;
	models.Orderline = models.Orderline.extend({
		export_as_JSON: function() {
			var json = OrderlineSuper.prototype.export_as_JSON.apply(this,arguments);
			json.lot_details = this.get_order_line_lot();
			return json;
		},
		// set_product_lot: function(product){
		//     this.has_product_lot = product.tracking !== 'none' && this.pos.config.use_existing_lots;
		//     this.pack_lot_lines  = this.has_product_lot && new PacklotlineCollection2(null, {'order_line': this});
		// },
		export_for_printing: function(){
			var pack_lot_ids = [];
			if (this.has_product_lot){
				this.pack_lot_lines.each(_.bind( function(item) {
					return pack_lot_ids.push(item.export_as_JSON());
				}, this));
			}
			var data = OrderlineSuper.prototype.export_for_printing.apply(this, arguments);
			data.pack_lot_ids = pack_lot_ids;
			data.lot_details = this.get_order_line_lot();
			return data;
		},

		get_order_line_lot:function(){
			var pack_lot_ids = [];
			if (this.has_product_lot){
				this.pack_lot_lines.each(_.bind( function(item) {
					return pack_lot_ids.push(item.export_as_JSON());
				}, this));
			}
			return pack_lot_ids;
		},
		get_required_number_of_lots: function(){
			var lots_required = 1;

			if (this.product.tracking == 'serial' || this.product.tracking == 'lot') {
				lots_required = this.quantity;
			}
			return lots_required;
		},

		// has_valid_product_lot: function(){
    //     if(!this.has_product_lot){
    //         return true;
    //     }
		// 		if (this.pos.config.allow_pos_lot && this.pos.config.allow_auto_select_lot) {
		// 			let order = this.pos.get_order();
		// 			console.log("this");
		// 			console.log(this);
		// 			// const payload = order._autoSelectLot(this.product,false);
		// 			//
		// 			// console.log(payload);
		// 			// if (payload.length>0) {
		// 			// 	// console.log('confirmed',confirmed);
		// 			// 	// console.log('payload',payload);
		// 			// 	// Segregate the old and new packlot lines
		// 			// 	// const modifiedPackLotLines = Object.fromEntries(
		// 			// 	// 	payload.newArray.filter(item => item.id).map(item => [item.id, item.text])
		// 			// 	// );
		// 			// 	// console.log("modifiedPackLotLines");
		// 			// 	// console.log(modifiedPackLotLines);
		// 			// 	// const newPackLotLines = payload.newArray
		// 			// 	// 	.filter(item => !item.id)
		// 			// 	// 	.map(item => ({ lot_name: item.text  , prod_qty : item.qty}));
		// 			//
		// 			// 	// console.log("newPackLotLines");
		// 			// 	// console.log(payload);
		// 			// 	const newPackLotLines = payload;
		// 			// 	const modifiedPackLotLines = [];
		// 			// 	// options.draftPackLotLines = { modifiedPackLotLines, newPackLotLines };
		// 			// 	this.setPackLotLines({ modifiedPackLotLines, newPackLotLines });
		// 			//
		// 			//
		// 			// 	// draftPackLotLines = { payload };
		// 			// } else {
		// 			// 	// We don't proceed on adding product.
		// 			// 	return;
		// 			// }
		//
		//
		//
		// 		}else if (this.pos.config.allow_pos_lot &&! this.pos.config.allow_auto_select_lot) {
		// 			var valid_product_lot = this.pack_lot_lines.get_valid_lots();
	  //       console.log("valid_product_lot");
	  //       console.log(valid_product_lot);
	  //       return this.get_required_number_of_lots() === valid_product_lot.length;
		// 		}
		//
    // },

		can_be_merged_with: function(orderline){
			// override delete check if product tracking == "lot"
        var price = parseFloat(round_di(this.price || 0, this.pos.dp['Product Price']).toFixed(this.pos.dp['Product Price']));
        var order_line_price = orderline.get_product().get_price(orderline.order.pricelist, this.get_quantity());
        order_line_price = orderline.compute_fixed_price(order_line_price);
        if( this.get_product().id !== orderline.get_product().id){    //only orderline of the same product can be merged
            return false;
        }else if(!this.get_unit() || !this.get_unit().is_pos_groupable){
            return false;
        }else if(this.get_discount() > 0){             // we don't merge discounted orderlines
            return false;
        }else if(!utils.float_is_zero(price - order_line_price - orderline.get_price_extra(),
                    this.pos.currency.decimals)){
            return false;
        }else if (this.description !== orderline.description) {
            return false;
        }else{
            return true;
        }
    },

	});

	var OrderSuper = models.Order;
	models.Order = models.Order.extend({
		add_product: function(product, options){

			if (this.pos.config.allow_pos_lot && this.pos.config.allow_auto_select_lot && ['serial', 'lot'].includes(product.tracking) && (this.pos.picking_type.use_create_lots || this.pos.picking_type.use_existing_lots)) {
				const payload = this._autoSelectLot(product,options);
				if (payload.length>0) {
					// console.log('confirmed',confirmed);
					// console.log('payload',payload);
					// Segregate the old and new packlot lines
					// const modifiedPackLotLines = Object.fromEntries(
					// 	payload.newArray.filter(item => item.id).map(item => [item.id, item.text])
					// );
					// console.log("modifiedPackLotLines");
					// console.log(modifiedPackLotLines);
					// const newPackLotLines = payload.newArray
					// 	.filter(item => !item.id)
					// 	.map(item => ({ lot_name: item.text  , prod_qty : item.qty}));


					const newPackLotLines = payload;
					const modifiedPackLotLines = [];
					options.draftPackLotLines = { modifiedPackLotLines, newPackLotLines };

					// draftPackLotLines = { payload };
				} else {
					// We don't proceed on adding product.
					return;
				}
			}


			OrderSuper.prototype.add_product.call(this,product, options);


    },
		_autoSelectLot(product,options) {
			var self = this;
			let order = this.pos.get_order();
			let orderline = order.selected_orderline;

			// var qty  =  orderline.get_quantity() || 1;
			var qty  =  options.quantity || 1;
			if (orderline && orderline.product.id == product.id) {
				qty = orderline.get_quantity()+1;
			}


			var product_lot = [];
			var lot_list = this.pos.db.list_lot_num;

			if (order.is_return_order) {



				var newPackLotLines = [];
				self.pos.db.pos_pack_lot_by_line_id[options.line.id].forEach(function(pack_lot){
					let obj = { lot_name: pack_lot.lot_name  , prod_qty : -1};
					newPackLotLines.push(obj);
				});


				return newPackLotLines;

			}else {
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
			}

			return [];
		}

	});

});
