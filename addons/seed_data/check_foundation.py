from datetime import timedelta
from odoo import fields
from odoo.exceptions import ValidationError, AccessError

p=env['res.partner'].create({'name':'Kiểm thử không lưu'})
q=env['res.partner'].create({'name':'Khách khác không lưu'})
pet=env['petcare.demo.pet'].create({'name':'Miu','species':'cat','owner_id':p.id})
svc=env['petcare.demo.service'].create({'name':'Grooming kiểm thử'})
slot=env['petcare.demo.slot'].create({'name':'Khung giờ kiểm thử','start_at':fields.Datetime.now()+timedelta(days=2),'capacity':1,'reserved':1})
b=env['petcare.demo.booking'].create({'owner_id':p.id,'pet_id':pet.id,'service_id':svc.id,'slot_id':slot.id})
try:
 with env.cr.savepoint():
  env['petcare.demo.booking'].create({'owner_id':q.id,'pet_id':pet.id,'service_id':svc.id,'slot_id':slot.id})
  raise AssertionError('Không chặn thú cưng thuộc người khác')
except ValidationError: print('PASS chặn thú cưng không thuộc chủ đặt')
b.action_confirm(); assert b.state=='confirmed';print('PASS nhân viên xác nhận lịch')
b.action_cancel();slot.invalidate_recordset(['reserved']); assert b.state=='cancelled' and slot.reserved==0;print('PASS hủy lịch trả lại chỗ')
portal=env.ref('base.public_user')
try:
 env['petcare.demo.pet'].with_user(portal).search([])
 raise AssertionError('Public không được xem tất cả hồ sơ')
except AccessError:print('PASS khách chưa đăng nhập không đọc được toàn bộ hồ sơ')
env.cr.rollback()
print('PASS kiểm thử được hoàn tác')
