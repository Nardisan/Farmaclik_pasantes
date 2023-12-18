odoo.define('point_of_sale.ReferenceClientListScreen', function(require) {
    'use strict';

    const { debounce } = owl.utils;
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const { useListener } = require('web.custom_hooks');
    const models = require('point_of_sale.models');

    models.load_fields('res.partner',['descuento','especialidad']);

    class ReferenceClientListScreen extends PosComponent{
        constructor(){
            super(...arguments);
            this.state = {
                query: null,
                selectedDoctor: this.props.doctor,
                selectedRefClient: '',
                detailIsShown: false,
            };
            this.updateClientList = debounce(this.updateClientList, 70);
        }
        back(){
            if(this.state.detailIsShown){
                this.state.detailIsShown = false;
                this.render();
            }else{
                this.props.resolve({ confirmed: false, payload: false });
                this.trigger('close-temp-screen');
            }
        }
        confirm(){
            if(this.props.flag == 'show_doctor'){
                this.env.pos.get_order().set_doctor(this.state.selectedDoctor)
                this.props.resolve({ confirmed: true, payload: this.state.selectedDoctor });
            }else{
                this.props.resolve({ confirmed: true, payload: this.state.selectedRefClient });
            }
            this.trigger('close-temp-screen');
        }
        get currentOrder() {
            return this.env.pos.get_order();
        }
        get clients() {
            if (this.state.query && this.state.query.trim() !== ''){
                let searched_result = this.env.pos.db.search_partner(this.state.query.trim());
                console.log("prueba this.state.query.trim()",this.state.query.trim());
                if(this.props.flag == 'show_doctor'){
                    return searched_result.filter(partner => partner.is_doctor == true);
                }else{
                    return searched_result
                }
            }else {
                // console.log("db",this.env.pos.db.partner_sorted.length);
                if(this.props.flag == 'show_doctor'){
                    let partners = this.env.pos.db.get_partners_sorted(this.env.pos.db.partner_sorted.length)
                    // console.log("PRUEBA: ",this.env.pos.db.get_partners_sorted, "partners: ",partners, "filtrado:",partners.filter(partner => partner.is_doctor == true));
                    return partners.filter(partner => partner.is_doctor == true);
                }else{
                    let partners = this.env.pos.db.get_partners_sorted(1000)
                    return partners
                }
            }
        }
        get isNextButtonVisible(){
            if(this.props.flag == 'show_doctor'){
                return this.state.selectedDoctor ? true : false;
            }else{
                return this.state.selectedRefClient ? true : false;
            }
        }
        get nextButton() {
            if (this.props.client && this.props.client === this.state.selectedRefClient && !this.props.flag) {
                alert('Cannot Select Reference Customer Same As Current Order Customer !!!!');
                return;
            }else if (this.props.doctor && this.props.doctor === this.state.selectedDoctor){
                return { command: 'deselect', text: 'Deselect Doctor' };
            }else {
                if(this.props.flag == 'show_doctor'){
                    return { command: 'set', text: 'Set Doctor' };
                }else{
                    return { command: 'set', text: 'Set Reference Customer' };
                }
            }
        }
        updateClientList(event){
            this.state.query = event.target.value;
            const clients = this.clients;
            if (event.code === 'Enter' && clients.length === 1) {
                if(this.props.flag == 'show_doctor'){
                    this.state.selectedDoctor = clients[0];
                }else{
                    this.state.selectedRefClient = clients[0];
                }
                this.clickNext();
            } else {
                this.render();
            }
        }
        clickClient(event){
            let partner = event.detail.client;
            if(this.props.flag == 'show_doctor'){
                if(this.state.selectedDoctor === partner){
                    this.state.selectedDoctor = null;
                }else{
                    this.state.selectedDoctor = partner;
                }
            }else{
                if(this.state.selectedRefClient === partner){
                    this.state.selectedRefClient = null;
                }else{
                    this.state.selectedRefClient = partner;
                }
            }
            this.render();
        }
        clickNext() {
            this.state.selectedRefClient = this.nextButton.command === 'set' ? this.state.selectedRefClient : null;
            this.state.selectedDoctor = this.nextButton.command === 'set' ? this.state.selectedDoctor : null;
            
            //DESCUENTO A LOS CLIENTES QUE TENGAN RECIPE DE UN MEDICO ESPECIFICO
            if(this.state.selectedDoctor ){
                var order    = this.env.pos.get_order();
                var lines    = order.get_orderlines();
                var product  = this.env.pos.db.get_product_by_id(this.env.pos.config.product_discount[0]);
                console.log(this.env.pos);
                // console.log(product);
                // console.log(this.state.selectedDoctor.descuento);
                if (product === undefined) {
                    this.showPopup('ErrorPopup', {
                        title : this.env._t("No discount product found"),
                         body  : this.env._t("The discount product seems misconfigured. Make sure it is flagged as 'Can be Sold' and 'Available in Point of Sale'."),
                     });
                     return;
                 }
        
                //Remove existing discounts
                var i = 0;
                while ( i < lines.length ) {
                    if (lines[i].get_product() === product) {
                        order.remove_orderline(lines[i]);
                    } else {
                        i++;
                    }
                }
        
                //Add discount
                //We add the price as manually set to avoid recomputation when changing customer.
                var base_to_discount = order.get_total_without_tax();
                if (product.taxes_id.length){
                    var first_tax = this.env.pos.taxes_by_id[product.taxes_id[0]];
                    if (first_tax.price_include) {
                        base_to_discount = order.get_total_with_tax();
                    }
                }
                
                var pc = this.state.selectedDoctor.descuento;
                
                if (this.state.selectedDoctor.descuento > 0){
                    var discount = - pc  / 100.0 * base_to_discount;
                
                    if( discount < 0 ){
                        order.add_product(product, {
                            price: discount,
                            lst_price: discount,
                            extras: {
                                price_manually_set: true,
                            },
                        });
                    }
                }
            }
            this.confirm();
        }
    }
    ReferenceClientListScreen.template = 'ReferenceClientListScreen';

    Registries.Component.add(ReferenceClientListScreen);

    return ReferenceClientListScreen;
});