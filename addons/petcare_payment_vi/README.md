# Thanh toán tiếng Việt

Mô-đun giao diện cho Odoo 19, kế thừa các mẫu `website_sale`; không thay đổi tính tiền, xác nhận đơn hoặc xử lý Stripe.

Sao chép thư mục vào addons đang được Odoo sử dụng rồi cài `petcare_payment_vi`. Cập nhật mô-đun sau khi thay đổi XML. Đã cài và kiểm tra trên cơ sở dữ liệu nhóm ngày 28/11/2026. Có thể gỡ mô-đun để bỏ phần kế thừa giao diện.

Thông báo COD nằm trong dữ liệu nhà cung cấp thanh toán, được cấu hình riêng tại Odoo: “Nhân viên giao hàng sẽ thu tiền khi giao hàng. Đơn hàng chưa được thanh toán.” Mô-đun không ghi đè cấu hình nhà cung cấp khi cài hoặc gỡ.
