import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('audit', Path(__file__).with_name('odoo_audit.py'))
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class AuditSafetyTests(unittest.TestCase):
    def test_key_status_never_returns_the_key(self):
        for key in ('', 'sk_test_example', 'sk_live_example'):
            result = audit.key_state(key, 'sk_test_')
            self.assertNotIn(key, result) if key else self.assertEqual(result, 'chưa cấu hình')
        self.assertEqual(audit.key_state('sk_test_example', 'sk_test_'), 'định dạng test')
        self.assertIn('cần kiểm tra', audit.key_state('sk_live_example', 'sk_test_'))

    def test_base_url_reports_category_not_full_url(self):
        self.assertEqual(audit.url_kind('http://localhost:8070'), 'địa chỉ máy cục bộ')
        self.assertEqual(audit.url_kind('https://example.test/path?token=hidden'), 'HTTPS ngoài máy')
        self.assertNotIn('hidden', audit.url_kind('https://example.test/path?token=hidden'))


if __name__ == '__main__':
    unittest.main()
