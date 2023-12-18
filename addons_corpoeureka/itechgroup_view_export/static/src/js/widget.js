odoo.define('itechgroup_view_export.widget_colorpicker', function(require) {
    "use strict";

    var core = require('web.core');
    var widget = require('web.Widget');
    var field_registry = require('web.field_registry');
    var fields = require('web.basic_fields');


    var FieldColorPicker = fields.FieldChar.extend({
        template: 'FieldColorPicker',
        widget_class: 'oe_form_field_color',

        _renderReadonly: function () {
            var show_value = this.value;
            this.$el.text(show_value);
            this.$el.css("background-color", show_value);
            this.$el.css("border-radius", "10px");
            this.$el.css("padding", "2px 7px");
            this.$el.css("font-size", "8px");
            this.$el.css("text-align", "center");
            this.$el.css("color", "white");
        },

        _getValue: function () {
            var $input = this.$el.find('input');
            return $input.val();
        },

        _renderEdit: function () {
            var show_value = this.value;
            var $input = this.$el.find('input');
            $input.val(show_value);
            this.$el.colorpicker({format: 'hex'});
            this.$input = $input;
        }

    });

    field_registry.add('colorpicker', FieldColorPicker);

    return {
        FieldColorPicker: FieldColorPicker
    };
});
