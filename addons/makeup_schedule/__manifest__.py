{
    'name': 'Lịch Học Bù',
    'version': '1.0',
    'summary': 'Quản lý lịch học bù cho học sinh vắng',
    'description': '''
        Module dành cho Trung tâm Tư vấn Giáo dục Nhật Minh:
        - Ghi nhận học sinh vắng từng buổi
        - Tạo lịch học bù tự động
        - Theo dõi trạng thái đã học bù hay chưa
        - Xem báo cáo học sinh vắng theo tháng
    ''',
    'author': 'Nhóm 5 - UTH',
    'category': 'Education',
    'depends': ['base', 'calendar'],
    'data': [
        'security/ir.model.access.csv',
        'views/makeup_schedule_view.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}