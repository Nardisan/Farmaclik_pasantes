odoo.define('l10n_ve_fiscal_requirements.models', function (require) {
	var models = require('point_of_sale.models');

    models.load_fields("res.partner", ['cedula', 'rif', 'residence_type']);

})