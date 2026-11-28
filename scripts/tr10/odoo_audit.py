"""Run read-only inside `odoo shell`; never output credential values."""
import json
from urllib.parse import urlparse


def key_state(value, expected_prefix):
    if not value:
        return 'chưa cấu hình'
    return 'định dạng test' if value.startswith(expected_prefix) else 'khác định dạng test — cần kiểm tra'


def url_kind(value):
    parsed = urlparse(value or '')
    host = (parsed.hostname or '').lower()
    if not host:
        return 'chưa cấu hình'
    if host in ('localhost', '127.0.0.1', '::1'):
        return 'địa chỉ máy cục bộ'
    return 'HTTPS ngoài máy' if parsed.scheme == 'https' else 'khác HTTPS — cần kiểm tra'


def main(env):
    module = env['ir.module.module'].sudo().search([('name', '=', 'payment_stripe')], limit=1)
    providers = env['payment.provider'].sudo().search([('code', 'in', ['stripe', 'custom'])])
    data = {'co_so_du_lieu': env.cr.dbname, 'module_stripe': module.state if module else 'không tìm thấy',
            'dia_chi_co_so': url_kind(env['ir.config_parameter'].sudo().get_param('web.base.url')),
            'nha_cung_cap': []}
    for provider in providers:
        row = {'loai': provider.code, 'ten': provider.name, 'trang_thai': provider.state}
        if 'is_published' in provider._fields:
            row['hien_thi'] = bool(provider.is_published)
        if provider.code == 'stripe':
            fields = provider._fields
            row['khoa_cong_khai'] = key_state(provider.stripe_publishable_key if 'stripe_publishable_key' in fields else '', 'pk_test_')
            row['khoa_bi_mat'] = key_state(provider.stripe_secret_key if 'stripe_secret_key' in fields else '', 'sk_test_')
            row['chu_ky_webhook'] = 'đã cấu hình' if 'stripe_webhook_secret' in fields and provider.stripe_webhook_secret else 'chưa cấu hình'
        data['nha_cung_cap'].append(row)
    print(json.dumps(data, ensure_ascii=False, indent=2))


if 'env' in globals():
    main(env)
