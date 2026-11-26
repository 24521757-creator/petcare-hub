items=env['product.template'].sudo().search([('name','=','Hạt thử nghiệm TR-10')])
items.write({'website_published':False})
env.cr.commit()
print('Đã ẩn khỏi cửa hàng:',len(items),'sản phẩm kiểm thử; dữ liệu vẫn được giữ trong Odoo')
