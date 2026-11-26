import base64
import json
import pathlib

ROOT = pathlib.Path('/mnt/extra-addons/seed_data')
data = json.loads((ROOT / 'toys.json').read_text(encoding='utf-8'))

Category = env['product.public.category'].sudo()
def category(name, parent=None):
    domain = [('name', '=', name), ('parent_id', '=', parent.id if parent else False)]
    return Category.search(domain, limit=1) or Category.create({'name': name, 'parent_id': parent.id if parent else False})

dog = category('Chó')
cat = category('Mèo')
dog_toys = category('Đồ chơi cho chó', dog)
cat_toys = category('Đồ chơi cho mèo', cat)

Attribute = env['product.attribute'].sudo()
Value = env['product.attribute.value'].sudo()
def attribute(name):
    a = Attribute.search([('name', '=', name)], limit=1)
    return a or Attribute.create({'name': name, 'create_variant': 'no_variant', 'display_type': 'multi', 'visibility': 'visible'})

species_attr = attribute('Loài thú cưng')
brand_attr = attribute('Thương hiệu')
weight_attr = attribute('Quy cách')

def attr_value(attr, name):
    v = Value.search([('attribute_id', '=', attr.id), ('name', '=', name)], limit=1)
    return v or Value.create({'attribute_id': attr.id, 'name': name})

Product = env['product.template'].sudo()
created = 0
updated = 0
with_images = 0

for row in data:
    cat_rec = dog_toys if row['species'] == 'Chó' else cat_toys
    trace = {
        'petcare_source_url': row['source_url'],
        'petcare_source_currency': row.get('source_currency', 'USD'),
        'petcare_source_price': float(row.get('source_price') or 0),
        'petcare_exchange_rate': float(row.get('rate') or 25000),
        'petcare_source_weight': row.get('weight', ''),
        'list_price': float(row['price_vnd_estimate']),
        'public_categ_ids': [(6, 0, [cat_rec.id])],
        'website_published': True,
        'sale_ok': True,
    }
    img_path = ROOT / 'images' / row.get('local_image', '')
    if img_path.is_file() and img_path.stat().st_size > 1500:
        trace['image_1920'] = base64.b64encode(img_path.read_bytes())
        with_images += 1

    existing = Product.search([('default_code', '=', row['sku'])], limit=1)
    if existing:
        existing.write(trace)
        product = existing
        updated += 1
    else:
        attributes = []
        if row.get('species'):
            attributes.append((0, 0, {'attribute_id': species_attr.id, 'value_ids': [(6, 0, [attr_value(species_attr, row['species']).id])]}))
        if row.get('brand'):
            attributes.append((0, 0, {'attribute_id': brand_attr.id, 'value_ids': [(6, 0, [attr_value(brand_attr, row['brand']).id])]}))
        if row.get('weight'):
            attributes.append((0, 0, {'attribute_id': weight_attr.id, 'value_ids': [(6, 0, [attr_value(weight_attr, row['weight']).id])]}))
        vals = {
            'name': row['name_vi'],
            'default_code': row['sku'],
            'type': 'consu',
            'attribute_line_ids': attributes,
        }
        vals.update(trace)
        product = Product.create(vals)
        created += 1

    product.update_field_translations('name', {
        'en_US': row['name'],
        'vi_VN': row['name_vi'],
    })

env.cr.commit()
print(f'TOYS_IMPORTED created={created} updated={updated} with_images={with_images}/{len(data)} dog_toys_id={dog_toys.id} cat_toys_id={cat_toys.id}')
