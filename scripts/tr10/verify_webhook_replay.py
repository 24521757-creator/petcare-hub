"""Run in Odoo shell after the documented TR-10 checkout tests.

Replays a REAL test event with a locally generated test signature, twice.
This is an integration test, not a substitute for Stripe delivery evidence.
Never prints event payloads, API keys, client secrets, or signing secrets.
"""
import hashlib
import hmac
import json
import time
import requests

provider = env['payment.provider'].search([('code', '=', 'stripe')], limit=1)
assert provider.state == 'test' and provider.stripe_secret_key.startswith('sk_test_')
tx = env['payment.transaction'].search([('reference', '=', 'S00011')], limit=1)
assert tx.provider_id == provider and tx.state == 'done'
event_id = 'evt_3UgoufGhutUmVwA70YOVXKmx'
event = provider._send_api_request('GET', 'events/' + event_id)
assert event['livemode'] is False
assert event['type'] == 'payment_intent.succeeded'
assert event['data']['object']['id'] == tx.provider_reference
assert event['data']['object']['description'] == tx.reference
assert event['data']['object']['currency'] == 'vnd'
assert event['data']['object']['amount'] == int(tx.amount)
payload = json.dumps(event, separators=(',', ':')).encode()
stamp = str(int(time.time()))
secret = provider.stripe_webhook_secret
assert secret.startswith('whsec_')
digest = hmac.new(secret.encode(), stamp.encode() + b'.' + payload, hashlib.sha256).hexdigest()

def snapshot():
    env.invalidate_all()
    return {
        'transaction': tx.state,
        'orders': [(o.name, o.state, len(o.picking_ids), len(o.invoice_ids)) for o in tx.sale_order_ids],
        'matching_transactions': env['payment.transaction'].search_count([('reference', '=', tx.reference)]),
    }

before = snapshot()
codes = []
for signature in ('invalid', digest, digest):
    response = requests.post(
        'http://127.0.0.1:8069/payment/stripe/webhook', data=payload,
        headers={'Content-Type': 'application/json', 'Stripe-Signature': f't={stamp},v1={signature}'},
        timeout=30,
    )
    codes.append(response.status_code)
    assert snapshot() == before, 'State/count changed during replay'
assert codes == [403, 200, 200], codes
print(json.dumps({'event_id': event_id, 'signature_invalid_http': codes[0],
                  'valid_replays_http': codes[1:], 'state_unchanged': True,
                  'verified_state': before}, ensure_ascii=False, indent=2))
