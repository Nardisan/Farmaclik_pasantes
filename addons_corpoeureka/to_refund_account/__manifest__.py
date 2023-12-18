{
    'name': 'Refund Accounts',
    'name_vi_VN': 'Tài khoản hoàn tiền',
    'version': '1.0',
    'category': 'Accounting',
    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': 'https://v13demo-int.erponline.vn',
    'support': 'apps.support@viindoo.com',
    'summary': 'Different Accounts for Refunding income and expense',
    'summary_vi_VN': 'Các tài khoản khác nhau cho việc Hoàn tiền doanh thu và chi phí',
    'description': """
By default, Odoo posts the amounts back to the original income/expense account when validating refund invoices.
This module will allow you to sepecify different accounts for income and expense refunds.

Instructions:
-------------
* Income/Expense Refund Accounts must be set on the product or its category. Otherwise, it will fall back to the Odoo's default behaviour
* Invoices without a product specified, the refund account will be taken from the journal entry of the correspoding original invoice.
* In multi-company environment, the refund accounts are company specific.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

""",
    'description_vi_VN': """
Theo mặc định, Odoo gửi số tiền trở lại tài khoản doanh thu/chi phí ban đầu khi xác thực hoàn tiền hóa đơn.
Module này sẽ cho phép bạn phân tách các tài khoản khác nhau để hoàn tiền doanh thu và chi phí.

Hướng dẫn:
----------
* Tài khoản hoàn tiền doanh thu/chi phí phải được đặt trên sản phẩm hoặc danh mục của nó. Nếu không, nó sẽ quay trở lại hành vi mặc định của Odoo.
* Hóa đơn không sản phẩm được chỉ định, tài khoản hoàn tiền sẽ được lấy từ bút toán sổ nhật ký của hóa đơn gốc.
* Trong môi trường nhiều công ty, các tài khoản hoàn tiền là công ty cụ thể.

Ấn bản hỗ trợ
=============
1. Ấn bản cộng đồng
2. Ấn bản doanh nghiệp

""",
    'depends': ['account'],
    'data': [
        'views/product_category_view.xml',
        'views/product_template_view.xml',
    ],

    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 18.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}