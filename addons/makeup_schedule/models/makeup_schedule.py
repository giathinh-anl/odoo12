from odoo import models, fields, api
from datetime import timedelta


class MakeupSchedule(models.Model):
    _name = 'makeup.schedule'
    _description = 'Lịch Học Bù'
    _order = 'absent_date desc'

    student_id = fields.Many2one(
        'res.partner',
        string='Tên học sinh',
        required=True,
        domain="[('is_company', '=', False)]"
    )

    student_name = fields.Char(
        string='Tên học sinh',
        related='student_id.name',
        store=True
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

    absent_date = fields.Date(
        string='Ngày vắng',
        required=True,
        default=fields.Date.today
    )

    absent_reason = fields.Char(
        string='Lý do vắng'
    )

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