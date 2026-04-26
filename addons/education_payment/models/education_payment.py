from odoo import models, fields, api
from odoo.exceptions import ValidationError


class EducationPayment(models.Model):
    _name = 'education.payment'
    _description = 'Thanh Toán Học Phí'
    _order = 'payment_date desc, id desc'

    name = fields.Char(
        string='Mã phiếu',
        required=True,
        copy=False,
        readonly=True,
        default='New'
    )

    student_id = fields.Many2one(
        'res.partner',
        string='Học sinh',
        required=True,
        domain="[('is_company', '=', False)]"
    )

    student_phone = fields.Char(
        string='Số điện thoại',
        related='student_id.phone',
        store=True,
        readonly=True
    )

    student_email = fields.Char(
        string='Email',
        related='student_id.email',
        store=True,
        readonly=True
    )

    class_name = fields.Char(
        string='Lớp'
    )

    course_name = fields.Selection([
        ('toan', 'Toán'),
        ('ngu_van', 'Ngữ văn'),
        ('tieng_viet', 'Tiếng Việt'),
        ('tieng_anh', 'Tiếng Anh'),
        ('khac', 'Khác'),
    ], string='Môn học / Khoá học', required=True)

    payment_date = fields.Date(
        string='Ngày ghi nhận',
        default=fields.Date.today,
        required=True
    )

    due_date = fields.Date(
        string='Hạn thanh toán'
    )

    total_amount = fields.Float(
        string='Tổng học phí',
        required=True,
        default=0.0
    )

    paid_amount = fields.Float(
        string='Số tiền đã đóng',
        default=0.0
    )

    remaining_amount = fields.Float(
        string='Số tiền còn nợ',
        compute='_compute_remaining_amount',
        store=True
    )

    payment_method = fields.Selection([
        ('cash', 'Tiền mặt'),
        ('bank', 'Chuyển khoản'),
        ('momo', 'Ví MoMo'),
        ('other', 'Khác'),
    ], string='Phương thức thanh toán', default='cash')

    state = fields.Selection([
        ('draft', 'Nháp'),
        ('unpaid', 'Chưa thanh toán'),
        ('partial', 'Thanh toán một phần'),
        ('paid', 'Đã thanh toán'),
        ('cancel', 'Huỷ'),
    ], string='Trạng thái', default='draft', required=True)

    note = fields.Text(
        string='Ghi chú'
    )

    @api.depends('total_amount', 'paid_amount')
    def _compute_remaining_amount(self):
        for rec in self:
            rec.remaining_amount = rec.total_amount - rec.paid_amount

    @api.constrains('total_amount', 'paid_amount')
    def _check_amounts(self):
        for rec in self:
            if rec.total_amount < 0:
                raise ValidationError('Tổng học phí không được nhỏ hơn 0.')

            if rec.paid_amount < 0:
                raise ValidationError('Số tiền đã đóng không được nhỏ hơn 0.')

            if rec.paid_amount > rec.total_amount:
                raise ValidationError('Số tiền đã đóng không được lớn hơn tổng học phí.')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            last_record = self.search([], order='id desc', limit=1)
            next_number = last_record.id + 1 if last_record else 1
            vals['name'] = 'PAY/%05d' % next_number

        return super().create(vals)

    def action_confirm(self):
        for rec in self:
            if rec.total_amount <= 0:
                raise ValidationError('Vui lòng nhập tổng học phí trước khi xác nhận.')

            if rec.paid_amount == 0:
                rec.state = 'unpaid'
            elif rec.paid_amount < rec.total_amount:
                rec.state = 'partial'
            else:
                rec.state = 'paid'

    def action_register_payment(self):
        for rec in self:
            if rec.total_amount <= 0:
                raise ValidationError('Vui lòng nhập tổng học phí.')

            if rec.paid_amount <= 0:
                raise ValidationError('Vui lòng nhập số tiền đã đóng.')

            if rec.paid_amount < rec.total_amount:
                rec.state = 'partial'
            elif rec.paid_amount == rec.total_amount:
                rec.state = 'paid'
            else:
                raise ValidationError('Số tiền đã đóng không hợp lệ.')

    def action_set_draft(self):
        for rec in self:
            rec.state = 'draft'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'