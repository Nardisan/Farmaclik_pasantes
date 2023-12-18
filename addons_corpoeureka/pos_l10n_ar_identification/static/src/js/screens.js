odoo.define('pos_l10n_ar_identification.screens', function(require) {
    'use strict';

    const ClientListScreen = require('point_of_sale.ClientListScreen');
    const Registries = require('point_of_sale.Registries');

    const POSSaveClientOverride = ClientListScreen =>
        class extends ClientListScreen {
            async saveChanges(event) {

                const CEDULA = $(".cedula").val();

                const TELEFONO = $(".telefono").val();

                const SIN_TELEFONO = $(".sin-telefono").is(':checked');

                if(!CEDULA) return await this.showPopup('ErrorPopup', {

                        title: this.env._t('SE REQUIERE EL CAMPO CÉDULA CON FORMATO VÁLIDO'),
                        body: this.env._t('Debe completar el campo cédula con formato válido ( EJ: V-12345678).'),

                });

                if( !SIN_TELEFONO && (!TELEFONO || !(/^[0-9]{10}$/.test(TELEFONO))) ) return await this.showPopup('ErrorPopup', {

                    title: this.env._t('SE REQUIERE EL CAMPO TELÉFONO CON FORMATO VÁLIDO'),
                    body: this.env._t('Debe completar el campo teléfono con formato válido (EJ: 4120001122).'),

                 });

                const numeros = [];
                let suma = 0;

                const LETRAS ={
                    V: 4,
                    E: 8, 
                    J: 12, 
                    G: 20,
                };

                numeros.push(+CEDULA[2] * 3);
                numeros.push(+CEDULA[3] * 2);
                numeros.push(+CEDULA[4] * 7);
                numeros.push(+CEDULA[5] * 6);
                numeros.push(+CEDULA[6] * 5);
                numeros.push(+CEDULA[7] * 4);
                numeros.push(+CEDULA[8] * 3);
                numeros.push(+CEDULA[9] * 2);

                suma = numeros.reduce((prev, n) => prev + n, 0);

                if(CEDULA[0] in LETRAS) suma += +(LETRAS[CEDULA[0]]);

                let result = 11 - (suma % 11);

                result = (result > 10) ? 0 : result;

                let rif, vat;

                rif = vat = CEDULA + result;

                await super.saveChanges(event).then(() => {
                     (this.state.selectedClient?.id) && this.rpc({
                        model: "res.partner",
                        method: "write",
                        args: [[this.state.selectedClient.id], { rif, vat }]
                    });
                });
            }
        };

    Registries.Component.extend(ClientListScreen, POSSaveClientOverride);

    return ClientListScreen;
});

