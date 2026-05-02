{
    'name': 'Quản Lý Thanh Toán Học Phí',
    'version': '1.0',
    'summary': 'Quản lý thanh toán học phí và liên kết hóa đơn',
    'description': '''
        Module Quản Lý Thanh Toán Học Phí:
        - Ghi nhận học phí của từng học sinh
        - Liên kết với Liên hệ
        - Liên kết với Sản phẩm trong Bán hàng
        - Tự lấy học phí theo sản phẩm đã chọn
        - Tự cộng tổng học phí
        - Tạo hóa đơn từ phiếu thanh toán
        - Tạo mã QR chuyển khoản VietQR
    ''',
    'author': 'Nhóm 5 - UTH',
    'category': 'Education',
    'depends': ['base', 'contacts', 'account', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'views/education_payment_view.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}