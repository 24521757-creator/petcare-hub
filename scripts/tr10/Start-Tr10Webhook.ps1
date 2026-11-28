param(
    [string]$StripePath = 'stripe',
    [string]$Container = 'petcare_odoo'
)
$ErrorActionPreference = 'Stop'
$odooCommand = 'odoo shell --db_host="$HOST" --db_user="$USER" --db_password="$PASSWORD" -d petcare_hub --no-http --max-cron-threads=0 --log-level=error'
$readKey = @'
p=env['payment.provider'].search([('code','=','stripe')],limit=1)
assert p.state=='test' and p.stripe_secret_key.startswith('sk_test_'), 'Chỉ hỗ trợ Stripe test'
print(p.stripe_secret_key)
'@
# Capture the key in memory; never echo it or save it to disk.
$lines = $readKey | docker exec -i $Container sh -c $odooCommand
if ($LASTEXITCODE -ne 0) { throw 'Không đọc được cấu hình Stripe test từ Odoo.' }
$keys = @($lines | Where-Object { $_ -match '^sk_test_[A-Za-z0-9]+$' })
if ($keys.Count -ne 1) { throw 'Không tìm thấy đúng một khóa test.' }
$previousKey = $env:STRIPE_API_KEY
$previousWebhook = $env:TR10_WEBHOOK_SECRET
try {
    $env:STRIPE_API_KEY = $keys[0]
    & $StripePath listen --events payment_intent.processing,payment_intent.amount_capturable_updated,payment_intent.succeeded,payment_intent.payment_failed,payment_intent.canceled --forward-to http://localhost:8070/payment/stripe/webhook --device-name petcare-tr10-test --color off 2>&1 | ForEach-Object {
        $line = $_.ToString()
        if ($line -match '(whsec_[A-Za-z0-9]+)') {
            $env:TR10_WEBHOOK_SECRET = $Matches[1]
            $update = @'
import os
p=env['payment.provider'].search([('code','=','stripe')],limit=1)
assert p.state=='test'
s=os.environ['TR10_WEBHOOK_SECRET']
assert s.startswith('whsec_')
p.stripe_webhook_secret=s
env.cr.commit()
print('Đã đồng bộ signing secret cho phiên webhook test.')
'@
            $update | docker exec -i --env TR10_WEBHOOK_SECRET $Container sh -c $odooCommand
            if ($LASTEXITCODE -ne 0) { throw 'Không đồng bộ được webhook secret.' }
        } else {
            Write-Output $line
        }
    }
} finally {
    $env:STRIPE_API_KEY = $previousKey
    $env:TR10_WEBHOOK_SECRET = $previousWebhook
    $keys = $null
    $lines = $null
    Write-Output 'Đã kết thúc listener; cần chạy lại trước lần demo tiếp theo.'
}
