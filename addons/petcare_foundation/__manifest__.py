{
    'name': 'PetCare Hub - Cửa hàng và dịch vụ',
    'version': '19.0.1.0.0',
    'depends': ['website_sale', 'website_sale_wishlist', 'portal'],
    'data': ['security/ir.model.access.csv', 'views/pages.xml', 'views/backend.xml'],
    'assets': {'web.assets_frontend': ['petcare_foundation/static/src/css/pastel.css', 'petcare_foundation/static/src/js/petcare.js']},
    'installable': True,
    'license': 'LGPL-3',
}
