import base64, json, pathlib, re
from odoo import fields
from datetime import timedelta

ROOT=pathlib.Path('/mnt/extra-addons/seed_data')
data=json.loads((ROOT/'products.json').read_text(encoding='utf-8'))
Category=env['product.public.category'].sudo()
def category(name,parent=None):
 domain=[('name','=',name),('parent_id','=',parent.id if parent else False)]
 return Category.search(domain,limit=1) or Category.create({'name':name,'parent_id':parent.id if parent else False})
dog=category('Chó');cat=category('Mèo')
dogfood=category('Thức ăn cho chó',dog);catfood=category('Thức ăn cho mèo',cat)
dogdry=category('Thức ăn khô',dogfood);catdry=category('Thức ăn khô',catfood)
vetfood=category('Dinh dưỡng thú y',dogfood)
Attribute=env['product.attribute'].sudo();Value=env['product.attribute.value'].sudo()
def attribute(name):
 a=Attribute.search([('name','=',name)],limit=1)
 return a or Attribute.create({'name':name,'create_variant':'no_variant','display_type':'multi','visibility':'visible'})
species=attribute('Loài thú cưng');brand=attribute('Thương hiệu')
stage=attribute('Độ tuổi');weight=attribute('Quy cách')
def value(attr,name):
 v=Value.search([('attribute_id','=',attr.id),('name','=',name)],limit=1)
 return v or Value.create({'attribute_id':attr.id,'name':name})
Product=env['product.template'].sudo();created=0
def extra_lines(row):
 result=[]
 name=row['name'].lower()
 if re.search(r'\b(puppy|kitten)\b',name): age='Thú cưng nhỏ'
 elif re.search(r'\bsenior\b',name): age='Lớn tuổi'
 elif re.search(r'\badult\b',name): age='Trưởng thành'
 elif re.search(r'\ball life stages\b|\ball ages\b',name): age='Mọi lứa tuổi'
 else: age=''
 for attr,val in [(stage,age),(weight,row.get('weight',''))]:
  if val:result.append((attr,val))
 return result
for row in data:
 veterinary='veterinary-diets' in row['source_url']
 trace={'petcare_source_url':row['source_url'], 'petcare_source_currency':row.get('source_currency',''),
        'petcare_source_price':float(row.get('source_price') or 0), 'petcare_exchange_rate':float(row.get('rate') or 0),
        'petcare_source_weight':row.get('weight',''), 'description_sale':False}
 existing=Product.search([('default_code','=',row['sku'])],limit=1)
 if existing:
  image=ROOT/'images'/row.get('local_image','')
  if row.get('local_image') and image.is_file() and not existing.image_1920:
   trace['image_1920']=base64.b64encode(image.read_bytes())
  if veterinary: trace.update({'website_published':False,'public_categ_ids':[(6,0,[vetfood.id])]})
  existing.write(trace)
  for attr,val in extra_lines(row):
   if not existing.attribute_line_ids.filtered(lambda line:line.attribute_id==attr):
    env['product.template.attribute.line'].sudo().create({'product_tmpl_id':existing.id,'attribute_id':attr.id,'value_ids':[(6,0,[value(attr,val).id])]})
  continue
 attributes=[]
 if row['species']: attributes.append((0,0,{'attribute_id':species.id,'value_ids':[(6,0,[value(species,row['species']).id])]}))
 if row['brand']: attributes.append((0,0,{'attribute_id':brand.id,'value_ids':[(6,0,[value(brand,row['brand']).id])]}))
 for attr,val in extra_lines(row): attributes.append((0,0,{'attribute_id':attr.id,'value_ids':[(6,0,[value(attr,val).id])]}))
 category_id=(vetfood if veterinary else dogdry if row['species']=='Chó' else catdry if row['species']=='Mèo' else False)
 vals={'name':row['name'],'default_code':row['sku'],'type':'consu','sale_ok':True,
       'list_price':float(row['price_vnd_estimate']),'website_published':bool(not veterinary and row['brand'] and row['species']),
       'public_categ_ids':[(6,0,[category_id.id] if category_id else [])], 'attribute_line_ids':attributes}
 vals.update(trace)
 image=ROOT/'images'/row.get('local_image','')
 if row.get('local_image') and image.is_file(): vals['image_1920']=base64.b64encode(image.read_bytes())
 Product.create(vals);created+=1
for key in ['website_sale.products_categories','website_sale.products_attributes','website_sale.filter_products_price']:
 v=env['ir.ui.view'].sudo().search([('key','=',key)],limit=1)
 if v:v.active=True
env.cr.commit()
print('IMPORTED',created,'CURRENCY',env.company.currency_id.name,'PRODUCTS',len(data))
