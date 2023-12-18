/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */

odoo.define('pos_stock.ProductScreen', function (require) {
    "use strict";

    const ProductScreen = require('point_of_sale.ProductScreen');

    const Registries = require('point_of_sale.Registries');

    const PosProductScreen = (ProductScreen) =>
        class extends ProductScreen {
            mounted(){
                super.mounted();
                this.env.pos.set_stock_qtys(this.env.pos.get('wk_product_qtys'));
                this.env.pos.wk_change_qty_css();
            }
    }
    Registries.Component.extend(ProductScreen, PosProductScreen);



});