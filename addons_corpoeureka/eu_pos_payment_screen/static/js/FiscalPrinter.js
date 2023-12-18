odoo.define('eu_pos_payment_screen.FiscalPrinter', function(require) {
    'use strict';

    const Registries = require('point_of_sale.Registries');
    const AbstractReceiptScreen = require('point_of_sale.AbstractReceiptScreen');

    const FiscalPrinter = (ReceiptScreen) => class extends ReceiptScreen {
        async handleClick(e) {
            const { pos } = this.env;
            const order = pos.get_order();

            if(!pos.config.fiscal_port)
                return this.showPopup('ErrorPopup', {
                    title: this.env._t('Error de conexión'),
                    body: this.env._t(
                        'No se ha especificado un puerto para establecer conexión la impresora fiscal.'
                    ),
                });

            const client = pos.get_client();

            const formato_completo = (documento) => {

                if (documento[0] == "J" || documento[0] == "G" ){

                    const numeros = [];
                    let suma = 0;

                    const LETRAS ={
                        V: 4,
                        E: 8, 
                        J: 12, 
                        G: 20,
                    };

                    numeros.push(+documento[2] * 3);
                    numeros.push(+documento[3] * 2);
                    numeros.push(+documento[4] * 7);
                    numeros.push(+documento[5] * 6);
                    numeros.push(+documento[6] * 5);
                    numeros.push(+documento[7] * 4);
                    numeros.push(+documento[8] * 3);
                    numeros.push(+documento[9] * 2);

                    suma = numeros.reduce((prev, n) => prev + n, 0);

                    if(documento[0] in LETRAS) suma += +(LETRAS[documento[0]]);

                    let result = 11 - (suma % 11);

                    result = (result > 10) ? 0 : result;

                    return( documento + "-" + result);

                }else{

                    return(documento)
                }
            }

            console.log(formato_completo(client.cedula))

            if(!client) return alert("El cliente es obligatorio");

            const orderlines = order.get_orderlines();
            const IS_NOTA_CREDITO = e.target.classList.contains("print_nota_credito");

            const Helpers = {
                tax: (line) => line.get_tax()
                    .toFixed(2)
                    .replace(/\.|\,/, "")
                    .slice(0, 4)
                    .padStart(4, "0"),
                format: (str) => str.slice(0, 40),
                convert: (line) => Math.abs(line.price / pos.config.show_currency_rate_real).toFixed(2)
            }; 

            let body = {
                port: pos.config.fiscal_port,
                ...(!(order.is_to_invoice()) && !IS_NOTA_CREDITO
                    ? {
                        action: "imprimir_no_fiscal",
                        lines: [
                            Helpers.format("CLIENTE: " + client.name),
                            Helpers.format("RIF: " + client.vat),
                            "-".repeat(40),
                            ...orderlines.map((line) => {
                                return Helpers.format([
                                    line.product.display_name,
                                    Helpers.convert(line),
                                    Helpers.tax(line)
                                ].join(" "));
                            })
                        ]
                    } : {
                        action: (IS_NOTA_CREDITO) ? "imprimir_devolucion" : "imprimir_fiscal",
                        lines: orderlines.map((line) => [
                            line.product.display_name.slice(0, 20).toUpperCase().replace(/\W/g, " "),
                            Math.abs(parseFloat(line.quantityStr)).toFixed(2),
                            Helpers.convert(line),
                            line.get_taxes()
                                .reduce((prev, { amount }) => prev + amount, 0)
                                .toString()
                                .padEnd(4, "0"),
                        ]),
                        customer: {
                            rif: formato_completo(client.cedula),
                            name: client.name
                        },
                    }),
            };

            if(IS_NOTA_CREDITO) {
                const { confirmed, payload } = await this.showPopup('NotaCreditoPopUp', {
                    title: this.env._t('Datos de la factura'),
                });

                if(!confirmed || !payload) return;

                Object.assign(body, payload);
            }
            

            return fetch("http://127.0.0.1/FIscalPrinter/index.php", {
                method: "POST",
                headers: {
                    "Content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                },
                mode: "cors",
                body: JSON.stringify(body),
            })
            .then(() => alert("La impresora se encuentra procesando su petición"))
            .catch(console.error);
        }
    }

    Registries.Component.extend(AbstractReceiptScreen, FiscalPrinter);

    return AbstractReceiptScreen;
});