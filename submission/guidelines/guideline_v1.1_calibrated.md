# Label contract — Phố châu Á — BỔ SUNG v1.1 — 03262 - Phạm Văn Ngọc Vinh

> **Chỉ viết phần thay đổi so với v1.0** (không copy cả file). Chốt các câu hỏi mở ở mục 6 của v1.0 và thêm quy tắc mới rút ra từ lỗi của máy / lỗi của bạn. Mỗi ca khó **có ảnh ví dụ** (`img_0xx`) và khớp một dòng trong `qc/calibration_decisions.csv`.

## 1. Câu hỏi mở đã chốt (từ mục 6 của v1.0)

| # | Câu hỏi | Quyết định | Ảnh ví dụ | `case_id` |
|---|---|---|---|---|
| 1 | Xe đạp điện / xe máy điện nhỏ: `bicycle` hay `motorbike`? | Xe có bàn đạp phụ trợ vận tốc thấp tính là `bicycle`; xe máy điện kiểu dáng scooter không bàn đạp luôn tính là `motorbike`. | `img_011.jpg` | CAL-05 |
| 2 | Khối xe máy đỗ dày đặc gần camera: từng xe hay `ignore_region`? | Xe nhìn rõ được trên 20% thân xe thì bắt buộc gán riêng từng `motorbike`; chỉ những xe bị che khuất > 80% hoặc nằm xa có chiều cao < 20px mới gộp vào `ignore_region`. | `img_018.jpg` | CAL-04 |
| 3 | Hàng nhô ra: xe đạp / ba gác chở hàng cồng kềnh, box xe có gồm hàng không? | Hàng hóa gắn cố định trên giá đèo hoặc trong giỏ thì tính trọn vào box xe; nếu là hàng nhô dài tự do (thanh tre, cọc sắt > 20% chiều dài xe) thì box chỉ bao trọn thân xe và giỏ cố định. | `img_008.jpg` | CAL-02 |
| 4 | Người ngồi trong xe ba bánh có mui che: tính thế nào? | Nếu nhìn thấy từ 20% phần thân người (đầu, vai, tay qua cửa hở) thì bắt buộc vẽ thêm 1 box `person` riêng chồng lên xe. | `img_013.jpg` | CAL-06 |
| 5 | Kính chắn gió / cửa sổ xe: thuộc mask xe hay không? | Kính chắn gió và cửa kính xe thuộc mask của xe, bất kể có thể nhìn xuyên thấu vào nội thất hay người ngồi bên trong. | `img_012.jpg` | CAL-07 |

## 2. Ca khó mới (từ lỗi của máy, bẫy lọt, box `can_review`)

| Ảnh | Tình huống | Máy làm gì (model nào) | Quyết định của bạn | Quy tắc mới (vào mục nào của v1.0) |
|---|---|---|---|---|
| `img_001.jpg` | Xích lô du lịch chở khách có mái che vòm | YOLO26m nhận nhầm thành `truck` do mui xe to và cồng kềnh | Gán `three_wheeler` cho toàn bộ xích lô; vẽ 2 box `person` cho người đạp và khách ngồi | Bổ sung mục 2: Mọi xe ba bánh chở khách/hàng (xích lô, cyclo, tuk-tuk) luôn thuộc `three_wheeler`. |
| `img_034.jpg` | Xe máy di chuyển ở phía xa bị bỏ sót (bẫy missing) | Máy bỏ sót hoàn toàn xe máy ở hậu cảnh; reviewer bị thiên kiến tự động hoá | Tắt layer máy để quét ảnh trắng; bổ sung box `motorbike` | Bổ sung mục 4.1: Bắt buộc tắt nhãn máy để quét ảnh gốc trước; đối tượng cao $\ge 20$px phải được gán đủ. |
| `img_014.jpg` | Xe máy bị máy vẽ box lỏng mở rộng ra vỉa hè (bẫy loose) | YOLO26 vẽ box mở rộng lấn sang lề đường | Thu hẹp box lại sát mép bánh xe và tay lái | Bổ sung mục 4.1.1: Box phải tiếp xúc 4 điểm ngoài cùng của vật thể, sai số $\le 2$px. |
| `img_027.jpg` | Hình ảnh người trên biển quảng cáo / phản chiếu cửa kính | YOLO26 nhận nhầm thành `person` | Xóa bỏ box nhận diện sai | Bổ sung mục 2: Tuyệt đối không gán người trong tranh ảnh, biển quảng cáo, ma-nơ-canh hoặc phản chiếu. |

## 3. Lịch sử thay đổi

| Phiên bản | Thay đổi | Lý do (ca nào, `case_id`) |
|---|---|---|
| v1.0 | Bản guideline gốc giảng viên viết sẵn | Bắt đầu bài lab |
| v1.1 | Chốt 5 câu hỏi mở (xe điện, hàng cồng kềnh, kính xe, mui xe); chuẩn hóa quy tắc phân tách người và xe ba bánh; đưa checklist tắt nhãn máy chống bỏ sót vào quy trình duyệt | Khắc phục lỗi YOLO26 nhầm xích lô thành truck (`img_001.jpg`, CAL-01); xử lý bẫy lọt missing (`img_034.jpg`, CAL-03); làm rõ câu hỏi mở hàng hóa (`img_008.jpg`, CAL-02) và cụm xe đông đúc (`img_018.jpg`, CAL-04) |
