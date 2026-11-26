from datetime import timedelta
from odoo import api, fields, models
from odoo.exceptions import ValidationError

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    petcare_source_url = fields.Char(string='URL nguồn tham khảo', copy=False)
    petcare_source_currency = fields.Char(string='Tiền tệ giá nguồn', copy=False)
    petcare_source_price = fields.Float(string='Giá nguồn tham khảo', digits=(16, 2), copy=False)
    petcare_exchange_rate = fields.Float(string='Tỷ lệ tham khảo USD/VND', digits=(16, 2), copy=False)
    petcare_source_weight = fields.Char(string='Quy cách nguồn', copy=False)

class PetcarePet(models.Model):
    _name = 'petcare.demo.pet'
    _description = 'Hồ sơ thú cưng (bản thử)'
    name = fields.Char(required=True)
    owner_id = fields.Many2one('res.partner', required=True, index=True, ondelete='restrict')
    species = fields.Selection([('dog', 'Chó'), ('cat', 'Mèo')], required=True)
    breed = fields.Char()
    birth_date = fields.Date()
    weight = fields.Float(string='Cân nặng (kg)')
    notes = fields.Text(string='Ghi chú chăm sóc')
    active = fields.Boolean(default=True)

    @api.constrains('weight', 'birth_date')
    def _check_pet(self):
        for pet in self:
            if pet.weight < 0 or (pet.birth_date and pet.birth_date > fields.Date.today()):
                raise ValidationError('Ngày sinh hoặc cân nặng không hợp lệ.')

class PetcareService(models.Model):
    _name = 'petcare.demo.service'
    _description = 'Dịch vụ chăm sóc (bản thử)'
    name = fields.Char(required=True)
    description = fields.Text()
    active = fields.Boolean(default=True)

class PetcareSlot(models.Model):
    _name = 'petcare.demo.slot'
    _description = 'Khung giờ chăm sóc (bản thử)'
    _order = 'start_at'
    name = fields.Char(required=True)
    start_at = fields.Datetime(required=True)
    capacity = fields.Integer(required=True, default=1)
    reserved = fields.Integer(default=0, readonly=True)
    active = fields.Boolean(default=True)
    @api.constrains('capacity')
    def _check_capacity(self):
        if any(slot.capacity < 1 for slot in self):
            raise ValidationError('Sức chứa phải lớn hơn 0.')
        if any(slot.reserved > slot.capacity for slot in self):
            raise ValidationError('Sức chứa không được nhỏ hơn số lịch đã giữ.')

class PetcareBooking(models.Model):
    _name = 'petcare.demo.booking'
    _description = 'Yêu cầu đặt lịch (bản thử)'
    _order = 'create_date desc'
    owner_id = fields.Many2one('res.partner', required=True, index=True, ondelete='restrict')
    pet_id = fields.Many2one('petcare.demo.pet', required=True, ondelete='restrict')
    service_id = fields.Many2one('petcare.demo.service', required=True, ondelete='restrict')
    slot_id = fields.Many2one('petcare.demo.slot', required=True, ondelete='restrict')
    state = fields.Selection([('pending','Chờ nhân viên'),('confirmed','Chờ thanh toán'),('cancelled','Đã hủy')], default='pending', required=True, readonly=True)
    expires_at = fields.Datetime(default=lambda self: fields.Datetime.now() + timedelta(minutes=15), readonly=True)
    note = fields.Text()
    @api.constrains('owner_id', 'pet_id')
    def _check_owner(self):
        for b in self:
            if b.pet_id.owner_id != b.owner_id:
                raise ValidationError('Thú cưng không thuộc tài khoản đặt lịch.')

    def action_confirm(self):
        for booking in self:
            if booking.state != 'pending' or booking.expires_at <= fields.Datetime.now():
                raise ValidationError('Yêu cầu đã hết hạn hoặc không còn chờ xác nhận.')
            booking.write({'state':'confirmed','expires_at':fields.Datetime.now()+timedelta(minutes=15)})

    def action_cancel(self):
        for booking in self.filtered(lambda b:b.state in ('pending','confirmed')):
            self.env.cr.execute('UPDATE petcare_demo_slot SET reserved = GREATEST(reserved-1,0) WHERE id=%s', [booking.slot_id.id])
            booking.write({'state':'cancelled'})

    @api.model
    def cron_expire(self):
        self.search([('state','in',['pending','confirmed']),('expires_at','<=',fields.Datetime.now())]).action_cancel()
