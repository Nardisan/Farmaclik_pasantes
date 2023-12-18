/** @odoo-module **/
odoo.define("user_membership.Main", function(require) {
    "use strict";

    const publicWidget = require('web.public.widget');
    const sAnimations = require('website.content.snippets.animation');
    
    new sAnimations.registry.WebsiteSale();

    publicWidget.registry.WebsiteSale.include({
        _onProductReady() {
            const $membership = this.$form.find("input[name='is_membership']");

            return ($membership.length)
                ? this._rpc({ route: "/cart/check-membership-product"})
                    .then((response) => !(response)
                        ? this._submitForm()
                        : alert("Sólo puedes comprar una membresía")
                    )
                : this._submitForm();
        }
    });
});