odoo.define('pos_lot_auto_select.ProductScreen', function(require){
	var core = require('web.core');
	var models = require('point_of_sale.models');
	var QWeb = core.qweb;
	const Registries = require('point_of_sale.Registries');
	const ProductScreen = require('point_of_sale.ProductScreen');
	const NumberBuffer = require('point_of_sale.NumberBuffer');

	const ProductScreenExtend = (ProductScreen) =>
		class extends ProductScreen {
			constructor() {
				super(...arguments);
			}

			async selectLot(product) {
				//debugger;

				if (!this.currentOrder) {
					this.env.pos.add_new_order();
				}
				let price_extra = 0.0;
				let draftPackLotLines, weight, description, packLotLinesToEdit;

				if (this.env.pos.config.product_configurator && _.some(product.attribute_line_ids, (id) => id in this.env.pos.attributes_by_ptal_id)) {
					let attributes = _.map(product.attribute_line_ids, (id) => this.env.pos.attributes_by_ptal_id[id])
									  .filter((attr) => attr !== undefined);
					let { confirmed, payload } = await this.showPopup('ProductConfiguratorPopup', {
						product: product,
						attributes: attributes,
					});

					if (confirmed) {
						description = payload.selected_attributes.join(', ');
						price_extra += payload.price_extra;
					} else {
						return;
					}
				}

				// Gather lot information if required.
				if (this.env.pos.config.allow_pos_lot && !this.env.pos.config.allow_auto_select_lot && ['serial', 'lot'].includes(product.tracking) && (this.env.pos.picking_type.use_create_lots || this.env.pos.picking_type.use_existing_lots)) {
					const isAllowOnlyOneLot = product.isAllowOnlyOneLot();
					if (isAllowOnlyOneLot) {
						packLotLinesToEdit = [];
					} else {
						const orderline = this.currentOrder
							.get_orderlines()
							.filter(line => !line.get_discount())
							.find(line => line.product.id === product.id);
						if (orderline) {
							packLotLinesToEdit = orderline.getPackLotLinesToEdit();
						} else {
							packLotLinesToEdit = [];
						}
					}
					const { confirmed, payload } = await this.showPopup('EditListPopup1', {
						title: this.env._t('Manual Lot/Serial Number Selection'),
						isSingleItem: isAllowOnlyOneLot,
						array: packLotLinesToEdit,
						product : product
					});
					if (confirmed) {
						// Segregate the old and new packlot lines
						const modifiedPackLotLines = Object.fromEntries(
							payload.newArray.filter(item => item.id).map(item => [item.id, item.text])
						);
						const newPackLotLines = payload.newArray
							.filter(item => !item.id)
							.map(item => ({ lot_name: item.text  , prod_qty : item.qty}));
						draftPackLotLines = { modifiedPackLotLines, newPackLotLines };
					} else {
						// We don't proceed on adding product.
						return;
					}
				}

				// Take the weight if necessary.
				if (product.to_weight && this.env.pos.config.iface_electronic_scale) {
					// Show the ScaleScreen to weigh the product.
					if (this.isScaleAvailable) {
						const { confirmed, payload } = await this.showTempScreen('ScaleScreen', {
							product,
						});
						if (confirmed) {
							weight = payload.weight;
						} else {
							// do not add the product;
							return;
						}
					} else {
						await this._onScaleNotAvailable();
					}
				}

				// Add the product after having the extra information.
				this.currentOrder.add_product(product, {
					draftPackLotLines,
					description: description,
					price_extra: price_extra,
					quantity: weight,
				});

				NumberBuffer.reset();
			}

			
			_getAddProductOptions(product) {
				return this.selectLot(product);
			}

			_clickProduct({ detail }) {
				if (!this.currentOrder) {
					this.env.pos.add_new_order();
				}
				
				return this.selectLot(detail);				
			}

			async _onClickPay() {
				var self = this;
				let order = this.env.pos.get_order();
				let has_valid_product_lot = _.every(order.orderlines.models, function(line){
					return line.has_valid_product_lot();
				});
				let check = true;
				if(!has_valid_product_lot){
					check = false;
					self.showPopup('ErrorPopup', {
						title: self.env._t('Empty Serial/Lot Number'),
						body: self.env._t("One or more product(s) required serial/lot number."),
					});
				}
				if(check){
					super._onClickPay();
				}
			}
		};

	Registries.Component.extend(ProductScreen, ProductScreenExtend);

	return ProductScreen;
});
