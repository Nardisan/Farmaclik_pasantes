odoo.define('flexipharmacy.PosContext', function (require) {
    'use strict';

    const { Context } = owl;

    // Create global context objects
    // e.g. component.env.device = new Context({ isMobile: false });
    return {
        returnOrderManagement: new Context({ searchString: '', selectedOrder: null }),
        orderManagement: new Context({ searchString: '', selectedOrder: null }),
        chrome: new Context({ showOrderSelector: true }),
    };
});
