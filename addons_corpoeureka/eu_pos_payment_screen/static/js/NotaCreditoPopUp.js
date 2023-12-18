/** @odoo-module **/
odoo.define('eu_pos_payment_screen.NotaCreditoPopUp', function(require) {
    'use strict';

    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const { useState } = owl.hooks;
    

    class NotaCreditoPopUp extends AbstractAwaitablePopup {

        fields = useState({
            fecha: "",
            nro_factura: "",
            maquina: this.env.pos.config.maquina,
        });

        onSubmit(e) {
            e.preventDefault();
            e.stopPropagation();
            return super.confirm();
        }

        getPayload() {
            const { fields } = this;
            const { fecha } = fields;

            return {
                nro_factura: fields.nro_factura,
                maquina: fields.maquina,
                fecha: moment(fecha).format("DDMMYY"),
                hora: moment(fecha).format("HHmm"),
            };
        }
    }
    NotaCreditoPopUp.template = 'NotaCreditoPopUp';
    NotaCreditoPopUp.defaultProps = {
        confirmText: 'Ok',
        cancelText: 'Cancel',
        title: 'Shortcuts',
    };

    Registries.Component.add(NotaCreditoPopUp);

    return NotaCreditoPopUp;
});