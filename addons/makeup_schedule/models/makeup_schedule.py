from odoo import models, fields, api
from datetime import timedelta


class MakeupSchedule(models.Model):
    _name = 'makeup.schedule'
    _description = 'Lịch Học Bù'
    _order = 'absent_date desc'

    # ── Liên kết học sinh từ Liên hệ ─────────────
    student_id = fields.Many2one(
        'res.partner',
        string='Tên học sinh',
        required=True
    )

    student_name = fields.Char(
        string='Tên học sinh',
        related='student_id.name',
        store=True,
        readonly=True
    )

    student_tags = fields.Many2many(
        'res.partner.category',
        string='Nhãn liên hệ',
        related='student_id.category_id',
        readonly=True
    )

    phone = fields.Char(
        string='Số điện thoại',
        related='student_id.phone',
        store=True,
        readonly=True
    )

    email = fields.Char(
        string='Email',
        related='student_id.email',
        store=True,
        readonly=True
    )

    class_name = fields.Char(
        string='Lớp',
        required=True
    )

    subject = fields.Selection([
        ('toan', 'Toán'),
        ('ngu_van', 'Ngữ văn'),
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
        string='Ngày học bù'
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

    note = fields.Text(
        string='Ghi chú'
    )

    # ── Tính tự động ────────────────────────────
    days_since_absent = fields.Integer(
        string='Số ngày chưa bù',
        compute='_compute_days_since_absent',
        store=False
    )

    is_urgent = fields.Boolean(
        string='Cần xếp gấp',
        compute='_compute_is_urgent',
        store=True
    )

    @api.onchange('student_id')
    def _onchange_student_id(self):
        """
        Khi chọn học sinh từ Liên hệ:
        - tự lấy lớp từ tag nếu tag có dạng 'Lớp 1', 'Lớp 8',...
        """
        for rec in self:
            if rec.student_id and rec.student_id.category_id:
                class_tags = rec.student_id.category_id.filtered(
                    lambda tag: tag.name and tag.name.lower().startswith('lớp')
                )
                if class_tags:
                    rec.class_name = class_tags[0].name

    @api.depends('absent_date', 'state')
    def _compute_days_since_absent(self):
        today = fields.Date.today()
        for rec in self:
            if rec.absent_date and rec.state != 'hoan_thanh':
                rec.days_since_absent = (today - rec.absent_date).days
            else:
                rec.days_since_absent = 0

    @api.depends('absent_date', 'state')
    def _compute_is_urgent(self):
        today = fields.Date.today()
        for rec in self:
            if rec.absent_date and rec.state == 'chua_xep':
                rec.is_urgent = (today - rec.absent_date).days >= 3
            else:
                rec.is_urgent = False

    # ── Nút bấm hành động ───────────────────────
    def action_xep_lich(self):
        for rec in self:
            rec.state = 'da_xep'

    def action_hoan_thanh(self):
        for rec in self:
            rec.state = 'hoan_thanh'

    def action_huy(self):
        for rec in self:
            rec.state = 'huy'

    @api.model
    def create(self, vals):
        record = super().create(vals)
        if record.absent_date and not record.makeup_date:
            record.makeup_date = record.absent_date + timedelta(days=3)
        return record