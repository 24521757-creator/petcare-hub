from datetime import date
import math
from odoo import http, fields
from odoo.http import request
from werkzeug.exceptions import BadRequest

class PetcareWebsite(http.Controller):
    def _pet_values(self, data):
        name=data.get('name','').strip(); species=data.get('species','')
        if not name or species not in ('dog','cat'): raise BadRequest('Vui lòng nhập tên và chọn chó hoặc mèo.')
        try:
            weight=float(data.get('weight') or 0)
            birthday=date.fromisoformat(data['birth_date']) if data.get('birth_date') else False
            if not math.isfinite(weight) or weight < 0 or weight > 200 or (birthday and birthday > date.today()): raise ValueError()
        except (ValueError, TypeError): raise BadRequest('Ngày sinh hoặc cân nặng không hợp lệ.')
        return {'name':name[:100], 'species':species, 'breed':data.get('breed','').strip()[:100],
                'weight':weight, 'birth_date':birthday, 'notes':data.get('notes','').strip()[:2000]}

    @http.route('/petcare', type='http', auth='public', website=True, sitemap=True)
    def home(self, **kw):
        return request.render('petcare_foundation.home', {})

    @http.route('/petcare/pets', type='http', auth='user', website=True)
    def pets(self, **kw):
        pets = request.env['petcare.demo.pet'].sudo().search([('owner_id','=',request.env.user.partner_id.id)])
        return request.render('petcare_foundation.pets', {'pets': pets})

    @http.route('/petcare/pets/add', type='http', auth='user', website=True, methods=['POST'])
    def pet_add(self, **kw):
        vals=self._pet_values(kw); vals['owner_id']=request.env.user.partner_id.id
        request.env['petcare.demo.pet'].sudo().create(vals)
        return request.redirect('/petcare/pets')

    @http.route('/petcare/pets/<int:pet_id>/edit', type='http', auth='user', website=True, methods=['POST'])
    def pet_edit(self, pet_id, **kw):
        pet=request.env['petcare.demo.pet'].sudo().search([('id','=',pet_id),('owner_id','=',request.env.user.partner_id.id)],limit=1)
        if not pet: raise BadRequest('Không tìm thấy hồ sơ thú cưng.')
        pet.write(self._pet_values(kw))
        return request.redirect('/petcare/pets')

    @http.route('/petcare/services', type='http', auth='public', website=True)
    def services(self, **kw):
        services = request.env['petcare.demo.service'].sudo().search([])
        return request.render('petcare_foundation.services', {'services':services})

    @http.route('/petcare/booking', type='http', auth='user', website=True)
    def booking(self, **kw):
        partner = request.env.user.partner_id
        try:
            selected_service_id = int(kw.get('service_id') or 0)
        except (ValueError, TypeError):
            selected_service_id = 0
        return request.render('petcare_foundation.booking', {
            'pets':request.env['petcare.demo.pet'].sudo().search([('owner_id','=',partner.id)]),
            'services':request.env['petcare.demo.service'].sudo().search([]),
            'slots':request.env['petcare.demo.slot'].sudo().search([('start_at','>',fields.Datetime.now())]),
            'bookings':request.env['petcare.demo.booking'].sudo().search([('owner_id','=',partner.id)], limit=20),
            'error':kw.get('error',''),
            'selected_service_id': selected_service_id,
        })

    @http.route('/petcare/booking/add', type='http', auth='user', website=True, methods=['POST'])
    def booking_add(self, pet_id='', service_id='', slot_id='', **kw):
        try: pet_id, service_id, slot_id = map(int, (pet_id, service_id, slot_id))
        except (ValueError, TypeError): raise BadRequest('Thông tin đặt lịch không hợp lệ.')
        env = request.env
        pet = env['petcare.demo.pet'].sudo().search([('id','=',pet_id),('owner_id','=',env.user.partner_id.id)],limit=1)
        service = env['petcare.demo.service'].sudo().search([('id','=',service_id)],limit=1)
        slot = env['petcare.demo.slot'].sudo().search([('id','=',slot_id),('start_at','>',fields.Datetime.now())],limit=1)
        if not (pet and service and slot): raise BadRequest('Không tìm thấy thông tin hợp lệ.')
        env.cr.execute('UPDATE petcare_demo_slot SET reserved = reserved + 1 WHERE id = %s AND reserved < capacity RETURNING id', [slot.id])
        if not env.cr.fetchone():
            return request.redirect('/petcare/booking?error=full')
        env['petcare.demo.booking'].sudo().create({'owner_id':env.user.partner_id.id, 'pet_id':pet.id, 'service_id':service.id, 'slot_id':slot.id})
        return request.redirect('/petcare/booking')

    @http.route('/petcare/wishlist/toggle', type='jsonrpc', auth='public', website=True)
    def wishlist_toggle(self, product_id=0, **kw):
        try:
            product_id = int(product_id)
        except (ValueError, TypeError):
            return {'in_wish': False, 'count': 0}
        product = request.env['product.product'].sudo().browse(product_id).exists()
        if not product:
            return {'in_wish': False, 'count': 0}
        Wishlist = request.env['product.wishlist']
        current_wishes = Wishlist.current()
        existing = current_wishes.filtered(lambda w: w.product_id.id == product.id)
        if existing:
            if request.website.is_public_user():
                wish_ids = list(request.session.get('wishlist_ids') or [])
                for w in existing:
                    if w.id in wish_ids:
                        wish_ids.remove(w.id)
                request.session['wishlist_ids'] = wish_ids
                request.session.touch()
                existing.sudo().unlink()
            else:
                existing.unlink()
            in_wish = False
        else:
            price = product._get_combination_info_variant()['price']
            if request.website.is_public_user():
                partner_id = False
                wish = Wishlist.sudo()._add_to_wishlist(
                    request.pricelist.id,
                    request.website.currency_id.id,
                    request.website.id,
                    price,
                    product.id,
                    partner_id,
                )
                request.session['wishlist_ids'] = list(request.session.get('wishlist_ids') or []) + [wish.id]
                request.session.touch()
            else:
                partner_id = request.env.user.partner_id.id
                Wishlist._add_to_wishlist(
                    request.pricelist.id,
                    request.website.currency_id.id,
                    request.website.id,
                    price,
                    product.id,
                    partner_id,
                )
            in_wish = True
        count = len(Wishlist.current())
        return {'in_wish': in_wish, 'count': count}

    @http.route('/petcare/cart/quick_add', type='jsonrpc', auth='public', website=True)
    def cart_quick_add(self, product_id=0, product_template_id=0, quantity=1, **kw):
        try:
            product_id = int(product_id or 0)
            product_template_id = int(product_template_id or 0)
            quantity = max(1, int(quantity or 1))
        except (ValueError, TypeError):
            return {'ok': False, 'cart_quantity': 0}

        Product = request.env['product.product'].sudo()
        product = Product.browse(product_id).exists() if product_id else Product
        if not product and product_template_id:
            tmpl = request.env['product.template'].sudo().browse(product_template_id).exists()
            if tmpl:
                product = tmpl.product_variant_id or tmpl._create_first_product_variant()
        if not product:
            return {'ok': False, 'cart_quantity': 0}

        order_sudo = request.cart or request.website._create_cart()
        order_sudo.with_context(skip_cart_verification=True)._cart_add(
            product_id=product.id,
            quantity=quantity,
        )
        order_sudo._verify_cart_after_update()
        qty = int(order_sudo.cart_quantity or 0)
        request.session['website_sale_cart_quantity'] = qty
        request.session.touch()
        return {
            'ok': True,
            'cart_quantity': qty,
            'product_name': product.display_name,
        }
