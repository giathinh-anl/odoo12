from odoo import models, fields, api
from odoo.exceptions import ValidationError
from urllib.parse import quote


class EducationPayment(models.Model):
    _name = 'education.payment'
    _description = 'Thanh Toán Học Phí'
    _order = 'payment_date desc, id desc'

    name = fields.Char(
        string='Mã phiếu thanh toán',
        required=True,
        copy=False,
        readonly=True,
        default='New'
    )

    student_id = fields.Many2one(
        'res.partner',
        string='Học sinh',
        required=True
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

    student_tags = fields.Many2many(
        'res.partner.category',
        string='Nhãn liên hệ',
        related='student_id.category_id',
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
    ], string='Môn học / Khóa học', required=True)

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

    # ── Liên kết hóa đơn Odoo ───────────────────
    invoice_id = fields.Many2one(
        'account.move',
        string='Hóa đơn liên kết',
        domain="[('move_type', '=', 'out_invoice')]",
        readonly=True,
        copy=False
    )

    invoice_name = fields.Char(
        string='Số hóa đơn',
        related='invoice_id.name',
        store=True,
        readonly=True
    )

    invoice_state = fields.Selection(
        related='invoice_id.state',
        string='Trạng thái hóa đơn',
        readonly=True
    )

    invoice_payment_state = fields.Selection(
        related='invoice_id.payment_state',
        string='Trạng thái thanh toán hóa đơn',
        readonly=True
    )

    # ── QR chuyển khoản ─────────────────────────
    bank_code = fields.Char(
        string='Mã ngân hàng',
        default='mbbank'
    )

    bank_account_no = fields.Char(
        string='Số tài khoản nhận',
        default='0123456789'
    )

    bank_account_name = fields.Char(
        string='Tên chủ tài khoản',
        default='TRUNG TAM NHAT MINH'
    )

    transfer_content = fields.Char(
        string='Nội dung chuyển khoản',
        compute='_compute_transfer_content',
        store=True
    )

    qr_payment_url = fields.Char(
        string='Link QR thanh toán',
        compute='_compute_qr_payment_url',
        store=True
    )

    qr_payment_html = fields.Html(
        string='Mã QR thanh toán',
        compute='_compute_qr_payment_html',
        sanitize=False
    )

    @api.onchange('student_id')
    def _onchange_student_id(self):
        for rec in self:
            if rec.student_id and rec.student_id.category_id:
                class_tags = rec.student_id.category_id.filtered(
                    lambda tag: tag.name and tag.name.lower().startswith('lớp')
                )
                if class_tags:
                    rec.class_name = class_tags[0].name

    @api.depends('total_amount', 'paid_amount')
    def _compute_remaining_amount(self):
        for rec in self:
            rec.remaining_amount = rec.total_amount - rec.paid_amount

    @api.depends('name', 'student_id')
    def _compute_transfer_content(self):
        for rec in self:
            if rec.name and rec.name != 'New':
                rec.transfer_content = rec.name.replace('/', '')
            else:
                rec.transfer_content = 'HOCPHI'

    @api.depends(
        'payment_method',
        'remaining_amount',
        'total_amount',
        'bank_code',
        'bank_account_no',
        'bank_account_name',
        'transfer_content'
    )
    def _compute_qr_payment_url(self):
        for rec in self:
            if rec.payment_method != 'bank' or not rec.bank_code or not rec.bank_account_no:
                rec.qr_payment_url = False
                continue

            amount = int(rec.remaining_amount if rec.remaining_amount > 0 else rec.total_amount)
            add_info = quote((rec.transfer_content or rec.name or 'HOCPHI')[:25])
            account_name = quote(rec.bank_account_name or '')

            rec.qr_payment_url = (
                f"https://img.vietqr.io/image/"
                f"{rec.bank_code}-{rec.bank_account_no}-compact2.jpg"
                f"?amount={amount}&addInfo={add_info}&accountName={account_name}"
            )

    @api.depends('qr_payment_url')
    def _compute_qr_payment_html(self):
        for rec in self:
            if rec.qr_payment_url:
                rec.qr_payment_html = f"""
                    <div style="text-align:center;">
                        <img src="{rec.qr_payment_url}"
                             style="max-width:280px; border:1px solid #ddd; border-radius:8px; padding:8px;"/>
                        <p style="margin-top:8px;">
                            Quét mã QR để chuyển khoản học phí
                        </p>
                    </div>
                """
            else:
                rec.qr_payment_html = """
                    <p style="color:#777;">
                        Chọn phương thức Chuyển khoản để hiển thị mã QR.
                    </p>
                """

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

    def action_create_invoice(self):
        for rec in self:
            if rec.invoice_id:
                raise ValidationError('Phiếu này đã có hóa đơn liên kết.')

            if not rec.student_id:
                raise ValidationError('Vui lòng chọn học sinh trước khi tạo hóa đơn.')

            if not rec.course_name:
                raise ValidationError('Vui lòng chọn môn học / khóa học.')

            if rec.total_amount <= 0:
                raise ValidationError('Vui lòng nhập tổng học phí trước khi tạo hóa đơn.')

            course_label = dict(rec._fields['course_name'].selection).get(
                rec.course_name,
                rec.course_name
            )

            line_name = f'Học phí {course_label}'
            if rec.class_name:
                line_name += f' - {rec.class_name}'

            invoice = self.env['account.move'].create({
                'move_type': 'out_invoice',
                'partner_id': rec.student_id.id,
                'invoice_date': rec.payment_date,
                'invoice_date_due': rec.due_date,
                'education_payment_id': rec.id,
                'invoice_origin': rec.name,
                'ref': rec.name,
                'invoice_line_ids': [(0, 0, {
                    'name': line_name,
                    'quantity': 1,
                    'price_unit': rec.total_amount,
                })],
            })

            rec.invoice_id = invoice.id

        return {
            'type': 'ir.actions.act_window',
            'name': 'Hóa đơn vừa tạo',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': invoice.id,
            'target': 'current',
        }

    def action_open_invoice(self):
        self.ensure_one()

        if not self.invoice_id:
            raise ValidationError('Phiếu này chưa có hóa đơn liên kết.')

        return {
            'type': 'ir.actions.act_window',
            'name': 'Hóa đơn liên kết',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': self.invoice_id.id,
            'target': 'current',
        }


class AccountMove(models.Model):
    _inherit = 'account.move'

    education_payment_id = fields.Many2one(
        'education.payment',
        string='Phiếu thanh toán học phí',
        readonly=True,
        copy=False
    )

    def action_open_education_payment(self):
        self.ensure_one()

        if not self.education_payment_id:
            raise ValidationError('Hóa đơn này chưa liên kết với phiếu thanh toán học phí.')

        return {
            'type': 'ir.actions.act_window',
            'name': 'Phiếu thanh toán học phí',
            'res_model': 'education.payment',
            'view_mode': 'form',
            'res_id': self.education_payment_id.id,
            'target': 'current',
        }