odoo.define('eu_pos_payment_screen.SearchPartner', function (require) {
    "use strict";

    const DB = require('point_of_sale.DB');

    DB.include({
        _partner_search_string(partner) {
            let str = this._super.apply(this, arguments);

            if(partner.cedula) {
                str = str.replace(":", (":" + partner.cedula + "|"));
            }

            return str;
        }
    });
});