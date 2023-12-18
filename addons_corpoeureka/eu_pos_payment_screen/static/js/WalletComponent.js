/** @odoo-module **/
odoo.define('eu_pos_payment_screen.WalletComponent', function(require) {
    'use strict';

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');
    const { useState } = owl.hooks;
    const { _t } = require("web.core");

    class WalletComponent extends PaymentScreen {
        constructor() {
            super(...arguments);
            this.state = useState({ remainingWalletAmount: 0 });
            
            this.rpc({
                model: "res.partner",
                method: "search_read",
                domain: [['id', '=', this.props.client.id]],
                fields:['remaining_wallet_amount']
            })
            .then((results) => results
                .forEach(({ remaining_wallet_amount }) => {
                    this.state.remainingWalletAmount = remaining_wallet_amount;

                    const amounts = [
                        this.showSymbol(this.state.remainingWalletAmount),
                        this.showSymbol(this.state.remainingWalletAmount, true)
                    ];
    
                    this.setText("0.00",  `${amounts[0]} en la billetera, (${amounts[1]})`);
                })
            );

            this.walletMethod = this.env.pos.payment_methods.find(({ jr_use_for }) => jr_use_for === 'wallet');
        }

        async useWalletForPayment()  {
            const { remainingWalletAmount } = this.state;

            let { confirmed, payload: { amount } } = await this.showPopup('WalletPopup', {
                title: this.env._t('Pay with Wallet'),
                confirmText: this.env._t('Use'),
                customer: this.props.client.name,
                defined_amount: this.env.pos.format_currency_no_symbol(
                    (this.currentOrder.get_due() < remainingWalletAmount)
                        ? this.currentOrder.get_due()
                        : remainingWalletAmount
                ),
            });

            if(!confirmed) {
                this.active = false;
                return;
            }

            if(amount === 0) return alert("La billetera está vacía");

            await this.rpc({
                model: "res.partner",
                method: "search_read",
                domain: [['id', '=', this.props.client.id]],
                fields:['remaining_wallet_amount']
            })
            .then((results) => 
                results.forEach((result) => {
                    amount = this.env.pos.db.thousandsDecimalChanger(amount);

                    if(amount > result.remaining_wallet_amount || amount > this.currentOrder.get_due()){
                        return alert('You are not allow to use wallet amount Morethen remaining amount !!!');
                    }

                    this.currentOrder.set_used_amount_from_wallet(Math.abs(amount));
                    this.currentOrder.set_type_for_wallet('change');

                    this.addNewPaymentLine({ detail: this.walletMethod });
                    this.walletLine.set_amount(amount);

                    const amounts = [
                        this.showSymbol(result.remaining_wallet_amount),
                        this.showSymbol(result.remaining_wallet_amount, true),
                        this.showSymbol(result.remaining_wallet_amount - amount),
                        this.showSymbol((result.remaining_wallet_amount - amount), true),
                    ];

                    this.setText(amount, `${amounts[0]} (${amounts[1]}) en la billetera, ${amounts[2]} (${amounts[3]}) después de la transacción`);

                    this.dispatchCalc();
                })
            );
        }

        setText(strong, p) {
            this.el.querySelector("strong").textContent = strong;
            this.el.querySelector("p").textContent = p;

            const $walletBox = this.el.querySelector(".wallet-box");

            $walletBox.classList.remove("disabled");

            if(strong === "0.00") $walletBox.classList.add("disabled");
        }

        mounted() {
            this.active = false;

            (this.walletLine) && this.deletePaymentLine({ detail: this.walletLine });
        }

        get walletLine() {
            return this.currentOrder
                .get_paymentlines()
                .find(({ payment_method: { jr_use_for } }) => jr_use_for === "wallet" ); 
        }

        dispatchCalc() {
            document.querySelectorAll("#payment-box, section[name='NumpadComponent'] > h1")
                .forEach(($el) => $el.dispatchEvent(new Event("calc")));
        }

        get inverse() {
            if(!this.el?.querySelector("strong")) return;

            return this.showSymbol(+(this.el.querySelector("strong").textContent), true);
        }

        get inverseCurrency() {
            return this.env.pos.currency.name === "USD" ? "VEF" : "USD";
        }

        showSymbol(amount, inverse = undefined) {
            return this.env.pos.format_currency_no_symbol(
                (inverse)
                    ? amount / this.env.pos.config.show_currency_rate_real
                    : amount
            ) + ((inverse) ? " Bs.s" : " $");
        }

        handleClick() {
            if(!this.state.remainingWalletAmount) {
                return this.env.pos.db.notification('danger', _t("The wallet of the selected customer is empty"));
            }

            if(!this.props.client) {
                return this.env.pos.db.notification('danger',"Please select customer!");
            }

            this.active = !this.active;

            if(this.active) {
                if(this.currentOrder.getNetTotalTaxIncluded() <= 0) return;

                this.useWalletForPayment();
            } else {
                (this.walletLine) && this.deletePaymentLine({ detail: this.walletLine });

                const amounts = [
                    this.showSymbol(this.state.remainingWalletAmount),
                    this.showSymbol(this.state.remainingWalletAmount, true)
                ];

                this.setText("0.00",  `${amounts[0]} en la billetera, (${amounts[1]})`);
                this.dispatchCalc();
            }
        }
    };

    WalletComponent.template = "WalletComponent";

    Registries.Component.add(WalletComponent);

    return WalletComponent;
});
