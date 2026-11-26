import csv
from pathlib import Path
source=Path('/mnt/extra-addons/seed_data/ban_dich_ten.csv')
updated=0
with source.open(encoding='utf-8-sig',newline='') as f:
 for row in csv.DictReader(f):
  translated=row['name_vi'].strip()
  product=env['product.template'].sudo().search([('default_code','=',row['sku'])],limit=1)
  if not translated or not product: continue
  translated=translated.replace('Thức ăn cho chó khô','Thức ăn khô cho chó').replace('thức ăn cho chó khô','thức ăn khô cho chó')
  translated=translated.replace('Thức ăn cho mèo khô','Thức ăn khô cho mèo').replace('thức ăn cho mèo khô','thức ăn khô cho mèo')
  translated=translated.replace('dành cho trưởng thành','dành cho thú cưng trưởng thành')
  product.update_field_translations('name', {'en_US':row['name_en'], 'vi_VN':translated})
  updated+=1
env.cr.commit()
print('Cập nhật tên tiếng Việt:',updated)
