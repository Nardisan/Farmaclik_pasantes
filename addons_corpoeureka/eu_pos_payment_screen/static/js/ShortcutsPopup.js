odoo.define('eu_pos_payment_screen.ShortcutsPopup', function(require) {
    'use strict';

    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');

    class ShortcutsPopup extends AbstractAwaitablePopup {
        get navigator() {
            return window.navigator.userAgent.toLowerCase();
        }
    }
    ShortcutsPopup.template = 'ShortcutsPopup';
    ShortcutsPopup.defaultProps = {
        confirmText: 'Ok',
        cancelText: 'Cancel',
        title: 'Shortcuts',
    };

    Registries.Component.add(ShortcutsPopup);

    return ShortcutsPopup;
});
