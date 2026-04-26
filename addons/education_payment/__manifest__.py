{
    'name': 'Quản Lý Thanh Toán Học Phí',
    'version': '1.0',
    'summary': 'Quản lý thanh toán học phí và liên kết hóa đơn',
    'description': '''
        Module Quản Lý Thanh Toán Học Phí:
        - Ghi nhận học phí của từng học sinh
        - Liên kết với hóa đơn Odoo
        - Tạo hóa đơn từ phiếu thanh toán
        - Tạo mã QR chuyển khoản VietQR
        - Theo dõi trạng thái thanh toán
    ''',
    'author': 'Nhóm 5 - UTH',
    'category': 'Education',
    'depends': ['base', 'contacts', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/education_payment_view.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}