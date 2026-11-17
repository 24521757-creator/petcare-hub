# petcare-hub
Đồ án EC312 — PETCARE HUB: Website B2C bán sản phẩm và đặt lịch grooming thú cưng, dùng Odoo 19 Community theo hướng BUY/CUSTOMIZE.

## Đặt file vào đâu?

| Thư mục / file | Nội dung |
| --- | --- |
| `addons/petcare_pet_profile/` | Module hồ sơ thú cưng của Nam Hiên. |
| `addons/petcare_grooming/` | Module đặt lịch grooming của Phương Thùy. |
| `diagrams/00_chung/` | Use Case tổng, kiến trúc, ERD và Class tổng thể. |
| `diagrams/UC01/` | Sơ đồ tìm kiếm, lọc sản phẩm và giỏ hàng. |
| `diagrams/UC04/` | Sơ đồ hồ sơ thú cưng. |
| `diagrams/UC05/` | Sơ đồ đặt hàng và thanh toán. |
| `diagrams/UC06/` | Sơ đồ đặt lịch và duyệt lịch grooming. |
| `diagrams/UC10/` | Sơ đồ quản trị và AI gợi ý. |
| `data/` | CSV sản phẩm, dịch vụ và dữ liệu mẫu giả lập. |
| `docs/` | Tài liệu kỹ thuật và liên kết Figma, báo cáo, Master Plan trên Drive. |
| `compose.yaml` | Cấu hình Docker dùng chung. |
| `.env.example` | Mẫu cấu hình máy cá nhân. Sao chép thành `.env` rồi điền giá trị riêng. |

Các thư mục module đang là chỗ để nộp code, chưa có chức năng được lập trình.

## Ai làm nhánh nào?

| Nhánh | Người phụ trách | Bỏ gì vào? |
| --- | --- | --- |
| `main` | Phương Thùy và Thùy Trâm tích hợp | Bản chung đã được duyệt. |
| `codex/goi1-san-pham-gio-hang` | Xuân Dung | `diagrams/UC01/`, CSV sản phẩm trong `data/`, ghi chép cấu hình cửa hàng trong `docs/`. |
| `codex/goi2-thanh-toan` | Thùy Trâm | `diagrams/UC05/`, Docker, hướng dẫn sandbox và webhook trong `docs/`. |
| `codex/goi3-ho-so-thu-cung` | Nam Hiên | `addons/petcare_pet_profile/`, `diagrams/UC04/`. |
| `codex/goi4-grooming` | Phương Thùy | `addons/petcare_grooming/`, `diagrams/UC06/`, ERD chung. |
| `codex/goi5-quan-tri-ai` | Thảo Nhi | `diagrams/UC10/`, kiến trúc chung, code AI và tài liệu quản trị. Thống nhất với Hiên/Thùy trước khi sửa module chung. |

Trước khi làm, cập nhật `main` và ghép các thay đổi mới vào nhánh của mình. Xong một việc thì commit, push và mở Pull Request vào `main`. Ghi mã việc trong tiêu đề, ví dụ `NH-08: thêm hồ sơ thú cưng`. Lead hoặc người được giao duyệt kiểm tra rồi merge. Giữ nhánh gói việc để tiếp tục các việc sau.

Sơ đồ nộp cả `.puml` và `.png` cùng tên, ví dụ `activity_UC04.puml` và `activity_UC04.png`.

## Chạy Odoo trên máy cá nhân

Đây là bộ cấu hình Docker chính thức của nhóm (thay cho file zip cũ trên Drive). Mở Docker Desktop, tại thư mục repo dùng PowerShell:

```powershell
Copy-Item .env.example .env
notepad .env                 # đổi PG_PASSWORD
notepad config\odoo.conf     # đổi admin_passwd (Master Password)
git update-index --skip-worktree config/odoo.conf   # để không lỡ commit mật khẩu thật
docker compose up -d
```

Đổi hai mật khẩu trước lần chạy đầu: PostgreSQL chỉ nhận mật khẩu lúc tạo CSDL lần đầu.

Sau đó mở `http://localhost:8070/web/database/manager`, chọn **Restore Database**, chọn file sao lưu `petcare_hub_*.zip` mới nhất trong thư mục `04_Odoo Demo` trên Drive, đặt tên CSDL là `petcare_hub` và chọn *This database is a copy*. Cấu hình chỉ cho phép CSDL tên `petcare_hub` (`dbfilter`).

Máy đã chạy bản zip cũ: chạy `docker compose down` (không có `-v`) trong thư mục cũ, rồi `docker compose up -d` trong repo. Tên project, container và volume giống nhau nên dữ liệu được giữ nguyên.

`proxy_mode` đã bật để nhận webhook Stripe qua đường hầm (TR-10). Cổng 8070 chỉ mở trên máy mình (127.0.0.1).

## Dữ liệu và cấu hình Odoo

Code và file `.puml` đồng bộ qua GitHub. Thao tác nhập sản phẩm, cấu hình thanh toán và sửa website trực tiếp trong Odoo được lưu trong CSDL. Người làm cấu hình ghi lại các bước trong `docs/` và xuất CSV mẫu vào `data/` khi phù hợp. Lead và Thùy Trâm quản lý bản demo tích hợp, sao lưu CSDL kèm tệp đính kèm lên Drive trước các lần tích hợp lớn.

Mật khẩu, API key, webhook secret và `.env` thật lưu trên từng máy. Dùng dữ liệu giả lập trong repo. Video và bản sao lưu CSDL lưu trên Drive có phân quyền.
