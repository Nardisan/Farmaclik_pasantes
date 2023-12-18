odoo.define('eu_pos_payment_screen.ContactComponent', function(require) {
    'use strict';

    const ClientListScreen = require('point_of_sale.ClientListScreen');
    const Registries = require('point_of_sale.Registries');

    const ContactComponent = (Client) => class extends Client {
        async saveChanges(event) {
            if(!this.state.isNewClient) return super.saveChanges(event);

            // const { confirmed } = await this.showPopup('ConfirmPopup', {
            //     title: 'Antes de crear...',
            //     body: 'Te gustaría que el usuario tenga disponible su billetera en el sitio web?',
            // });

            const confirmed = false;

            if(!confirmed) return super.saveChanges(event);

            if (!event.detail.processedChanges.email) {
                return this.showPopup('ErrorPopup', {
                  title: _('A Customer Email Is Required'),
                });
            }

            await super.saveChanges(event).then(() => {
                (this.state.selectedClient?.id) && this.rpc({
                    model: "res.partner",
                    method: "action_apply",
                    args: [this.state.selectedClient.id]
                });
            });

            return alert("Se ha creado el usuario");
        }
    }

    Registries.Component.extend(ClientListScreen, ContactComponent);

    return ContactComponent;
});