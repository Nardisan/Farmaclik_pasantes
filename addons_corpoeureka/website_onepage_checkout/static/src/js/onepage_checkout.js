"use strict";
odoo.define('website_onepage_checkout.website_onepage_checkout', function(require) {

    require('web.dom_ready');

    var core = require('web.core');
    var ajax = require('web.ajax');

    var _t = core._t;

    $(document).ready(function() {
        $('.oe_website_sale').each(function() {
            var oe_website_sale = this;

            $(oe_website_sale).on('click', '.submit-billing-btn', function(ev) {
                var shipping = $('#shipping-panel-data').data('shipping');
                if (shipping === 'off') {
                    confirm_order_details(oe_website_sale, 'billing-panel');
                } else {
                    success_panel('billing-panel');
                }
            });

            $(oe_website_sale).on('click', '.submit-shipping-btn', function(ev) {
                $('.oe_website_sale_onepage .has-error').removeClass('has-error');
                confirm_order_details(oe_website_sale, 'shipping-panel');
            });

            $(oe_website_sale).on('click', '.submit-extra-info-btn', function(e) {
                e.preventDefault();
                success_panel('extra-step-panel');
            });

            $(oe_website_sale).on('click', '.submit-delivery-btn', function(e) {
                success_panel('delivery-method-panel');
            });

            $(oe_website_sale).on('click', '.submit-delivery-btn', function(e) {
                success_panel('delivery-method-panel');
            });
        });

        function set_order_amount(oe_website_sale, result) {
            console.log("result 1");
            console.log(result);
            // order final total
            $('#order_total .oe_currency_value').text(result.order_total);
            $('#onepage_total .oe_currency_value').text(result.order_total);
            var total_ammount = (result.order_total).toString().replace(',', '');
            $(oe_website_sale).find('input[name="amount"]').val(total_ammount);

            // order tax amount
            $('#order_total_taxes .oe_currency_value').text(result.order_total_taxes);
            $('#onepage_taxes .oe_currency_value').text(result.order_total_taxes);

            // order total without tax and delivery
            $('#order_subtotal .oe_currency_value').text(result.order_subtotal);
            $('#onepage_subtotal .oe_currency_value').text(result.order_subtotal);

            // order delivery amount
            $('#order_delivery .oe_currency_value').text(result.order_total_delivery);
            $('#onepage_delivery .oe_currency_value').text(result.order_total_delivery);

        }

        function success_panel(panel_selector) {
            $('#' + panel_selector).attr('class', '').addClass('card-header bg-success');
            $('#' + panel_selector).parent('.card').attr('class', '').addClass('card border-success');
            $('#' + panel_selector).parent('.card').next('.card').find('button.btn-link').removeClass('hide_class').trigger("click");
        }

        function error_panel(panel_selector, message) {
            $('#' + panel_selector).attr('class', '').addClass('card-header bg-danger');
            $('#' + panel_selector).parent('.card').attr('class', '').addClass('card border-danger');
            $('#' + panel_selector).parent('.card').nextAll().find('button.btn-link').addClass('hide_class');
            console.log(message);
        }

        function confirm_order_details(oe_website_sale, panel_selector) {
            $('.onepage-loader-big').show();
            ajax.jsonRpc('/shop/onepage/confirm_order', 'call', {})
            .then(function(result) {
                if (result[0]) {
                    var $template = $(result[2]);
                    var error = $template.find('input[name="delivery-error"]').val();
                    if (error) {
                        $('button.submit-delivery-btn').hide();
                        // error_panel('delivery-method-panel', '');
                    } else {
                        $('button.submit-delivery-btn').show();
                    }
                    $('#delivery-method-collapse .card-body').html($template);

                    if (result[1].success) {
                        set_order_amount(oe_website_sale, result[1]);
                        ajax_appended_delivery_carrier();
                        success_panel(panel_selector);
                    } else {
                        error_panel(panel_selector, '');
                    }

                } else {
                    window.location.href = result[1];
                }
                $('.onepage-loader-big').hide();
            })
            .catch(function(result) {
                $('.onepage-loader-big').hide();
                error_panel('shipping-panel', 'fail executed');
            });
        }

        function ajax_appended_delivery_carrier() {
                /* Handle interactive carrier choice + cart update */
            var $pay_button = $('#o_payment_form_pay');

            var _onCarrierUpdateAnswer = function(result) {
                var $amount_delivery = $('#order_delivery span.oe_currency_value');
                var $amount_untaxed = $('#order_total_untaxed span.oe_currency_value');
                var $amount_tax = $('#order_total_taxes span.oe_currency_value');
                var $amount_total_ref =  $("#multicurrency_cart_two span.oe_currency_value");
                var $amount_total = $('#order_total span.oe_currency_value');
                var $carrier_badge = $('#delivery_carrier input[name="delivery_type"][value=' + result.carrier_id + '] ~ .badge.d-none');
                var $compute_badge = $('#delivery_carrier input[name="delivery_type"][value=' + result.carrier_id + '] ~ .o_delivery_compute');
                var $discount = $('#order_discounted');

                if ($discount && result.new_amount_order_discounted) {
                    $discount.find('.oe_currency_value').text(result.new_amount_order_discounted);
                    // We are in freeshipping, so every carrier is Free
                    $('#delivery_carrier .badge').text(_t('Gratis'));
                }

                Object.keys(result).forEach((key) => {
                    const VALUE = result[key];

                    result[key] = (key.includes("amount")) 
                        ? Number(VALUE).toFixed(2)
                        : VALUE;
                });

                if (result.status === true) {
                    $carrier_badge.children('span').text(result.new_amount_delivery);
                    $carrier_badge.removeClass('d-none');
                    $compute_badge.addClass('d-none');
                    $pay_button.prop('disabled', false);
                }
                else {
                    console.error(result.error_message);
                    $compute_badge.text(result.error_message);
                }
                
                $amount_delivery.text(result.new_amount_delivery);
                $amount_untaxed.text(result.new_amount_untaxed);
                $amount_tax.text(result.new_amount_tax);
                $amount_total.text(result.new_amount_total);
                $amount_total_ref.text(result.new_amount_total_ref);
                $("input[name='amount_total']").val(result.new_amount_total);
                document.querySelector("form.o_payment_form").dispatchEvent(new Event("update"));
            };

            var _onCarrierClick = function(ev) {
                $pay_button.prop('disabled', true);
                var carrier_id = $(ev.currentTarget).val();
                var values = {'carrier_id': carrier_id};
                ajax.jsonRpc('/shop/update_carrier', 'call', values).then(_onCarrierUpdateAnswer);
            };

            var $carriers = $("#delivery_carrier input[name='delivery_type']");
            $carriers.click(_onCarrierClick);
        }
    });
});
