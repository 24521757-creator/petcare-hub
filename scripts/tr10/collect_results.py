"""Read only. Run in Odoo shell; emits only the named TR-10 test records."""
import json
from datetime import datetime, timezone

p = env['payment.provider'].search([('code', '=', 'stripe')], limit=1)
assert p.state == 'test'
references = ['S00010', 'S00011', 'S00012', 'TR10-CANCEL-S00012']
rows = []
for ref in references:
    tx = env['payment.transaction'].search([('reference', '=', ref)], limit=1)
    assert tx, ref
    row = {'reference': ref, 'provider': tx.provider_code, 'state': tx.state,
           'amount': tx.amount, 'currency': tx.currency_id.name,
           'orders': [{'reference': o.name, 'state': o.state,
                       'picking_count': len(o.picking_ids)} for o in tx.sale_order_ids]}
    if tx.provider_code == 'stripe':
        intent = p._send_api_request('GET', 'payment_intents/' + tx.provider_reference)
        assert intent['livemode'] is False
        row['stripe'] = {k: intent[k] for k in ['id', 'status', 'amount', 'currency', 'livemode']}
    rows.append(row)
assert [r['state'] for r in rows] == ['pending', 'done', 'error', 'cancel']
assert rows[1]['orders'][0]['state'] == 'sale'
assert rows[2]['orders'][0]['state'] == rows[3]['orders'][0]['state'] == 'draft'
print(json.dumps({'recorded_at_utc': datetime.now(timezone.utc).isoformat(),
                  'provider_mode': p.state, 'transactions': rows}, ensure_ascii=False, indent=2))
