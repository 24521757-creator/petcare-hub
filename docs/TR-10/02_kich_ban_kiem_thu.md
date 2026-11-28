# TR-10 — Kịch bản và minh chứng

Tất cả kịch bản bên dưới hiện **CHƯA CHẠY LẠI**. Kết quả mong đợi không phải kết quả thực tế. Dùng khách hàng, sản phẩm, đơn và thẻ thử nghiệm; không dùng thông tin thanh toán thật.

| Mã | Kịch bản | Kết quả cần đối chiếu | Trạng thái |
| --- | --- | --- | --- |
| TC-01 | Đơn sản phẩm, chọn COD, xác nhận | Đơn được xác nhận theo cấu hình; giao dịch COD và công nợ thể hiện chưa thu tiền, có phiếu giao phù hợp. | Chưa chạy lại; có ảnh lịch sử 17/11 |
| TC-02 | Stripe test, thẻ thành công | Stripe ghi nhận thành công; transaction Odoo `done`, số tiền/tiền tệ khớp; đơn `sale` sau hậu xử lý. | Chưa chạy |
| TC-03 | Stripe test, thẻ bị từ chối | Giao dịch không `done`; đơn không được xác nhận do giao dịch thất bại; ghi lại trạng thái thực tế, khách có thể thử lại hoặc đổi phương thức nếu giao diện hỗ trợ. | Chưa chạy |
| TC-04 | Khách hủy/quay lại trước khi hoàn tất | Không kết luận đã thanh toán; ghi lại trạng thái transaction/đơn thực tế và kiểm tra hành động tiếp theo. | Chưa chạy |
| TC-05 | Kiểm thử webhook: sự kiện hợp lệ và gửi lại, hoặc chữ ký sai trên môi trường cô lập | Sự kiện hợp lệ cập nhật đúng giao dịch; sự kiện lặp không tạo xác nhận/đơn trùng; chữ ký sai không làm thay đổi giao dịch. Ghi cả mã phản hồi và trạng thái. | Chưa chạy |

Ví dụ thẻ test dùng trong trang thanh toán Stripe: `4242 4242 4242 4242` cho trường hợp thành công và `4000 0000 0000 0002` cho từ chối thông thường; dùng ngày hết hạn tương lai và mã bảo mật test theo [Stripe Testing](https://docs.stripe.com/testing). Số thẻ trên là số kiểm thử công khai, không phải thẻ thật. Không đưa khóa, mã bí mật, địa chỉ khách thật hoặc toàn bộ nội dung webhook vào ảnh hay log nộp bài.

## Minh chứng cần giữ cho từng lần chạy

1. Mã test, thời gian, sản phẩm kiểm thử, số tiền và tiền tệ; trạng thái cấu hình provider (không lộ khóa).
2. Màn hình kết quả checkout và mã đơn/giao dịch; trạng thái đơn và giao dịch trong Odoo.
3. Stripe Dashboard ở môi trường test: mã PaymentIntent, trạng thái và kết quả sự kiện webhook đã che thông tin nhạy cảm.
4. Với thất bại/hủy: ảnh thông báo và trạng thái đơn; không lấy trường hợp khách rời trang làm bằng chứng chắc chắn giao dịch thất bại.
5. Với COD: thông tin thể hiện phương thức thu hộ, đơn được xác nhận và khoản tiền chưa thu; đối chiếu phiếu giao nếu có.

Lưu ảnh vào thư mục Drive TR-10 của Trâm; cập nhật mục 5.3 và 5.5 sau khi chạy. Không dùng sự kiện giả do `stripe trigger` tạo độc lập làm bằng chứng rằng đơn Odoo cụ thể đã nhận webhook: cần sự kiện khớp giao dịch và tham chiếu Odoo.
