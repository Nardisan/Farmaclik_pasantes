//Copyright 2020 Shurshilov Artem <shurshilov.a@yandex.ru>
odoo.define("additional_fields_signup.sector_and_ciudad_changue", function(require) {
    "use strict";
    var rpc = require('web.rpc');


    $(document).ready(function(){

            var state           = $('select[name="sector"]');
            var stateOptions    = state.last().filter(':enabled').find('option:not(:first)');
        $('select[name="ciudad"]').on('change', function(event) {
            
            var $country        = $('select[name="ciudad"]');
            var countryID=0
            if($country.length>1){
                $country.each(function() {
                    if ($(this).val()>countryID){
                        countryID=$(this).val();
                    }
                });
            }
            else {
                var countryID=($country.val()||0);
            }
            function removeDuplicates(arr) {
                var seen = {};
                arr.each(function() {
                    var txt = $(this).val();
                    console.log($(this).val())
                    if (seen[txt])
                    arr.remove($(this));
                    else
                        seen[txt] = true;
                });
                return arr;
            }
            
            
            stateOptions.detach();
            var displayedState = stateOptions.filter('[data-sector-id=' + countryID + ']');
            const setdisplayedState=removeDuplicates(displayedState);
            console.log(setdisplayedState);
            
            var nb = setdisplayedState.appendTo(state).show().length;
           
            state.parent().toggle(nb >= 1);
        });
    });

    
    
});