{
    'name': 'Quản Lý Thanh Toán Học Phí',
    'version': '1.0',
    'summary': 'Quản lý thanh toán học phí cho trung tâm giáo dục',
    'description': '''
        Module Quản Lý Thanh Toán Học Phí:
        - Ghi nhận học phí của từng học sinh
        - Theo dõi số tiền phải đóng, đã đóng và còn nợ
        - Quản lý trạng thái thanh toán
        - Liên kết học sinh với Liên hệ trong Odoo
    ''',
    'author': 'Nhóm 5 - UTH',
    'category': 'Education',
    'depends': ['base', 'contacts'],
    'data': [
        'security/ir.model.access.csv',
        'views/education_payment_view.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}