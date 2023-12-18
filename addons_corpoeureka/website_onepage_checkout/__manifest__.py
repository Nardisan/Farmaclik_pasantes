# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "Website Onepage Checkout",
  "summary"              :  """Onepage Checkout for Website""",
  "category"             :  "Website",
  "version"              :  "1.0.1",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-Website-Onepage-Checkout.html",
  "description"          :  """====================
**Help and Support**
====================
.. |icon_features| image:: website_onepage_checkout/static/src/img/icon-features.png
.. |icon_support| image:: website_onepage_checkout/static/src/img/icon-support.png
.. |icon_help| image:: website_onepage_checkout/static/src/img/icon-help.png

|icon_help| `Help <http://webkul.uvdesk.com/en/customer/create-ticket/>`_ |icon_support| `Support <http://webkul.uvdesk.com/en/customer/create-ticket/>`_ |icon_features| `Request new Feature(s) <http://webkul.uvdesk.com/en/customer/create-ticket/>`_""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=website_onepage_checkout&custom_url=/shop/checkout",
  "depends"              :  [
                             'website_sale_delivery',
                             'website_webkul_addons',
                             'eu_website_multicurrency'
                            ],
  "data"                 :  [
                             'security/ir.model.access.csv',
                             'views/onepage_config_view.xml',
                             'data/onepage_checkout_data.xml',
                             'views/webkul_addons_config_inherit_view.xml',
                             'views/templetes.xml',
                            ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  99,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}