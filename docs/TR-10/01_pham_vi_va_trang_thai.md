# TR-10 — Thanh toán thử nghiệm trên Odoo 19

Tài liệu làm việc cho UC-05 / FR-003, cập nhật 28/11/2026. Đây là hướng BUY/CUSTOMIZE: sử dụng mô-đun thanh toán của Odoo, không viết lại cổng thanh toán.

## Trạng thái và bằng chứng hiện có

- COD: nhóm đã lưu ảnh cấu hình, lựa chọn COD, đơn `S00001` đã chuyển sang đơn bán và phiếu giao hàng ở trạng thái sẵn sàng. Ảnh được ghi ngày 17/11/2026; đây là **bằng chứng lịch sử**, không thay thế việc kiểm tra lại cấu hình hiện tại. Đơn COD đã xác nhận không đồng nghĩa đã thu tiền.
- Stripe: đã từng cài `payment_stripe`; trạng thái mới nhất, khóa test, webhook và các giao dịch **chưa được kiểm tra trong lượt này**. Không đánh dấu thành công hay thất bại cho tới khi có giao dịch thật trong môi trường Stripe test.
- Bản sao lưu ngày 26/11 cho thấy Stripe đang tắt và các trường khóa Stripe chưa có giá trị; COD đang bật và được đăng trên website. Đây là kết quả đọc bản sao lưu, không khẳng định trạng thái hệ thống ngày 28/11.
- Kiểm tra trực tiếp 28/11 sau khi Docker hoạt động: Stripe đã cài nhưng vẫn tắt, chưa có khóa công khai, khóa bí mật hoặc secret webhook; COD đang bật và được công bố.
- Kiểm thử COD 28/11: tạo đơn **S00010** với khách và địa chỉ ghi rõ kiểm thử, tổng **758.725 VND**. Trang hiển thị xác nhận đơn; kiểm tra Odoo ghi nhận đơn `sale`, giao dịch COD `pending`, phiếu giao `assigned`. Đây là đơn kiểm thử trên dữ liệu nhóm, không xử lý giao hàng thật; cần nhóm nhận diện khi vận hành. Trang xác nhận còn một số chuỗi tiếng Anh cần Việt hóa.
- Môi trường: ngày 28/11/2026, Docker Engine trả lỗi 500 và Odoo cổng 8070 không phản hồi trong lần kiểm tra. Không khởi động lại toàn bộ Docker khi chưa xác định ảnh hưởng tới các dịch vụ khác.
- Dữ liệu bí mật, nội dung webhook, thông tin khách, hình thẻ và bản sao cơ sở dữ liệu không đưa vào kho GitHub.

## Phạm vi

1. Đơn sản phẩm: khách kiểm tra giỏ, địa chỉ và giao hàng; chọn COD hoặc Stripe test.
2. COD: xác nhận đơn theo cấu hình Odoo; ghi nhận vẫn chờ thu tiền khi giao.
3. Stripe: giao dịch test thành công → kiểm chứng trạng thái giao dịch và đơn. Nếu bị từ chối/hủy/chưa rõ kết quả → kiểm tra trạng thái thực tế; không coi là đã thanh toán.
4. Webhook: xác thực chữ ký và đối chiếu đúng tài khoản, môi trường, mã giao dịch và đơn. Kiểm tra sự kiện trùng và tình huống quay về website đến trước/sau webhook.
5. Lịch grooming là UC-06 riêng: nhân viên duyệt trước, sau đó thanh toán; đối chiếu cách giữ chỗ/hủy/hoàn tiền với module của Phương Thùy. Không gộp mặc định đơn sản phẩm và lịch dịch vụ.

## Các phụ thuộc trước khi chạy

- Odoo/PostgreSQL đang hoạt động, có bản sao lưu và có sản phẩm/khách hàng kiểm thử.
- Trâm hoặc nhóm xác nhận có quyền truy cập tài khoản Stripe test/sandbox. Không gửi khóa qua chat hay ghi vào GitHub.
- Cấu hình khóa test trong giao diện Odoo và kiểm tra webhook tương ứng. Nếu sử dụng Stripe CLI để chuyển sự kiện về máy, secret ký của phiên CLI phải khớp cấu hình; không nhầm với signing secret của endpoint khác. Giữ CLI hoạt động khi kiểm thử.
- Đảm bảo phương thức giao hàng/COD, phương thức thẻ, quốc gia và VND phù hợp với tài khoản thử nghiệm. VND là tiền tệ không có phần thập phân trong API Stripe; khả dụng còn tùy tài khoản và quốc gia.

Odoo hỗ trợ kiểm thử với khóa test và cung cấp `payment_stripe`; webhook `/payment/stripe/webhook` được Odoo xử lý, không tự viết endpoint song song. Xem [tài liệu Odoo 19](https://www.odoo.com/documentation/19.0/applications/finance/payment_providers/stripe.html), [nguồn controller Odoo](https://github.com/odoo/odoo/blob/19.0/addons/payment_stripe/controllers/main.py), [kiểm thử Stripe](https://docs.stripe.com/testing) và [tiền tệ Stripe](https://docs.stripe.com/currencies).

Việt Nam không xuất hiện trong danh sách quốc gia/địa bàn hỗ trợ mở tài khoản thanh toán Stripe trên [trang Stripe Global](https://stripe.com/global) tại thời điểm tra cứu. Đây là vấn đề tính khả thi cần nhóm xác minh theo tài khoản cụ thể, không suy ra rằng mọi sandbox đều không thể sử dụng và không thay đổi quốc gia doanh nghiệp để né quy định.

## Đồng bộ với các bạn

- Xuân Dung / UC-01: giỏ Odoo là `sale.order` nháp; việc lọc, số lượng và giá phải chuyển đúng sang UC-05.
- Nam Hiên / UC-04: hồ sơ thú cưng thuộc khách; không dùng hồ sơ của khách khác trong UC-06.
- Phương Thùy / UC-06: thời hạn giữ suất và thanh toán là quy tắc của dịch vụ, không áp dụng mặc định cho giỏ sản phẩm.
- Nhánh mã hiện có `petcare_foundation` chứa mô hình trình diễn; cần đối chiếu với mô-đun hồ sơ và grooming chính thức của nhóm trước khi khẳng định đã kết nối thanh toán dịch vụ.
- Thảo Nhi / UC-10: đơn COD được xác nhận nhưng chưa thu tiền cần thể hiện đúng trong vận hành; trạng thái giao dịch và đơn là hai thông tin khác nhau.

Không ghi nhận TR-10 hoàn thành cho đến khi chạy và lưu minh chứng theo `02_kich_ban_kiem_thu.md`.
