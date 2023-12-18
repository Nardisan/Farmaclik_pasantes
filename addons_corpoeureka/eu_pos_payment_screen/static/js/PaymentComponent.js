/** @odoo-module **/
odoo.define('eu_pos_payment_screen.PaymentComponent', function(require) {
    'use strict';

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');
    const models = require('point_of_sale.models');
    const NumberBuffer = require('point_of_sale.NumberBuffer');
    
    models.load_fields(
        'pos.payment.method',
        ["manual_currency_exchange_rate", "currency_id", "has_reference"]
    );

    /**
     * For touchscreen devices, it is user-friendly to have a way to handle
     * with autofocus
     */
    Object.defineProperty(window, "activeInput", { 
        set($el) {
            this._activeInput = $el;
            $el.focus();
        },
        get() {
            return this._activeInput;
        }
    });

    class PaymentComponent extends PaymentScreen  {
        constructor() {
            super(...arguments);

            this.handleCalc = this.handleCalc.bind(this);
        }

        get normalMethods() {
            return this.env
                .pos
                .payment_methods
                .filter(({ jr_use_for }) => !(['wallet', 'gift_card'].includes(jr_use_for)))
                .sort((a, b) => b.length - a.length);
        }

        mounted() {
            this.el.addEventListener("calc", this.handleCalc);

            // Assign to all inputs an access key from 1 to 9
            $(this.el).find("input[name='amount-payment']:not(:read-only)")
                .on("focusin", (e) => activeInput = e.target)
                .each(function(i) { this.accessKey = i + 1; });
        }

        /**
         * Displays the current advance in both currencies
         */
        handleCalc() {
            let { usd, bs } = [...this.el.querySelectorAll(".flex-form")]
                .reduce((prev, $box) => {
                    const key = $box.querySelector("small").textContent === "$" ? "usd" : "bs";

                    prev[key] += +($box.querySelector("input").value);

                    return prev;
                }, { usd: 0, bs: 0});

            const getAmount = ($el) => {                
                const amount = +$el.querySelector("strong").textContent;
                
                ($el.querySelector("small").textContent === "$")
                    ? (usd += amount)
                    : (bs += amount)
            };

            [...document.querySelectorAll(".wallet-box, #giftcard-button")]
                .filter(Boolean)
                .forEach(getAmount);

            [usd, bs] = [usd, bs].map((n) => this.env.pos.format_currency_no_symbol(n));

            $("#total > span").html([usd + " $", bs + " Bs.S"].join("<br />"));

            NumberBuffer.reset();
        }

        willUnmount() {
            this.el.removeEventListener("calc", this.handleCalc);
            $(this.el).find("input[name='amount-payment']:not(:read-only)").off("focusin");
        }
    }

    class PaymentBox extends PaymentScreen  {
        mounted() {
            this.el.classList.add("empty");
        }

        handleKeyUp(e) {
            e.target
                .parentElement
                .nextElementSibling
                .querySelector("input")
                .dispatchEvent(
                    new CustomEvent("reference", { detail: { value: e.target.value } })
                );
        }
    }

    PaymentComponent.template = "PaymentComponent";

    PaymentBox.template = "PaymentBox";

    Registries.Component.add(PaymentComponent);
    Registries.Component.add(PaymentBox);

    return [
        PaymentComponent,
        PaymentBox,
    ];
});
