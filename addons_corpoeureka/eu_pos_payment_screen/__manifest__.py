# -*- coding: utf-8 -*-
{
    'name': "eu_pos_payment_screen",
    'summary': " User-friendly payment screen to the POS",
    'author': "Corpoeureka",
    'website': "http://www.yourcompany.com",
    'category': 'Point of sale',
    'version': '1.0',
    'installable': True,
    'depends': [
        'base', 
        'point_of_sale',
        'eu_multi_currency',
        'flexipharmacy',
        'web',
        'mail',
        'account'
    ],
    'data': [
        "./data/template.xml",
        "./views/assets.xml",
        "./views/pos_payment_method_views.xml",
        "./views/pos_config_views.xml",
    ],
    'qweb': [
        "./static/xml/index.xml",
        "./static/xml/NumpadComponent.xml",
        "./static/xml/ButtonsComponent.xml",
        "./static/xml/PaymentComponent.xml",
        "./static/xml/HeaderComponent.xml",
        "./static/xml/InputComponent.xml",
        "./static/xml/WalletComponent.xml",
        "./static/xml/ShortcutsPopup.xml",
        "./static/xml/GiftCardComponent.xml",
        "./static/xml/FiscalPrinter.xml",
        "./static/xml/NotaCreditoPopUp.xml",
    ]
}