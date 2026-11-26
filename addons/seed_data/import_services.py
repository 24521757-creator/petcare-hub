from datetime import timedelta
from odoo import fields
Service=env['petcare.demo.service'].sudo()
for name,description in [('Tắm và vệ sinh cơ bản','Gói minh họa: tắm, sấy và vệ sinh cơ bản cho chó hoặc mèo.'),('Cắt tỉa lông','Gói minh họa: chăm sóc và cắt tỉa lông cho chó hoặc mèo.')]:
 if not Service.search_count([('name','=',name)]): Service.create({'name':name,'description':description})
Slot=env['petcare.demo.slot'].sudo()
for day in (1,2,3):
 start=fields.Datetime.now().replace(hour=3,minute=0,second=0,microsecond=0)+timedelta(days=day)
 name='Lịch minh họa '+(start+timedelta(hours=7)).strftime('%d/%m/%Y %H:%M')
 if not Slot.search_count([('name','=',name)]): Slot.create({'name':name,'start_at':start,'capacity':3})
env.cr.commit()
print('SERVICES',Service.search_count([]),'SLOTS',Slot.search_count([]))
