odoo.define('eu_tab_payment.payment_form', function (require) {
    "use strict";
    
    const publicWidget = require('web.public.widget');
    const PaymentForm = require("payment.payment_form");
    const { _t } = require('web.core');
    
    const format = (num) => +(num.toFixed(2));
    const getRef = ($i) => $i.parentElement.parentElement.querySelector("input:last-child");
    const TOTAL = () => Number(Number($("input[name='amount_total']").val()).toFixed(2));

    PaymentForm.include({
        async onSubmit(e) {
            e.preventDefault();
            e.stopPropagation();

            if(!confirm(_t("Está a punto de realizar una transacción que no se puede deshacer, desea proseguir?"))) return;

            let to_wallet = false;

            const CURRENCY = e.target.elements.company_currency.value;
            const WALLET = +$("input[name='client_wallet']").val();

            const walletAmount = +$(`input[data-provider='wallet'][data-currency='${CURRENCY}']`).val();

            if(walletAmount > WALLET || walletAmount < 0)
                return this.do_warn(false, _t('Monto de billetera inválido'));

            const paymentIds = [...$(".current-form input[type='number']")]
                .filter(({ value, dataset }) => +(value) && (dataset.currency === CURRENCY))
                .map(($input) => {
                    const $ref = getRef($input);

                    return {
                        id: $input.dataset.paymentId,
                        provider: $input.dataset.provider,
                        value: +$input.value,
                        hasRef: !!$ref,
                        ...($ref && { reference: $ref.value }),
                        ...(($input.dataset.provider === 'wallet') && { walletAmount })
                    };
                });

            const amountTotal = paymentIds.map(({ value }) => value).reduce((p, n) => p + n,0);

            let hasChange = false;

            if(amountTotal > Number((TOTAL() + 0.16).toFixed(2))) {
                if(await this._rpc({ route: "/cart/check-membership-product" })) {
                    return this.do_warn(false, _t('No puedes pagar de más al comprar una membresía'));
                }

                if(paymentIds[0].provider === "wallet") {
                    return this.do_warn(false, _t('No puedes pagar demás usando sólamente la billetera como método de pago'));
                }

                hasChange = true;
                to_wallet = confirm(_t(
`La transacción ha dejado cambio, por defecto el cambio no se guarda en su billetere, confirme
si desea guardar su cambio en la billetera`
                ));
            }
            
            const callback = (result) => {
                if (result) {
                    // if the server sent us the html form, we create a form element
                    var newForm = document.createElement('form');
                    newForm.method = this._get_redirect_form_method();
                    newForm.setAttribute("provider", paymentIds[0].provider);
                    newForm.hidden = true; // hide it
                    newForm.innerHTML = result; // put the html sent by the server inside the form
                    var action_url = $(newForm).find('input[name="data_set"]').data('actionUrl') || '/payment/transfer/feedback';
                    newForm.setAttribute("action", action_url); // set the action url
                    $(document.getElementsByTagName('body')[0]).append(newForm); // append the form to the body
                    $(newForm).find('input[data-remove-me]').remove(); // remove all the input that should be removed

                    if(action_url) {
                        newForm.submit(); // and finally submit the form
                        return new Promise(function () {});
                    }
                }
                else {
                    this.displayError(
                        _t('Server Error'),
                        _t("We are not able to redirect you to the payment form.")
                    );
                }
            };

            return this._rpc({
                route: "/shop/partial/payment/",
                params: {
                    payments: paymentIds,
                    wallet: WALLET,
                    to_wallet
                },
            })
            .then(callback)
            .guardedCatch((error) => {
                console.dir(error);
                error.event.preventDefault();
                this.displayError(
                    _t('Server Error'),
                    _t("We are not able to redirect you to the payment form.") + "\n" +
                        this._parseError(error)
                );
            });
        },
    });

    publicWidget.registry.TabPaymentForm = PaymentForm.extend({
        events: {
            'click .tab': 'changePaymentType',
            'click .current-form nav > button': 'changePaymentAccount',
            'input input[type="number"]': 'handleInput',
        },
        handleUpdate() {
            this.total = TOTAL();
            this.setAvailable(this.total);
        },
        start() {
            return this._super.apply(this, arguments).then(() => {
                $("#spin").remove();
                $(".tabs-card").toggleClass("d-none");
                
                if(!$(".tab").length) {
                    $(".tabs-card").html(`
                        <h4 class="text-center py-1">
                            Agrega un método de pago, contacta con el administrador del sitio
                        </h4>
                    `);

                    return;
                }
           
                Object.assign(this, {
                    currency: $("input[name='pricelist_currency_name']").val(),
                    symbol: $("input[name='pricelist_currency_symbol']").val(),
                    rate: +$("input[name='ref_rate']").val(),
                    refSymbol: $("input[name='ref_symbol']").val(),
                });
                
                const ID = this.$el.find(".tab:first-child")[0].id;
                
                [this.selected, this.type] = [ID, ID.split("-")[1]];
                
                this.total = TOTAL();

                this.toggle();
                this.setAvailable(this.total);

                $("#tab-available button").click(this.handleClick.bind(this));
                this.$el.on("update", this.handleUpdate.bind(this));

                if($("input[type='number'][data-rate]").length !== $("input[type='number']").length)
                    alert("Algunos métodos de pago no tienen una moneda o una tasa configurada");
            });
        },
        handleClick(e) {
            const $button = $(e.target);

            const VALUE = +($button.text().split(" ")[0]);

            if(Number.isNaN(VALUE)) return;

            const $input = $button
                .parent()
                .parent()
                .find(`#payment-type-${this.type}  .form-quantity`)
                .filter(function() { 
                    return $(this).css("display") != "none"; 
                })
                .find("input")
                
            $input.val(format(VALUE + Number($input.val()))).trigger("input");
        },
        setAvailable(amount) {
            $("#tab-available button").text((amount > 0) ? amount + " " + this.symbol : 'Nada!');
            $("#total-ref").text(
                (amount > 0) 
                    ? format(
                        (this.currency === "VEF") ? amount / this.rate : amount * this.rate
                    ) + this.refSymbol
                    : "Nada!"
            );
        },
        toggle() {
            const result = this.hide();

            $(`#payment-type-${this.type} > nav > button:first-child`).click().addClass("selected");
        
            const { selected } = this;

            (result) && $(".tab")
                .removeClass("selected")
                .filter(function() {
                    return this.id === selected;
                })
                .addClass("selected");

            return result;
        },
        hide() {
            const self = this;

            if(self?.active && self?.active?.querySelector("input[data-reference]")) {
                const active = $(self.active);

                if(+active.find("input[data-payment-id]").val() && !(active.find("input[data-reference]").val())) {
                    this.do_warn(false, _t('La referencia es obligatoria'));

                    return 0;
                }
            }
                
            $(".current-form > div").each(function() {
                if(this.id === `payment-type-${self.type}`) {
                    $(this).show();
                    self.active = this;
                } else {
                    $(this).hide();
                }
            });

            return 1
        },
        changePaymentType({ target }) {
            const [ temp1, temp2 ] = [this.selected, this.type];

            [this.selected, this.type] = [target.id, target.id.split("-")[1]];

            const result = this.toggle();

            (!result) && ([this.selected, this.type] = [ temp1, temp2 ]);
        },
        changePaymentAccount({ currentTarget }) {
            const self = this;

            if(self?.active && self?.active?.querySelector("input[data-reference]")) {
                const active = $(self.active);

                if(+active.find("input[data-payment-id]").val() && !(active.find("input[data-reference]").val()))
                    return this.do_warn(false, _t('La referencia es obligatoria'));
            }

            $(`#payment-type-${self.type} > nav > button.selected`).removeClass("selected");
            $(`#payment-type-${self.type} > .payment-quantity > .form-quantity`)
                .each(function() {
                    const $el = $(this);

                    if($el.has(`input[name='payment-${self.type}-${currentTarget.dataset.typeId}-quantity-dollar']`).length) {
                        $el.show();
                        $(currentTarget).addClass("selected");
                    } else {
                        $el.hide();
                    }
                });
        },
        getAllInputs() {
            return [...document.querySelectorAll(`input[type='number'][data-currency='${this.currency}']`)]
                .map(({ value }) => +value)
                .filter(Boolean);
        },
        handleInput(e) {
            const $target = e.target;
            const { currency, rate } = $target.dataset;

            const $inverse = $target
                .parentElement
                .parentElement
                .querySelector(`input[data-currency="${(currency === "USD") ? "VEF" : "USD"}"]`);
                
            const val = $target.value;

            $inverse.value = format((currency === "USD") ? val * rate : val / rate);
            
            const VALUES = this.getAllInputs();

            this.amount = format(VALUES.reduce((prev, n) => prev + n, 0));

            const $total = $(".tab-total");
            const $button = $("#payment_button");
            const AVAILABLE = format(this.total - this.amount);

            this.setAvailable(AVAILABLE);

            const $change = $("#change-amount");

            if(this.amount < (this.total - 0.16)) {
                $button.prop("disabled", true);
                $total.addClass("d-none").html("");
                $change.text("");
                return;
            }

            if(this.amount > this.total) $change.text("Cambio: " + (format(this.amount - this.total) + this.symbol));
            else $change.text("");

            $button.prop("disabled", false);

            $total.removeClass([
                "d-none", 
                "border-warning", 
                "text-warning", 
                "text-success",
                "border-success"
            ]).addClass(
                (this.amount < (this.total - 0.16))
                    ? ["border-warning", "text-warning"]
                    : ["text-success", " border-success"]
            );

            let text = [
                `Total a pagar: <strong>${this.amount + this.symbol}</strong> dividido`,
                (VALUES.length > 1) 
                    ? `entre <strong>${VALUES.length}</strong> métodos de pago`
                    : "en un sólo método de pago"
            ];

            $total.html(text.join(" "));
        },
    });

    publicWidget.registry.PaymentProcessing.include({
        displayContent() {
            this._super.apply(this, arguments);

            document.querySelector("sup.my_cart_quantity").textContent = 0;
        }
    });

    return publicWidget.registry.TabPaymentForm;
});