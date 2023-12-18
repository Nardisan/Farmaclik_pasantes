odoo.define('pos_lot_auto_select.EditListPopup', function(require) {
	'use strict';

	const { useState } = owl.hooks;
	const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
	const Registries = require('point_of_sale.Registries');
	const { useAutoFocusToLast } = require('point_of_sale.custom_hooks');
	const { useListener } = require('web.custom_hooks');

	class EditListPopup1 extends AbstractAwaitablePopup {

		constructor() {
			super(...arguments);
			this._id = 0;
			var product_lot = [];
			var lot_list = this.env.pos.db.list_lot_num;
			for(var i=0;i<lot_list.length;i++){
				if(lot_list[i].product_id[0] == this.props.product.id && lot_list[i].total_available_qty > 0){
					// lot_list[i]['temp_qty'] =  lot_list[i].product_qty
					lot_list[i]['temp_qty'] =  lot_list[i].total_available_qty
					product_lot.push(lot_list[i]);
				}
			}
			// console.log(lot_list);
			// console.log(product_lot);
			product_lot.sort((a, b) => (a.expiration_date > b.expiration_date) ? 1 : -1)
			this.state = useState({array: this._initialize(this.props.array), product_lot : product_lot , qstr : '' });
			useAutoFocusToLast();
		}
		_nextId() {
			return this._id++;
		}
		_emptyItem() {
			return {
				text: '',
				qty : 0,
				_id: this._nextId(),
			};
		}
		_initialize(array) {
			if (array.length === 0) return [this._emptyItem()];
			return array.map((item) => Object.assign({}, { _id: this._nextId() }, typeof item === 'object'? item: { 'text': item}));
		}

		search_lot(event){
			this.state.qstr = event.target.value;
			var lot_list = this.env.pos.db.list_lot_num;
			var product_lot = [];
			for(var i=0;i<lot_list.length;i++){
				if(lot_list[i].product_id[0] == this.props.product.id ){
					if(lot_list[i].name.toLowerCase().search(event.target.value.toLowerCase()) > -1){
						product_lot.push(lot_list[i]);
					}
				}
			}
			this.state.product_lot = product_lot;
		}

		addNewLotLine(event){
			let self = this;
			// console.log(event.currentTarget.dataset);
			let lot_name = event.currentTarget.dataset.lot;
			let total_available_qty = parseFloat(event.currentTarget.dataset.total_available_qty);
			let temp_qty = parseFloat(event.currentTarget.dataset.temp_qty);
			let entered_qty = parseFloat(event.currentTarget.parentNode.parentNode.getElementsByClassName('input_qty')[0].value);
			if(total_available_qty >= entered_qty){
				for(var i = 0 ; i < entered_qty ; i++){
					self.state.array.push(
						{text: lot_name,
						qty : 1,
						_id: self._nextId(),
					});

					self.state.product_lot.forEach(function (val) {
						if(val['name'] == lot_name){
							val['temp_qty'] -= 1
						}
					});
				}
			}else{
				alert('Please enter valid quantity');
			}
			self.render();
		}

		removeItem(event) {
			let self = this;
			const itemToRemove = event.detail;
			let lot_name = event.detail.text;
			self.state.product_lot.forEach(function (val) {
				if(val['name'] == lot_name){
					val['temp_qty'] += 1
				}
			});
			this.state.array.splice(
				this.state.array.findIndex(item => item._id == itemToRemove._id),
				1
			);
			if (this.state.array.length === 0) {
				this.state.array.push(this._emptyItem());
			}
			this.render();
		}

		createNewItem() {
			if (this.props.isSingleItem) return;
			this.state.array.push(this._emptyItem());
		}

		getPayload() {
			return {
				newArray: this.state.array
					.filter((item) => item.text.trim() !== '')
					.map((item) => Object.assign({}, item)),
			};
		}
	}
	EditListPopup1.template = 'EditListPopup1';
	EditListPopup1.defaultProps = {
		confirmText: 'Ok',
		cancelText: 'Cancel',
		array: [],
		isSingleItem: false,
	};

	Registries.Component.add(EditListPopup1);

	return EditListPopup1;
});
