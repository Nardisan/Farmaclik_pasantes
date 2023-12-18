/** @odoo-module **/
odoo.define('eu_pos_payment_screen.ButtonsComponent', function(require) {
    'use strict';

    const Registries = require('point_of_sale.Registries');
    const PaymentScreen = require('point_of_sale.PaymentScreen');

    class ButtonsComponent extends PaymentScreen {
        constructor() {
            super(...arguments);

            this.handleResize = this.handleResize.bind(this);
        }

        get isTouchScreen() {
            return ("ontouchstart" in window) || (navigator.maxTouchPoints > 0);
        }

        mounted() {
            this.handleResize();
            window.addEventListener("resize", this.handleResize);
        }

        /**
         * Toggles the accesskeys of the buttons elements inside the component 
         * by a CSS media query
         */
        handleResize() {
            if(!this.el) return;

            this.match = window.matchMedia(this.props.media).matches;
        
            const $el = $(this.el);

            const [$inv, $cus] = [...this.el.querySelectorAll("button")];

            if(this.match) {
                $el.show();
                [$inv.accessKey, $cus.accessKey] = ["i", "c"];
            } else {
                $el.hide();
                $inv.accessKey = $cus.accessKey = "";
            } 
        }

        willUnmount() {
            window.removeEventListener("resize", this.handleResize);
        }
    };

    ButtonsComponent.template = "ButtonsComponent";

    Registries.Component.add(ButtonsComponent);

    return ButtonsComponent;
});
