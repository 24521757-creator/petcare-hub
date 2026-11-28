# Bàn giao dữ liệu sản phẩm PetCare Hub (755 bản ghi đã nhập / 620 sản phẩm hiển thị)

Tài liệu này ghi nhận **đúng thực tế nguồn gốc, tệp dữ liệu thô, script nhập, bảng quy đổi và mẫu kiểm chứng từ nguồn đến Odoo** cho toàn bộ sản phẩm đang có trên PetCare Hub (CSDL sao lưu `petcare_hub_2026-11-26_01-25-44.zip`).

> **Lưu ý quan trọng về tính trung thực khi viết báo cáo:**
> Toàn bộ 620 sản phẩm đang bán trên `/shop` **không đi qua một crawler chung duy nhất**, mà gồm **3 đợt dữ liệu riêng biệt**:
> - **Đợt 1 (605 bản ghi trong `products.json`)**: gồm **600 sản phẩm gốc `origin: "lab3_600"`** (500 PetSmart + 100 Chewy) và 5 sản phẩm thức ăn khô cho mèo. Hiện trong repo **chỉ còn file dữ liệu nhập cuối cùng** (`products.json`, `ban_dich_ten.csv`) cùng script nhập vào Odoo (`import_products.py`, `apply_vietnamese.py`), **không có mã nguồn crawler gốc của đợt `lab3_600`**. Nhóm cần trình bày đúng thực tế này.
> - **Đợt 2 (50 đồ chơi trong `toys.json`)** và **Đợt 3 (100 sản phẩm mèo trong `cat_catalog_extra.json`)**: được thu thập trực tiếp từ trang danh mục thật trên **PetSmart** và **Chewy** bằng trình duyệt tự động, lưu thành JSON thô, tải & kiểm tra hợp lệ 100% ảnh bằng Pillow (`download_toy_images.py`, `download_cat_extra_images.py`), rồi nhập vào Odoo bằng `import_toys.py` và `import_cat_extra.py`.

---

## 1. Danh mục tệp bàn giao trong `addons/seed_data/`

| Loại tài liệu | Tên tệp | Nội dung |
| --- | --- | --- |
| **File Excel tổng hợp (5 sheet)** | `addons/seed_data/tong_hop_san_pham_va_bang_quy_doi.xlsx` | Tổng hợp đủ 755 bản ghi (kèm Odoo ID thực tế), bảng quy đổi danh mục, bảng thương hiệu, quy tắc quy đổi và 10 mẫu kiểm chứng từ nguồn đến Odoo. |
| **Dữ liệu thô Đợt 1** | `products.json`, `ban_dich_ten.csv` | 605 bản ghi (`lab3_600` + 5 SP mèo khô) và bảng dịch tên tiếng Việt. |
| **Dữ liệu thô Đợt 2** | `toys.json` | 50 đồ chơi (25 Chó + 25 Mèo) từ PetSmart & Chewy. |
| **Dữ liệu thô Đợt 3** | `cat_catalog_extra.json` | 100 sản phẩm mèo (35 khô + 35 ướt/pate + 30 đồ chơi mới) từ PetSmart & Chewy. |
| **Script tải ảnh & nhập Odoo** | `import_products.py`, `apply_vietnamese.py`, `download_toy_images.py`, `import_toys.py`, `download_cat_extra_images.py`, `import_cat_extra.py`, `hide_test_item.py` | Toàn bộ mã quy đổi danh mục, thuộc tính, tỷ giá 25.000 đ/USD, gán trường truy vết `petcare_source_*` và lọc sản phẩm ẩn. |

---

## 2. Bảng quy đổi Danh mục & Chó–Mèo (từ nguồn → Odoo)

| Đợt nhập | Danh mục / Nhóm nguồn | Loài | Quy tắc lọc / quy đổi | ID DM Odoo | Đường dẫn Danh mục Odoo | Tổng | Hiển thị (`/shop`) | Ẩn |
| --- | --- | --- | --- | ---: | --- | ---: | ---: | ---: |
| Đợt 1 (products.json) | Chó > Thức ăn cho chó > Thức ăn khô | Chó | Không phải veterinary-diets, đủ Thương hiệu & Loài | 5 | Chó / Thức ăn cho chó / Thức ăn khô | 465 | 465 | 0 |
| Đợt 1 (products.json) | Chó > Thức ăn cho chó > Thức ăn khô (URL chứa veterinary-diets) | Chó | URL chứa "veterinary-diets" → tự động ẩn khỏi /shop | 7 | Chó / Thức ăn cho chó / Dinh dưỡng thú y | 40 | 0 | 40 |
| Đợt 1 (products.json) | Chó > Thức ăn cho chó > Thức ăn khô (thiếu brand/species) | Chó / Trống | Thiếu brand hoặc species → nhập nháp, không đăng /shop | 5 | Chó / Thức ăn cho chó / Thức ăn khô (Chưa đăng) | 95 | 0 | 95 |
| Đợt 1 (products.json) | Mèo > Thức ăn cho mèo > Thức ăn khô / Mèo > Thức ăn khô | Mèo | Đủ Thương hiệu & Loài → đăng /shop | 6 | Mèo / Thức ăn cho mèo / Thức ăn khô | 5 | 5 | 0 |
| Đợt 2 (toys.json) | Dog Toys (PetSmart & Chewy) | Chó | species = "Chó" → đăng /shop | 10 | Chó / Đồ chơi cho chó | 25 | 25 | 0 |
| Đợt 2 (toys.json) | Cat Toys (PetSmart & Chewy) | Mèo | species = "Mèo" → đăng /shop | 11 | Mèo / Đồ chơi cho mèo | 25 | 25 | 0 |
| Đợt 3 (cat_catalog_extra.json) | Cat Dry Food (PetSmart & Chewy) | Mèo | category = "dry_food" → đăng /shop | 6 | Mèo / Thức ăn cho mèo / Thức ăn khô | 35 | 35 | 0 |
| Đợt 3 (cat_catalog_extra.json) | Cat Wet Food (PetSmart & Chewy) | Mèo | category = "wet_food" → tạo danh mục mới, đăng /shop | 17 | Mèo / Thức ăn cho mèo / Thức ăn ướt | 35 | 35 | 0 |
| Đợt 3 (cat_catalog_extra.json) | Cat Toys (PetSmart & Chewy) | Mèo | category = "toy" (lọc trùng 25 SP Đợt 2) → đăng /shop | 11 | Mèo / Đồ chơi cho mèo | 30 | 30 | 0 |
| **Tổng cộng** | | | | | | **755** | **620** | **135** |

*(Ngoài 755 bản ghi sản phẩm từ 3 đợt trên, trong Odoo còn 1 sản phẩm kiểm thử thanh toán nội bộ `Hạt thử nghiệm TR-10` đã được ẩn khỏi `/shop` qua `hide_test_item.py`.)*

---

## 3. Quy tắc quy đổi Thuộc tính, Tỷ giá & Thương hiệu

- **Loài thú cưng (`Loài thú cưng`, Attribute ID 1):** `Chó` / `Mèo` (`create_variant = no_variant`).
- **Thương hiệu (`Thương hiệu`, Attribute ID 2):** giữ nguyên tên thương hiệu chuẩn từ nguồn (**74** thương hiệu hợp lệ; ở Đợt 1 có 95 bản ghi trống thương hiệu/loài bị giữ ở trạng thái chưa đăng `website_published = False`).
  - *Top thương hiệu tiêu biểu đang hiển thị:* Royal Canin (54), Purina Pro Plan (50), Hill's Science Diet (48), Blue Buffalo (41), Simply Nourish (31), Authority (29), Wellness (24), NUTRO (22), Merrick (20), Purina ONE (20), Nulo (19), Natural Balance (16).
  - *(Xem danh sách đầy đủ toàn bộ thương hiệu trong sheet `Quy_doi_Thuong_hieu` của file Excel.)*
- **Độ tuổi (`Độ tuổi`, Attribute ID 3):**
  - Tên gốc chứa `puppy` / `kitten` → **Thú cưng nhỏ**
  - Tên gốc chứa `senior` → **Lớn tuổi**
  - Tên gốc chứa `adult` → **Trưởng thành**
  - Tên gốc chứa `all life stages` / `all ages` → **Mọi lứa tuổi**
- **Quy cách (`Quy cách`, Attribute ID 4):** giữ nguyên đơn vị khối lượng / đóng gói (`30 Lb`, `3 Oz`, `24 Lon x 3 Oz`, `Bộ 5 que`...) và lưu thêm vào `petcare_source_weight`.
- **Quy đổi giá VND:** tỷ giá cố định **25.000 VND / USD** (lưu đủ 4 trường truy vết `petcare_source_url`, `petcare_source_price`, `petcare_source_currency`, `petcare_exchange_rate` trên `product.template`).
- **Lọc sản phẩm ẩn (`website_published = False`):** 40 sản phẩm có URL chứa `veterinary-diets` (chuyển vào `Dinh dưỡng thú y`) và 95 bản ghi Đợt 1 thiếu thương hiệu/loài.

---

## 4. Kiểm chứng đối chiếu 10 sản phẩm mẫu (Từ link nguồn → Dữ liệu thô → Odoo)

| # | Đợt | SKU | Odoo ID | Nguồn | Tên tiếng Việt trên Odoo | Giá gốc (USD) | Giá Odoo (VND) | Danh mục Odoo | Trạng thái | Link nguồn gốc |
| ---: | --- | --- | ---: | --- | --- | ---: | ---: | --- | --- | --- |
| 1 | Đợt 1 | `LAB3-PETSMART-5252900` | 3 | PetSmart | Purina Pro Plan – Thức ăn khô cho chó da và dạ dày nhạy cảm Công thức cá hồi & gạo dành cho thú cưng trưởng thành Sức khỏe tiêu hóa | $77.99 | 1.949.750 ₫ | Chó / Thức ăn cho chó / Thức ăn khô | Đang hiển thị | [Xem nguồn](https://www.petsmart.com/dog/food/dry-food/purina-pro-plan-sensitive-skin-and-stomach-dry-dog-food-adult-salmon-and-rice-formula-digestive-health-36648.html) |
| 2 | Đợt 1 | `LAB3-CHEWY-1759510` | 18 | Chewy | Chewy Made – Công thức dinh dưỡng hoàn chỉnh cho gà, gạo lứt và rau củ Thức ăn khô cho chó (trước đây là hành trình Mỹ), túi 28-lb | $52.99 | 1.324.750 ₫ | Chó / Thức ăn cho chó / Thức ăn khô | Đang hiển thị | [Xem nguồn](https://www.chewy.com/chewy-made-complete-nutrition-chicken/dp/1759510) |
| 3 | Đợt 1 | `PETSMART-5154810` | 23 | PetSmart | Hill's Science Diet – Thức ăn khô cho mèo trưởng thành trong nhà - Thịt gà, 15,5 lb | $64.99 | 1.624.750 ₫ | Mèo / Thức ăn cho mèo / Thức ăn khô | Đang hiển thị | [Xem nguồn](https://www.petsmart.com/cat/food-and-treats/dry-food/hills-science-diet-indoor-adult-dry-cat-food---chicken-1390.html) |
| 4 | Đợt 1 | `LAB3-PETSMART-5206384` | 10 | PetSmart | Royal Canin Veterinary Diet – Thức ăn khô dành cho chó trưởng thành HP dành cho chó trưởng thành chứa protein thủy phân | $142.99 | 3.574.750 ₫ | Chó / Thức ăn cho chó / Dinh dưỡng thú y | Đang ẩn | [Xem nguồn](https://www.petsmart.com/dog/food/veterinary-diets/royal-canin-veterinary-diet-hydrolyzed-protein-hp-adult-dog-dry-food-2398.html) |
| 5 | Đợt 2 | `TOY-PETSMART-5381282` | 640 | PetSmart | PetSmart Charities – Thú bông đồ chơi Giáng sinh Chance & Friends cho chó | $5.00 | 125.000 ₫ | Chó / Đồ chơi cho chó | Đang hiển thị | [Xem nguồn](https://www.petsmart.com/dog/toys/plush-toys/petsmart-charities-chance-and-friends-holiday-christmas-dog-toy-wish-98236.html) |
| 6 | Đợt 2 | `TOY-CHEWY-188522` | 680 | Chewy | Frisco – Bộ 10 lò xo nhiều màu siêu đàn hồi cho mèo | $3.99 | 99.750 ₫ | Mèo / Đồ chơi cho mèo | Đang hiển thị | [Xem nguồn](https://www.chewy.com/frisco-colorful-springs-cat-toy-10/dp/188522) |
| 7 | Đợt 3 | `CAT-PS-DRY-1188` | 800 | PetSmart | Royal Canin Indoor Adult – Thức ăn khô dinh dưỡng cho mèo trưởng thành nuôi trong nhà | $23.99 | 600.000 ₫ | Mèo / Thức ăn cho mèo / Thức ăn khô | Đang hiển thị | [Xem nguồn](https://www.petsmart.com/cat/food-and-treats/dry-food/royal-canin-feline-health-indoor-adult-dry-cat-food-nutrition-1188.html) |
| 8 | Đợt 3 | `CAT-CH-DRY-112774` | 816 | Chewy | Blue Buffalo Wilderness Indoor – Thức ăn khô giàu đạm không ngũ cốc cho mèo trong nhà vị Gà (11 lb) | $44.98 | 1.125.000 ₫ | Mèo / Thức ăn cho mèo / Thức ăn khô | Đang hiển thị | [Xem nguồn](https://www.chewy.com/blue-buffalo-wilderness-indoor/dp/112774) |
| 9 | Đợt 3 | `CAT-PS-WET-12865` | 825 | PetSmart | Fancy Feast Classic Pate – Pate mềm mịn cho mèo trưởng thành (Lon lẻ 85g / 3 oz) | $0.96 | 24.000 ₫ | Mèo / Thức ăn cho mèo / Thức ăn ướt | Đang hiển thị | [Xem nguồn](https://www.petsmart.com/cat/food-and-treats/wet-food/fancy-feast-adult-classic-pate-wet-cat-food---3-oz-12865.html) |
| 10 | Đợt 3 | `CAT-CH-TOY-130264` | 881 | Chewy | Yeowww! – Quả chuối vàng nhồi 100% cỏ mèo hữu cơ siêu thơm cho mèo | $7.64 | 191.000 ₫ | Mèo / Đồ chơi cho mèo | Đang hiển thị | [Xem nguồn](https://www.chewy.com/yeowww-catnip-yellow-banana-cat-toy/dp/130264) |

Tất cả 10 mẫu đại diện đủ 3 đợt (PetSmart + Chewy, Chó + Mèo, Thức ăn khô + Thức ăn ướt + Đồ chơi + 1 mẫu `veterinary-diets` đang ẩn) đều khớp 100% giữa đường link nguồn, dữ liệu JSON thô và bản ghi thực tế trong bảng `product_template` của Odoo.
