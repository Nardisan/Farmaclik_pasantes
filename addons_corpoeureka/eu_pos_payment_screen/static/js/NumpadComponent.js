/** @odoo-module **/
odoo.define('eu_pos_payment_screen.NumpadComponent', function(require) {
    'use strict';

    const PaymentScreenStatus = require('point_of_sale.PaymentScreenStatus');
    const Registries = require('point_of_sale.Registries');
    const NumberBuffer = require('point_of_sale.NumberBuffer');

    class NumpadComponent extends PaymentScreenStatus  {
        constructor() {
            super(...arguments);

            this.handleCalc = this.handleCalc.bind(this);
        }

        /**
         * The numpad buttons in order with their symbols
         * @property
         */
        buttons = [7, 8, 9, String.fromCharCode(9003), 6, 5, 4, "=", 2, 1, 3, "C", "-", 0, "."];

        /**
         * Get the change amount in REF currency
         */
        get total_inv() {
            const pos = this.env.pos;
            const total = posmodel.get_order().get_total_with_tax();

            return pos.format_currency_no_symbol(
                +(pos.config.show_currency[1].toUpperCase() === "USD"
                    ? total * pos.config.show_currency_rate_real
                    : total / pos.config.show_currency_rate_real)
            ) + " " + pos.config.show_currency_symbol;
        }

        mounted() {
            const $h1 = this.el.querySelector("h1");

            $h1.addEventListener("calc", this.handleCalc);

            $h1.querySelector("span").innerHTML = [this.totalDueText, this.total_inv].join("<br />");
        }

        handleCalc() {
            const $totals = $(this.el).find("> h1 > span");
            
            const pos = this.env.pos;

            const DUE = pos.get_order().get_due();

            let amount = +(pos.config.show_currency[1].toUpperCase() === "USD" 
                ? DUE * pos.config.show_currency_rate_real 
                : DUE / pos.config.show_currency_rate_real);

            $totals.html([
                pos.format_currency(DUE),
                pos.format_currency_no_symbol(amount) + " " + pos.config.show_currency_symbol
            ].join("<br />"));

            NumberBuffer.reset();
        }

        /**
         * Get the change amount in REF currency
         */
        get hasChange() {
            return Boolean(this.currentOrder.get_change());
        }

        get change() {
            const pos = this.env.pos;

            let base = this.currentOrder.get_change(),
                inv = pos.format_currency_no_symbol(
                +(pos.config.show_currency[1].toUpperCase() === "USD" 
                    ? base / pos.config.show_currency_rate_real
                    : base * pos.config.show_currency_rate_real)
            )  + " " + pos.config.show_currency_symbol;

            base = pos.format_currency(base);

            return { base, inv };
        }

        /**
         * Handler of the numpad. It switch the action based on the target button symbol
         * @param {Event} e 
         */
        handleClick(e) {
            activeInput ||= document.querySelector("#payment-box input[name='amount-payment']");

            const content = e.target.textContent;

            if(content === "." && activeInput.value.includes(content)) return;

            switch(true) {
                case content === "C":
                    activeInput.value = "";
                    break;
                case (/[0-9\.]/.test(content)): 
                    activeInput.value += content;
                    break;
                case (content === "-" && activeInput.value.includes("-")):
                    activeInput.value = activeInput.value.substring(1);
                    break;
                case (content === "="):
                    activeInput.dispatchEvent(
                        new CustomEvent("amount", {
                            detail: {
                                amount: this.currentOrder.get_total_with_tax() + this.currentOrder.get_rounding_applied()
                            }
                        })
                    );
                    break;
                case (content.charCodeAt(0) === 9003):
                    activeInput.value = activeInput.value.substring(0, activeInput.value.length - 1);
                    break;
                default:
                    activeInput.value = "-" + activeInput.value;
                    break;
            }

            // To check the changes out we manually dispatch the input event
            activeInput.dispatchEvent(new Event("input"));

            this.handleCalc();
        }

        willUnmount() {
            this.el.querySelector("h1").addEventListener("calc", this.handleCalc);
        }
    }

    NumpadComponent.template = "NumpadComponent";

    Registries.Component.add(NumpadComponent);

    return NumpadComponent;
});
