odoo.define('eu_pos_payment_screen.InputComponent', function(require) {
    'use strict';

    const Registries = require('point_of_sale.Registries');
    const PaymentScreen = require('point_of_sale.PaymentScreen');

    /**
     * The 'calc' event is used to perform multicurrency calculations
     * @const
     */
    const CALC = new Event("calc");

    class InputComponent extends PaymentScreen {
        constructor() {
            super(...arguments);

            this.handleFocus = this.handleFocus.bind(this);
            this.handleAmount = this.handleAmount.bind(this);
            this.handleReference = this.handleReference.bind(this);
        }

        mounted() {
            if(this.el
                .parentElement
                .querySelectorAll("input[name='amount-payment']").length !== 1
            ) {
                this.$inverse = ((this.props.inverse) 
                    ? this.el.previousElementSibling 
                    : this.el.nextElementSibling
                ).querySelector("input");
            }

            const $small = this.el.querySelector("small"),
                $input = this.el.querySelector("input");

            $small.textContent = ($input.dataset.paymentName === "USD") ? "$" : "Bs.S";
            
            if(this.props.inverse) {
                $small.textContent = ($small.textContent === "$") ? "Bs.S" : "$";
                $input.dataset.paymentName = ($input.dataset.paymentName === "USD") ? "VEF" : "USD";
                $input.readOnly = !this.env.pos.config.edit_ref_input;
		
            }

            if($small.textContent === "$") {
                $small.classList.add("input-dollar");
                $input.classList.add("input-dollar");
            } else {
                $small.classList.add("input-bolivar");
                $input.classList.add("input-bolivar");
            }

            this.currency = $small.textContent;

            $input.addEventListener("focus", this.handleFocus);
            $input.addEventListener("amount", this.handleAmount);
            $input.addEventListener("reference", this.handleReference);

            (this.paymentLine) && this.deletePaymentLine({ detail: this.paymentLine });
        }

        /**
         * Returns the paymentline related to this box
         */
        get paymentLine() {
            return this.paymentLines.find(({ name }) => name === this.props.paymentMethod.name);
        }

        handleAmount({ detail: { amount }, target }) {
            const { pos } = this.env;

            if(pos.config.show_currency[1].toUpperCase() === target.dataset.paymentName) {
                target.value = (target.dataset.paymentName === "USD")
                    ? amount * pos.config.show_currency_rate_real
                    : amount / pos.config.show_currency_rate_real;
            } else {
                target.value = amount;
            }

            target.dispatchEvent(new Event("input"));
        }

        handleReference(e) {
            (this.paymentLine) && (this.paymentLine.transaction_id = e.detail.value);
        }

        /**
         * Performs the multicurrency calculations
         */
         handleKeyUp() {
            document.querySelector("section[name='NumpadComponent'] > h1").dispatchEvent(CALC);
        }

        handleFocus(e) {
            const $target = $(e.currentTarget);
            const pos = this.env.pos;
            const monto_dolares = pos.get_order().get_due();
            const monto_bolivares = +(pos.config.show_currency[1].toUpperCase() === "USD"  ? monto_dolares * pos.config.show_currency_rate_real : monto_dolares / pos.config.show_currency_rate_real);

            if( monto_dolares != 0 ){

                if($target.data("paymentName") === "USD"){

                    $target.val(monto_dolares.toFixed(2));
                   
                    
    
                }
    
                if($target.data("paymentName") === "VEF"){
    
                    $target.val(monto_bolivares.toFixed(2));
                
                
                }
                this.handleInput(e);
                this.handleKeyUp();

            }
           
            this.line = this.paymentLine;
        }

        /**
         * Main handler of the component. It setups the line, the exchange amount process
         * and the UI effects
         * @param {Event} e 
         */
        handleInput(e) {
            const $target = $(e.currentTarget);
            const { paymentMethod } = this.props;
            const { pos } = this.env;
            const val = +$target.val();


            const inverseVal = ($target.data("paymentName") === "USD")
                    ? val / pos.config.show_currency_rate_real
                    : val * pos.config.show_currency_rate_real;

            if(this.$inverse) this.$inverse.value = inverseVal.toFixed(2);

            const $parent = $target.parent().parent();

            $parent.removeClass("empty");
            if(!val) $parent.addClass("empty");

            /**
             * Sets the line's amount and checks if the amount is greater than the total
             * @callback
             */
            const callback = () => {
                this.line.set_amount(
                    +((pos.config.show_currency[1].toUpperCase() !== ($target.data("paymentName")))
                        ? val
                        : inverseVal).toFixed(2)
                );

                (this.line.amount > pos.get_order().get_total_with_tax()) 
                    ? $parent.addClass("more")
                    : $parent.removeClass("more");
            };
       
            if(val && !this.paymentLine) {
                this.addNewPaymentLine({ detail: paymentMethod });
                this.line = this.paymentLine;
                callback();
            } else if(!val && this.paymentLine) {
                this.deletePaymentLine({ detail: this.paymentLine });
                this.line = undefined;
                if($parent.hasClass("mode")) $parent.removeClass("mode");
            } else if(val && this.paymentLine && this.line) {
                callback();
            } else if((val === 0) && ($parent.hasClass("mode"))) {
                $parent.removeClass("mode");
            }

            $target.get(0).dispatchEvent(new CustomEvent("reference", {
                detail: {
                    value: $parent.find("input[name='reference']").get(0).value,
                }
            }));
            
            document.querySelector("#payment-box").dispatchEvent(CALC);

            console.log("VALOR DEL INPUT: ", val);

        }

        willUnmount() {
            const $input = this.el.querySelector("input");
            
            $input.removeEventListener("focus", this.handleFocus);
            $input.removeEventListener("amount", this.handleAmount);
            $input.removeEventListener("reference", this.handleReference);
        }
    }

    InputComponent.template = 'InputComponent';

    Registries.Component.add(InputComponent);

    return InputComponent;
});
