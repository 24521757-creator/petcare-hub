# TR-10 — Kịch bản và minh chứng

Đã kiểm tra ngày 28–29/11/2026. TC-01 đến TC-03 chạy qua giao diện; TC-04 kiểm tra quay về giỏ và hủy PaymentIntent qua API test; TC-05 dùng webhook thật chuyển tiếp bằng Stripe CLI cùng phép thử phát lại có chữ ký tạo cục bộ. Xem kết quả thực tế và giới hạn ở `04_ket_qua_28112026.md`.

| Mã | Kịch bản | Kết quả cần đối chiếu | Trạng thái |
| --- | --- | --- | --- |
| TC-01 | Đơn sản phẩm, chọn COD, xác nhận | Đơn được xác nhận theo cấu hình; giao dịch COD và công nợ thể hiện chưa thu tiền, có phiếu giao phù hợp. | Đạt phần checkout: S00010, 758.725 VND, đơn sale, transaction pending, phiếu giao assigned. Chưa kiểm tra hóa đơn/công nợ kế toán. |
| TC-02 | Stripe test, thẻ thành công | Stripe ghi nhận thành công; transaction Odoo `done`, số tiền/tiền tệ khớp; đơn `sale` sau hậu xử lý. | Đạt: S00011, 758.725 VND; Stripe succeeded, Odoo done/sale; webhook HTTP 200. |
| TC-03 | Stripe test, thẻ bị từ chối | Giao dịch không `done`; đơn không được xác nhận do giao dịch thất bại; ghi lại trạng thái thực tế, khách có thể thử lại hoặc đổi phương thức nếu giao diện hỗ trợ. | Đạt: S00012; thông báo từ chối, Odoo error/draft, không có phiếu giao; webhook HTTP 200. |
| TC-04 | Quay về giỏ và hủy PaymentIntent qua API test | Không kết luận đã thanh toán; ghi lại trạng thái transaction/đơn thực tế và kiểm tra hành động tiếp theo. | Đạt phạm vi kiểm tra: quay lại giỏ sau từ chối; giao dịch TR10-CANCEL-S00012 nhận webhook canceled và thành cancel, đơn vẫn draft. Hủy qua API, không phải nút hủy checkout. |
| TC-05 | Kiểm thử webhook thật và phát lại sự kiện | Sự kiện hợp lệ cập nhật đúng giao dịch; sự kiện lặp không tạo xác nhận/đơn trùng; chữ ký sai không làm thay đổi giao dịch. | Đạt: webhook thật HTTP 200; phát lại sự kiện thật hai lần với chữ ký test tạo cục bộ HTTP 200/200, chữ ký sai HTTP 403; trạng thái và số lượng bản ghi không đổi. |

Ví dụ thẻ test dùng trong trang thanh toán Stripe: `4242 4242 4242 4242` cho trường hợp thành công và `4000 0000 0000 0002` cho từ chối thông thường; dùng ngày hết hạn tương lai và mã bảo mật test theo [Stripe Testing](https://docs.stripe.com/testing). Số thẻ trên là số kiểm thử công khai, không phải thẻ thật. Không đưa khóa, mã bí mật, địa chỉ khách thật hoặc toàn bộ nội dung webhook vào ảnh hay log nộp bài.

## Minh chứng cần giữ cho từng lần chạy

1. Mã test, thời gian, sản phẩm kiểm thử, số tiền và tiền tệ; trạng thái cấu hình provider (không lộ khóa).
2. Màn hình kết quả checkout và mã đơn/giao dịch; trạng thái đơn và giao dịch trong Odoo.
3. Stripe Dashboard ở môi trường test: mã PaymentIntent, trạng thái và kết quả sự kiện webhook đã che thông tin nhạy cảm.
4. Với thất bại/hủy: ảnh thông báo và trạng thái đơn; không lấy trường hợp khách rời trang làm bằng chứng chắc chắn giao dịch thất bại.
5. Với COD: thông tin thể hiện phương thức thu hộ, đơn được xác nhận và khoản tiền chưa thu; đối chiếu phiếu giao nếu có.

Lưu ảnh vào thư mục Drive TR-10 của Trâm; cập nhật mục 5.3 và 5.5 sau khi chạy. Không dùng sự kiện giả do `stripe trigger` tạo độc lập làm bằng chứng rằng đơn Odoo cụ thể đã nhận webhook: cần sự kiện khớp giao dịch và tham chiếu Odoo.
