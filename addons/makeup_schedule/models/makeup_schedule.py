from odoo import models, fields, api
from datetime import timedelta

class MakeupSchedule(models.Model):
    _name = 'makeup.schedule'
    _description = 'Lịch Học Bù'
    _order = 'absent_date desc'

    # ── Thông tin học sinh ──────────────────────
    student_name = fields.Char(
        string='Tên học sinh',
        required=True
    )
    class_name = fields.Char(
        string='Lớp',
        required=True
    )
    subject = fields.Selection([
        ('toan', 'Toán'),
        ('tieng_viet', 'Tiếng Việt'),
        ('tieng_anh', 'Tiếng Anh'),
    ], string='Môn học', required=True)

    # ── Thông tin vắng ──────────────────────────
    absent_date = fields.Date(
        string='Ngày vắng',
        required=True,
        default=fields.Date.today
    )
    absent_reason = fields.Char(
        string='Lý do vắng'
    )

    # ── Lịch học bù ─────────────────────────────
    makeup_date = fields.Date(
        string='Ngày học bù',
    )
    makeup_time = fields.Char(
        string='Giờ học bù',
        placeholder='VD: 14:00 - 15:30'
    )
    state = fields.Selection([
        ('chua_xep', 'Chưa xếp lịch'),
        ('da_xep', 'Đã xếp lịch'),
        ('hoan_thanh', 'Đã học bù'),
        ('huy', 'Huỷ'),
    ], string='Trạng thái',
       default='chua_xep',
       required=True
    )
    note = fields.Text(string='Ghi chú')

    # ── Tính tự động ────────────────────────────
    days_since_absent = fields.Integer(
        string='Số ngày chưa bù',
        compute='_compute_days_since_absent',
        store=False
    )
    is_urgent = fields.Boolean(
        string='Cần xếp gấp',
        compute='_compute_is_urgent',
        store=False
    )

    @api.depends('absent_date', 'state')
    def _compute_days_since_absent(self):
        today = fields.Date.today()
        for rec in self:
            if rec.absent_date and rec.state != 'hoan_thanh':
                delta = today - rec.absent_date
                rec.days_since_absent = delta.days
            else:
                rec.days_since_absent = 0

    @api.depends('days_since_absent')
    def _compute_is_urgent(self):
        for rec in self:
            rec.is_urgent = rec.days_since_absent >= 3

    # ── Nút bấm hành động ───────────────────────
    def action_xep_lich(self):
        """Chuyển sang trạng thái đã xếp lịch"""
        self.state = 'da_xep'

    def action_hoan_thanh(self):
        """Đánh dấu đã học bù xong"""
        self.state = 'hoan_thanh'

    def action_huy(self):
        """Huỷ lịch học bù"""
        self.state = 'huy'

    @api.model
    def create(self, vals):
        """Khi tạo mới, tự gợi ý ngày học bù = ngày vắng + 3 ngày"""
        record = super().create(vals)
        if record.absent_date and not record.makeup_date:
            record.makeup_date = record.absent_date + timedelta(days=3)
        return record