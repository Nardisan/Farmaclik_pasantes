//Copyright 2020 Shurshilov Artem <shurshilov.a@yandex.ru>
odoo.define("sector_and_ciudad_changue", function(require) {
    "use strict";
    var ajax = require("web.ajax");
    var publicWidget = require('web.public.widget');
    var wSaleUtils = require('website_sale.utils');
    var VariantMixin = require('sale.VariantMixin');
    var utils = require('web.utils');

    $(document).ready(function(){
            var state           = $('select[name="sector"]');
            var stateOptions    = state.filter(':enabled').find('option:not(:first)');
        $('select[name="ciudad"]').on('change', function(event) {
            
            var $country        = $('select[name="ciudad"]');
            var countryID       = ($country.val() || 0);
            stateOptions.detach();
            var displayedState = stateOptions.filter('[data-sector-id=' + countryID + ']');
            var nb = displayedState.appendTo(state).show().length;
            state.parent().toggle(nb >= 1);
        });
    });
});