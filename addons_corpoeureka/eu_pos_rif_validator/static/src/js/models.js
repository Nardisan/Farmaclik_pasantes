odoo.define('eu_pos_rif_validator.models', function (require) {
"use strict";

const models = require('point_of_sale.models');
const PaymentScreen = require('point_of_sale.PaymentScreen');
const Registries = require('point_of_sale.Registries');
const session = require('web.session');
const core = require('web.core');
const _t = core._t;
const QWeb = core.qweb;

models.load_fields('res.partner',['cedula','rif']);
models.load_fields('account.tax',['aliquot_type']);

var _super = models.Order;
models.Order = models.Order.extend({
    export_for_printing: function(){
        var json = _super.prototype.export_for_printing.apply(this,arguments);
        var client  = this.get('client');

        this.orderlines.each(function(line){
            for(var orderline in json.orderlines){
                if(json.orderlines[orderline].product_name == line.product.display_name){
                    json.orderlines[orderline].barcode = line.product.barcode
                    json.orderlines[orderline].default_code = line.product.default_code
                    json.orderlines[orderline].taxes = line.get_taxes()
                }
            }
            for(var orderline in json.orderlines){
                if(json.orderlines[orderline].product_name == line.product.display_name){
                    json.orderlines[orderline].barcode = line.product.barcode
                    json.orderlines[orderline].default_code = line.product.default_code
                    json.orderlines[orderline].taxes = line.get_taxes()
                }
            }
        });

        if (this.get_client()) {
            json.customerve = {
                client:     client ? client.name : null ,
                vat:        client ? client.vat : null ,
                dni:        client ? client.cedula : null ,
                rif:        client ? client.rif : null ,
                street:     client ? client.street : null ,
                city:       client ? client.city : null ,
                state_id:       client ? client.state_id : null ,
                country_id:     client ? client.country_id : null ,
                phone:      client ? client.phone : null ,
                email:      client ? client.email : null ,
            };
        }
        return json;
    },

});

var _superPaymentline = models.Paymentline.prototype;
models.Paymentline = models.Paymentline.extend({
    export_for_printing: function(){
        var json = _superPaymentline.export_for_printing.apply(this,arguments);
        return json;
    },
});

    /*Validate Required Client*/
    const PosRifValidator = PaymentScreen =>
    class extends PaymentScreen {
        async validateOrder(isForceValidate) {
            var client = this.env.pos.get_order().get_client()
            if (!client) {
                const { confirmed } = await this.showPopup('ConfirmPopup', {
                    title: this.env._t('Por favor, seleccione un cliente'),
                    body: this.env._t(
                        'Necesita selecciona un cliente para poder facturar.'
                    ),
                });
                if (confirmed) {
                    this.selectClient();
                }
                return false;
    
            } else if (!client.vat){
                const { confirmed } = await this.showPopup('ConfirmPopup', {
                    title: this.env._t('Configure su Cliente'),
                    body: this.env._t(
                        'El campo RIF en el cliente es obligatorio.'
                    ),
                });
                if (confirmed) {
                    this.selectClient();
                }
                return false;
            }
            return super.validateOrder(isForceValidate);
        }
    };
Registries.Component.extend(PaymentScreen, PosRifValidator);
return PaymentScreen;
});
