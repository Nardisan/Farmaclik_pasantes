/** @odoo-module **/
odoo.define('eu_pos_payment_screen.GiftCardComponent', function(require) {
    'use strict';

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');
    const { _t } = require("web.core");
    const models = require('point_of_sale.models');
    
    models.load_fields('res.partner', ["giftcard_amount"]);

    class GiftCardComponent extends PaymentScreen {
        constructor() {
            super(...arguments);
            this.giftCardMethod = this.env.pos.payment_methods.find(({ jr_use_for }) => jr_use_for === 'gift_card');
        }

        get giftCardPaymentLine() {
            return this.currentOrder
                .get_paymentlines()
                .find(({ payment_method: { jr_use_for } }) => jr_use_for === "gift_card");
        }

        mounted() {
            this.active = false;

            (this.giftCardPaymentLine) && this.deletePaymentLine({ detail: this.giftCardPaymentLine });
        }

        dispatchCalc() {
            document.querySelectorAll("#payment-box, section[name='NumpadComponent'] > h1")
                .forEach(($el) => $el.dispatchEvent(new Event("calc")));
        }

        async useGiftCardForPayment() {
            const { confirmed, payload } = await this.showPopup('giftCardRedeemPopup', {
                title: this.env._t('Gift Card'),
            });

            if(!confirmed) return;
            
            const redeem_amount = payload.card_amount;

            if(redeem_amount <= 0) {
                return this.env.pos.db.notification('danger', _t('Please enter valid amount.'));
            }

            if(payload.redeem?.card_value <= redeem_amount) {
                return this.env.pos.db.notification('danger',_t('Please enter amount below card value.'));
            }

            const CODE = payload.card_no;
            
            const CLIENT = this.currentOrder.get_client();

            this.addNewPaymentLine({ detail: this.giftCardMethod });
            this.giftCardPaymentLine.set_amount(Math.max(redeem_amount), 0);
            this.giftCardPaymentLine.set_giftcard_line_code(CODE);
            this.currentOrder.set_redeem_giftcard({
                'redeem_card_no': payload.redeem.id,
                'redeem_remaining': payload.redeem.card_value - redeem_amount,
                'redeem_card_amount': redeem_amount,
                ...((payload.redeem?.customer_id[0])
                    ? {
                        'redeem_card': CODE,
                        'card_customer_id': CLIENT?.id || false,
                        'customer_name': CLIENT?.name || "",
                    } : {
                        'redeem_card': $('#text_gift_card_no').val(),
                        'card_customer_id': CLIENT?.id || payload.redeem?.customer_id[0],
                        'customer_name': CLIENT?.name || payload.redeem?.customer_id[1],
                    }
                )
            });

            this.el.querySelector("strong").textContent = this.giftCardPaymentLine.amount;
            this.trigger('close-popup');
            this.dispatchCalc();
        }

        handleClick() {
            this.active = !this.active;
            
            if(this.active) {
                if(this.currentOrder.getNetTotalTaxIncluded() <= 0) return;

                this.useGiftCardForPayment();
            } else {
                (this.giftCardPaymentLine) && this.deletePaymentLine({ detail: this.giftCardPaymentLine });
                this.el.querySelector("strong").textContent = "0.00";
                this.dispatchCalc();
            }
            
        }
    };

    GiftCardComponent.template = "GiftCardComponent";

    Registries.Component.add(GiftCardComponent);

    return GiftCardComponent;
});
