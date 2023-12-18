/** @odoo-module **/
odoo.define('eu_pos_payment_screen.HeaderComponent', function(require) {
    'use strict';

    const Registries = require('point_of_sale.Registries');
    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const PaymentScreenStatus = require('point_of_sale.PaymentScreenStatus');
    const NumberBuffer = require('point_of_sale.NumberBuffer');

    let timeout;
    
    class HeaderComponent extends PaymentScreen {
        mounted() {
            window.addEventListener("keyup", this.handleKeyUp);
        }

        handleKeyUp() {
            NumberBuffer.reset();
            window.clearTimeout(timeout);
            timeout = window.setTimeout(() => NumberBuffer.reset(), 500);
        }

        willUnmount() {
            window.removeEventListener("keyup", this.handleKeyUp);
        }

        get walletLine() {
            return this.currentOrder
                .get_paymentlines()
                .find(({ payment_method: { jr_use_for } }) => jr_use_for === "wallet");
        }

        get giftCardPaymentLine() {
            return this.currentOrder
                .get_paymentlines()
                .find(({ payment_method: { jr_use_for } }) => jr_use_for === "gift_card");
        }

        async validate() {
            [this.walletLine, this.giftCardPaymentLine]
                .forEach((pm) => (pm && (this.currentOrder.get_due() < 0)) && this.deletePaymentLine({ detail: pm }));

            if(this.currentOrder.get_change() && this.env.pos.config.enable_wallet && this.currentOrder.get_client() && (this.currentOrder.get_type_for_wallet() !=='change')){
                await this.showPopup('PaymentWalletPopup', {
                    title: this.env._t('Add to Wallet'),
                    change: this.env.pos.format_currency(this.currentOrder.get_change()),
                    nextScreen: this.nextScreen,
                    order: this,
                });
            }

            return super.validateOrder(false);
        }
    }

    class DueComponent extends PaymentScreenStatus {
        constructor() {
            super(...arguments);

            this.handleKeyDown = this.handleKeyDown.bind(this);
        }

        /**
         * Get the total amount in REF currency
         */
        get total_inv() {
            const { pos } = this.env;
            const total = pos.get_order().get_total_with_tax();

            return pos.format_currency_no_symbol(
                +(pos.config.show_currency[1].toUpperCase() === "USD"
                    ? total * pos.config.show_currency_rate_real
                    : total / pos.config.show_currency_rate_real)
            ) + " " + pos.config.show_currency_symbol;
        }

        setText() {
            $(this.el).find("h1").text(
                (this.env.pos.currency.name === this.mode) ? this.totalDueText : this.total_inv
            );
        }
        
        mounted() {
            // Add the header-related keyboard shortcuts
            document.addEventListener("keydown", this.handleKeyDown);

            this.mode = this.env.pos.currency.name;
            this.setText();
        }

        handleKeyDown(e) {
            if(e.ctrlKey && e.altKey) {
                switch(e.key) {
                    case "p":
                        this.handleClick();
                        break;
                    case "}":
                        document.querySelector("button.validate").click();
                        break;
                    case "{":
                        document.querySelector("button.back").click();
                        break;
                    case "+":
                    case "-":
                        if(activeInput) {
                            activeInput.dispatchEvent(
                                new CustomEvent("amount", {
                                    detail: {
                                        amount: (e.key === "+")
                                            ? this.currentOrder.get_total_with_tax() + this.currentOrder.get_rounding_applied()
                                            : this.currentOrder.get_due()
                                    }
                                })
                            );
                        }
                        break;
                    case "Backspace":
                        $("input[name='amount-payment']").val("0.00");
                        break; 
                }
            }
        }

        /**
         * Changes the view mode
         */
        handleClick() {
            this.mode = (this.mode === "VEF") ? "USD": "VEF";

            this.setText();
        }

        willUnmount() {
            document.removeEventListener("keydown", this.handleKeyDown);
        }
    };

    HeaderComponent.template = "HeaderComponent";
    DueComponent.template = "DueComponent";

    Registries.Component.add(HeaderComponent);
    Registries.Component.add(DueComponent);

    return [
        HeaderComponent,
        DueComponent,
    ];
});
