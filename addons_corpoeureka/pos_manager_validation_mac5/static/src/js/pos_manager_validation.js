odoo.define('pos_manager_validation.pos_manager_validation', function (require) {
"use strict";

const Chrome = require('point_of_sale.Chrome');
const NumberBuffer = require('point_of_sale.NumberBuffer');
const NumpadWidget = require('point_of_sale.NumpadWidget');
const ProductScreen = require('point_of_sale.ProductScreen');
const Registries = require('point_of_sale.Registries');
const TicketScreen = require('point_of_sale.TicketScreen');

var models = require('point_of_sale.models');


models.load_fields('res.users', ['pos_security_pin'])


const PosUserAccessChrome = (Chrome) =>
    class extends Chrome {
        async _closePos() {
            if (this.env.pos.config.iface_validate_close) {
                var managerUserIDs = this.env.pos.config.manager_user_ids;
                var users = this.env.pos.users;

                const { confirmed, payload } = await this.showPopup('NumberPopup', {
                    title: this.env._t('Abarrotes San Luis'),
                    isPassword: true,
                });
                var password = payload ? payload.toString() : ''

                if (confirmed) {
                    this.env.pos.manager = false;
                    for (var i = 0; i < users.length; i++) {
                        if (managerUserIDs.indexOf(users[i].id) > -1
                                && password === (users[i].pos_security_pin || '')) {
                            this.env.pos.manager = users[i];
                        }
                    }
                    if (this.env.pos.manager) {
                        await super._closePos();
                    } else {
                        await this.showPopup('ErrorPopup', {
                            title: this.env._t('Error en la contraseña'),
                            body: this.env._t('Password incorrecto !!!'),
                        });
                    }
                }
            } else {
                await super._closePos();
            }
        }
    };


const PosUserAccessNumpadWidget = (NumpadWidget) =>
    class extends NumpadWidget {
        changeMode(mode) {
            if ((mode === 'discount' && this.env.pos.config.iface_validate_discount)
                    || (mode === 'price' && this.env.pos.config.iface_validate_price)) {
                var managerUserIDs = this.env.pos.config.manager_user_ids;
                var users = this.env.pos.users;

                this.showPopup('NumberPopup', {
                    title: this.env._t('Autorizacion del gerente'),
                    isPassword: true,
                }).then(({ confirmed, payload }) => {
                    var password = payload ? payload.toString() : ''

                    if (confirmed) {
                        this.env.pos.manager = false;
                        for (var i = 0; i < users.length; i++) {
                            if (managerUserIDs.indexOf(users[i].id) > -1
                                    && password === (users[i].pos_security_pin || '')) {
                                this.env.pos.manager = users[i];
                            }
                        }
                        if (this.env.pos.manager) {
                            super.changeMode(mode);
                        } else {
                            this.showPopup('ErrorPopup', {
                                title: this.env._t('Error'),
                                body: this.env._t('Password Incorrecto!!!'),
                            });
                        }
                    }
                });
            } else {
                super.changeMode(mode);
            }
        }
    };


const PosUserAccessProductScreen = (ProductScreen) =>
    class extends ProductScreen {
        _setValue(val) {
            var newQty = NumberBuffer.get() ? NumberBuffer.getFloat() : 0;
            var orderLines = this.currentOrder.get_orderlines();
            if (orderLines !== undefined && orderLines.length > 0) {
                var currentOrderLine = this.currentOrder.get_selected_orderline();
                var currentQty = this.currentOrder.get_selected_orderline().get_quantity();
                if (currentOrderLine && this.state.numpadMode === 'quantity'
                        && ((newQty < currentQty && this.env.pos.config.iface_validate_decrease_quantity)
                            || (val === 'remove' && this.env.pos.config.iface_validate_delete_orderline))) {
                    var managerUserIDs = this.env.pos.config.manager_user_ids;
                    var users = this.env.pos.users;

                    this.showPopup('NumberPopup', {
                        title: this.env._t('Abarrotes San Luis'),
                        isPassword: true,
                    }).then(({ confirmed, payload }) => {
                        var password = payload ? payload.toString() : ''

                        if (confirmed) {
                            this.env.pos.manager = false;
                            for (var i = 0; i < users.length; i++) {
                                if (managerUserIDs.indexOf(users[i].id) > -1
                                        && password === (users[i].pos_security_pin || '')) {
                                    this.env.pos.manager = users[i];
                                }
                            }
                            if (this.env.pos.manager) {
                                super._setValue(val);
                            } else {
                                this.showPopup('ErrorPopup', {
                                    title: this.env._t('Error'),
                                    body: this.env._t('Password Incorrecto!'),
                                });
                            }
                        }
                    });
                } else {
                    super._setValue(val);
                }
            } else {
                super._setValue(val)
            }
        }

        _onClickPay() {
            if (this.env.pos.config.iface_validate_payment) {
                var managerUserIDs = this.env.pos.config.manager_user_ids;
                var users = this.env.pos.users;

                this.showPopup('NumberPopup', {
                    title: this.env._t('Autorizacion del gerente'),
                    isPassword: true,
                }).then(({ confirmed, payload }) => {
                    var password = payload ? payload.toString() : ''

                    if (confirmed) {
                        this.env.pos.manager = false;
                        for (var i = 0; i < users.length; i++) {
                            if (managerUserIDs.indexOf(users[i].id) > -1
                                    && password === (users[i].pos_security_pin || '')) {
                                this.env.pos.manager = users[i];
                            }
                        }
                        if (this.env.pos.manager) {
                            super._onClickPay();
                        } else {
                            this.showPopup('ErrorPopup', {
                                title: this.env._t('Error'),
                                body: this.env._t('Password Incorrecto!!!'),
                            });
                        }
                    }
                });
            } else {
                super._onClickPay();
            }
        }

    };


const PosUserAccessTicketScreen = (TicketScreen) =>
    class extends TicketScreen {
        async deleteOrder(order) {
            if (this.env.pos.config.iface_validate_delete_order) {
                var managerUserIDs = this.env.pos.config.manager_user_ids;
                var users = this.env.pos.users;

                const { confirmed, payload } = await this.showPopup('NumberPopup', {
                    title: this.env._t('Abarrotes San Luis'),
                    isPassword: true,
                });
                var password = payload ? payload.toString() : ''

                if (confirmed) {
                    this.env.pos.manager = false;
                    for (var i = 0; i < users.length; i++) {
                        if (managerUserIDs.indexOf(users[i].id) > -1
                                && password === (users[i].pos_security_pin || '')) {
                            this.env.pos.manager = users[i];
                        }
                    }
                    if (this.env.pos.manager) {
                        await super.deleteOrder(order);
                    } else {
                        await this.showPopup('ErrorPopup', {
                            title: this.env._t('Error'),
                            body: this.env._t('Password Incorrecto!!!'),
                        });
                    }
                }
            } else {
                await super.deleteOrder(order);
            }
        }
    };


Registries.Component.extend(Chrome, PosUserAccessChrome);
Registries.Component.extend(NumpadWidget, PosUserAccessNumpadWidget);
Registries.Component.extend(ProductScreen, PosUserAccessProductScreen);
Registries.Component.extend(TicketScreen, PosUserAccessTicketScreen);

});
