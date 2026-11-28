# TR-10 — Chạy kiểm tra cấu hình an toàn

Mở PowerShell tại thư mục có `compose.yaml`. Kiểm tra Docker và ứng dụng trước:

```powershell
docker version
docker compose ps
```

Khi các dịch vụ Odoo và PostgreSQL đã chạy, chạy script chỉ đọc:

```powershell
Get-Content -Raw -Encoding UTF8 .\scripts\tr10\odoo_audit.py | docker exec -i petcare_odoo sh -c 'odoo shell --db_host="$HOST" --db_user="$USER" --db_password="$PASSWORD" -d petcare_hub --no-http --max-cron-threads=0'
```

Script không in giá trị khóa; nó chỉ cho biết từng trường có được thiết lập và có dạng test hay không. Không dán đầu ra có dữ liệu cá nhân, khóa hay đường dẫn chứa token lên GitHub. Script **không** thực hiện thanh toán hoặc chứng minh webhook hoạt động. Muốn xác nhận TR-10 cần chạy các ca thực tế trong tài liệu kịch bản.

Nếu dùng Stripe CLI, đăng nhập bằng trình duyệt theo hướng dẫn chính thức và dùng `stripe listen --forward-to localhost:8070/payment/stripe/webhook` trong phiên kiểm thử. CLI in signing secret cho phiên lắng nghe: nhập trực tiếp vào cấu hình Stripe của Odoo, không chia sẻ hoặc commit. Chi tiết xem [Stripe CLI](https://docs.stripe.com/stripe-cli/use-cli) và [Stripe webhook](https://docs.stripe.com/webhooks). Việc chuyển tiếp bằng CLI cần được mô tả trung thực là chuyển tiếp sự kiện test, không phải một HTTPS tunnel công khai. Nếu nhóm bắt buộc dùng tunnel công khai, cấu hình riêng theo lựa chọn của nhóm và kiểm tra URL/secret khớp nhau.

Sau khi dùng test mode, kiểm tra lại provider không được chuyển sang live. Không sửa `web.base.url` hoặc `proxy_mode` trên hệ thống dùng chung khi chưa kiểm tra tác động tới đăng nhập, liên kết và luồng của các bạn.

## Chạy lại listener cho buổi demo

Đã bổ sung `scripts/tr10/Start-Tr10Webhook.ps1`. Cần Docker/Odoo hoạt động, Stripe đã cấu hình khóa test và cài Stripe CLI từ nguồn chính thức. Chạy từ thư mục gốc kho mã:

```powershell
.\scripts\tr10\Start-Tr10Webhook.ps1
```

Nếu CLI chưa nằm trong PATH, thêm `-StripePath 'đường-dẫn-đến-stripe.exe'`. Bản CLI đã dùng để kiểm thử là 1.55.15; bản tạm trên máy triển khai nằm ở `%LOCALAPPDATA%\Temp\petcare-stripe-cli\stripe.exe` và có thể bị Windows dọn. Cần cài lại từ [Stripe CLI chính thức](https://docs.stripe.com/cli) nếu không còn tệp.

Script chỉ đọc khóa Stripe test từ Odoo vào bộ nhớ, đồng bộ signing secret khi listener mở, không in hoặc ghi khóa ra tệp. Dừng bằng Ctrl+C sau buổi demo; đóng listener thì đường chuyển tiếp ngừng hoạt động. Script đã được chạy kiểm tra khởi động và đồng bộ secret; các ca giao dịch được chạy với cùng phương thức chuyển tiếp Stripe CLI.

`collect_results.py` và `verify_webhook_replay.py` là các script kiểm tra dành cho bộ hồ sơ TR-10 đã ghi nhận. Script replay có mã sự kiện/giao dịch cụ thể; khi chạy trên cơ sở dữ liệu hoặc tài khoản khác, phải tạo test mới và thay các tham chiếu tương ứng, không coi thiếu dữ liệu là lỗi nghiệp vụ.
