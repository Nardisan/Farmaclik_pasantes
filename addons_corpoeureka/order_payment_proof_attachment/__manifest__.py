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
  "name"                 :  "Website Proof of payment Attachment",
  "summary"              :  """The module is to attach the payment proof for the manual transfer mode of payment.""",
  "category"             :  "Website/Website",
  "version"              :  "1.0.6",
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-Website-Proof-Of-Payment-Attachment.html",
  "description"          :  """The module allows you to give preference to users who already made the payment and attached the payment proof""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=order_payment_proof_attachment&version=13.0&custom_url=/shop",
  "depends"              :  [
                             'website_sale',
                             'sale',
                            ],
  "data"                 :  [
                             'views/views.xml',
                             'views/templates.xml',
                             'edi/attachment_mail.xml',
                            ],
  "images"               :  ['static/description/order-payment-proof-attachment-Banner.png'],
  "price"                :  49,
  "currency"             :  "USD",
}