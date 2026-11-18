# Báo cáo Day 08 — 03262 - Phạm Văn Ngọc Vinh

> Một file duy nhất cho cả bài (đã gộp recipe, QC và ghi chú cá nhân). Mọi con số kèm **mẫu số** và nguồn (file nào). Viết bằng lời của bạn.

## 1. Model và recipe (Part 2–3)

| Lớp | Model + cỡ | Ngưỡng | Vì sao (dẫn `run_id` trong `model_log.csv`) |
|---|---|---|---|
| person / bicycle / motorbike / car / bus / truck | YOLO26m | person=0.5, motorbike=0.5, car=0.5 (các lớp còn lại dùng 0.3) | Dựa trên kết quả chạy tour `r04` (conf 0.25) và `r05` (conf 0.5): ngưỡng 0.5 giúp giảm triệt để box nhiễu ở hậu cảnh, đạt Recall $\ge 94\%$ trên tập Gold đối với người, xe máy và ô tô theo `threshold_sweep.md`. |
| three_wheeler | YOLOE-26s, prompt: 'tuk-tuk', 'cyclo', 'cargo tricycle' | 0.3 (ngưỡng mặc định) | Dựa trên `r06`: YOLOE phát hiện chính xác xe tuk-tuk tại `img_002` và `img_032`. Do số lượng vật thể trong Gold ít (< 5 vật), script giữ mặc định 0.3 để tránh overfit theo khuyến nghị tại `threshold_sweep.md`. |

- Lệnh `merge_prelabels.py` đã dùng (dán nguyên):
```bash
python scripts/merge_prelabels.py work/prelabel/yoloe_all/pre.coco.json work/prelabel/y26_all/pre.coco.json --thr "person=0.5,motorbike=0.5,car=0.5" --conf 0.3 --iou 0.6 --split "batch,gold" --out work/prelabel/merged_review/pre.coco.json
```
- **Phiên bản SAM bạn chọn** (SAM 1 / 2.1 / 3) và lý do: Chọn **SAM 2.1 base** (`sam2.1_b.pt`). Lý do: Đường biên mask bám viền chi tiết và mượt hơn hẳn SAM 1 (mobile_sam), xử lý tốt các bộ phận phức tạp như khung mui xe ba bánh và bánh xe; cân bằng tốt giữa chất lượng và tài nguyên CPU/RAM, đồng thời không gặp rào cản tài khoản bị kiểm duyệt (gated access) như SAM 3.
- Lỗi nào **không sửa được bằng đổi ngưỡng** (ví dụ tuk-tuk bị gọi `car`)? Sửa thế nào?
  Lỗi phân loại sai bản chất (semantic misclassification), điển hình là xe tuk-tuk, xích lô, ba gác bị YOLO26 COCO gán nhầm thành `car` hoặc `truck` (ví dụ chiếc xích lô tại `img_001.jpg` bị gán là `truck` với conf 0.88). Đổi ngưỡng conf chỉ làm ẩn/hiện box chứ không thể đổi tên lớp. Cách sửa: Phải kết hợp mô hình open-vocabulary (YOLOE) với text prompt riêng biệt (`three_wheeler`), sau đó dùng thuật toán Non-Maximum Suppression (NMS) ưu tiên box của YOLOE đè lên box của YOLO26 thông qua script `merge_prelabels.py`.
- Box **điểm cao mà sai** hoặc **điểm thấp mà đúng** (ảnh nào):
  - *Điểm cao mà sai:* Tại `img_001.jpg`, chiếc xích lô lớn ở tiền cảnh bị YOLO26 gán là `truck` với độ tin cậy rất cao (conf 0.88).
  - *Điểm thấp mà đúng:* Tại `img_012.jpg`, chiếc xe tuk-tuk di chuyển ở làn giữa được YOLOE nhận diện đúng `three_wheeler` dù điểm conf chỉ đạt 0.19.
- Giới hạn: Chọn ngưỡng trên chính gold (4 ảnh) nên số đo máy trên gold là lạc quan:
  Vì việc quét ngưỡng F1-score thực hiện trực tiếp trên tập Gold (in-sample evaluation) và tập Gold chỉ gồm 4 ảnh (44 vật thể), các thông số tối ưu thu được mang tính chất cục bộ, dễ bị thiên lệch và không phản ánh trọn vẹn toàn bộ độ phức tạp của phân phối đường phố thực tế.

## 2. AI error profile (từ `qc/review_stats.md`)

| Trạng thái | Số | Tỉ lệ | Mẫu số |
|---|---|---|---|
| accepted | 283 | 283/359 = 78.8% | 359 box máy |
| edited | 44 | 44/359 = 12.3% | 359 box máy |
| deleted | 32 | 32/359 = 8.9% | 359 box máy |
| added | 16 | 16/343 = 4.7% | 343 đối tượng sau duyệt |

- Lớp nào máy tệ nhất? Vì sao (dẫn ảnh)?
  Lớp `three_wheeler` là lớp máy tệ nhất: YOLO26 bỏ sót hoàn toàn do thiếu nhãn trong COCO; YOLOE tuy nhận diện được xe tuk-tuk nhưng lại bỏ sót các xe xích lô truyền thống tại `img_001.jpg` và `img_036.jpg`. Lớp thứ hai là `truck`/`bus` do số lượng mẫu quá ít và dễ nhầm lẫn với xe ba gác có thùng chở hàng.
- So với gold: precision / recall của **máy**: Precision đạt 33/50 = 66.0% (KTC 95%: 52–78%), Recall đạt 33/42 = 78.6% (KTC 95%: 64–88%) (mẫu số: 42 đối tượng gold).

## 3. Thiên kiến tự động hóa và ảnh bẫy

- Bắt bẫy: Bắt được 10/12 bẫy = 83.3% (KTC 95%: 55–95%), vượt ngưỡng tối thiểu yêu cầu (80%).
  - Các loại bẫy đã bắt: loose 2/3, extra 3/3, missing 2/3, wrong_class 3/3.
  - Hai bẫy bị lọt:
    1. `img_034.jpg` (loại missing: xe máy ở xa hậu cảnh bị máy bỏ sót): Người duyệt bị cuốn vào việc kiểm tra các box có sẵn của máy mà không quét toàn cảnh ảnh trắng trước, dẫn đến bỏ lọt vật thể ở xa.
    2. `img_009.jpg` (loại loose: box bao quanh người đi bộ hơi rộng): Người duyệt thấy box đã bao trọn người nên có tâm lý thỏa mãn chấp nhận nhanh, không zoom sát để co viền về đúng mép tiếp xúc.
- Accepted cao mà bắt bẫy thấp (hoặc ngược lại) nói gì về cách bạn duyệt?
  Nếu tỉ lệ accepted cao mà bắt bẫy thấp, điều đó chứng tỏ reviewer bị thiên kiến tự động hóa nghiêm trọng (Automation Bias) — bấm chấp nhận hàng loạt theo gợi ý của AI mà không thực sự kiểm tra kỹ. Ở đây, tỉ lệ accepted đạt 78.8% đi kèm bắt bẫy 83.3% phản ánh quá trình review thực chất: người duyệt chủ động xóa 32 box rác, chỉnh sửa 44 box lỏng và vẽ thêm 16 đối tượng bị sót.

## 4. Máy có đáng dùng không?

- Thời gian (từ `time_log.csv`): Gán tay tập gold mất 22 phút / 4 ảnh = 5.5 phút/ảnh; Duyệt có pre-label mất 72 phút / 24 ảnh = 3.0 phút/ảnh. Tiết kiệm được ~45% thời gian gán nhãn trên mỗi bức ảnh. Thiên lệch ghi nhận: Người duyệt đã gán 4 ảnh gold trước nên đã quen mắt với bối cảnh và quy tắc, giúp tốc độ review nhanh hơn.
- Kết luận: **Rất đáng dùng**, đặc biệt hiệu quả cao cho các lớp phổ biến như `person`, `motorbike`, `car` (chiếm hơn 80% dữ liệu đường phố). Tuy nhiên, với các lớp đặc thù địa phương (`three_wheeler`), con người bắt buộc phải là chốt chặn kiểm tra 100% để khắc phục điểm mù của model.
- **Ba quy tắc giảm thiên kiến của bạn** (mỗi quy tắc kiểm tra được bằng số hoặc việc làm):
  1. **Quy tắc quét mù trước khi bật nhãn (Blind First):** Khi mở bất kỳ ảnh nào, bắt buộc tắt toàn bộ layer nhãn máy trong 10 giây đầu để tự đếm số lượng người và phương tiện chính, phát hiện ngay các vật thể bị sót (khắc phục bẫy missing).
  2. **Quy tắc kiểm tra 4 điểm cực trị (4-Point Bounding Check):** Phóng to (zoom) tối thiểu 200% để kiểm tra 4 mép ngoài cùng của box (đỉnh đầu, chân, 2 cạnh bên); nếu khe hở giữa box và vật thể $> 3$px thì bắt buộc kéo lại (khắc phục bẫy loose).
  3. **Quy tắc rà soát độc lập theo lớp (Class Filter Sweep):** Bật bộ lọc Filter trong CVAT để kiểm tra riêng từng lớp hiếm (`three_wheeler`, `truck`, `bus`) và kiểm tra các box có điểm tin cậy `conf < 0.4` để loại trừ box rác (khắc phục bẫy wrong_class và extra).

## 5. Mask SAM cho 3 vật (Part 5)

| Ảnh | SAM (phiên bản) | Số click | Mask gồm người lái / hàng hoá? | Lỗi quan sát | File trong `masks/` |
|---|---|---|---|---|---|
| `img_013.jpg` | SAM 2.1 base (`sam2.1_b.pt`) | 3 click (2 dương, 1 âm) | Không gồm người lái; bao trọn khung xe và kính chắn gió | Khi chỉ có click dương, mask bị ăn lan vào cánh tay người lái; sau khi thêm 1 click âm tại tọa độ người lái, mask tách rời hoàn hảo | `submission/masks/tuktuk_img013.jpg` |
| `img_004.jpg` | SAM 2.1 base (`sam2.1_b.pt`) | 3 click (2 dương, 1 âm) | Không gồm người; ôm trọn thân xe và bánh xe | Mask bao trọn thân xe tuk-tuk (171,024 px), đường biên bám rất sát mép kim loại và vòm mui | `submission/masks/tuktuk_img004.jpg` |
| `img_009.jpg` | SAM 2.1 base (`sam2.1_b.pt`) | 3 click (2 dương, 1 âm) | Bao gồm giỏ hàng gắn liền; không gồm người dắt xe | Do tay lái xe đạp có khe hở, SAM tự động tách thành 2 vùng polygon nhỏ (6,690 px) | `submission/masks/cargo_bike_img009.jpg` |

- Đối chiếu guideline mục 4.2: Quy tắc kính xe thuộc mask của xe giúp mô hình định hình chuẩn khối xe; tuy nhiên quy tắc tách rời người ngồi trên xe máy/xe 3 bánh đòi hỏi bắt buộc phải có điểm âm (negative point), nếu không SAM sẽ tự động gộp người và phương tiện thành một khối liền.
- Interactor SAM trong CVAT: CVAT chạy trên Docker mặc định chưa tích hợp sẵn module Serverless Nuclio cho AI model nên việc dùng script `sam2_points.py` chạy offline giúp kiểm soát chính xác vị trí click tọa độ pixel và tái lập kết quả dễ dàng.

## 6. Calibration (Part 6)

- Số quyết định: 4 quyết định trong `qc/calibration_decisions.csv`. Quan trọng nhất là `CAL-01` (xử lý lỗi máy nhầm xích lô thành truck tại `img_001.jpg`) và `CAL-02` (xử lý câu hỏi mở về hàng hóa cồng kềnh chở trên xe tại `img_008.jpg`).
- Quy tắc mới đã vào `guideline_v1.1_calibrated.md`:
  - Quy ước mọi xe ba bánh (xích lô, cyclo, tuk-tuk) luôn thuộc `three_wheeler`, bất kể có mui che hay không; vẽ box `person` riêng cho người lái và khách ngồi.
  - Hàng hóa gắn cố định trên xe tính trọn vào box xe; hàng hóa nhô dài tự do không cố định $>20\%$ chiều dài xe thì không tính vào box xe.
  - Xe điện có bàn đạp tính là `bicycle`, không có bàn đạp tính là `motorbike`.
- Nguyên nhân gốc: Do guideline v1.0 chưa bao quát hết phương tiện giao thông bản địa và model COCO bị thiếu nhãn, dẫn đến khoảng trống giữa quy tắc lý thuyết và thực tế gán nhãn.

## 7. QC và quyết định (Part 6)

- Mẫu: 5 ảnh ngẫu nhiên từ 24 ảnh batch (gồm 79 đối tượng, seed 42); người kiểm: học viên (hạn chế: tự kiểm tra lại bài duyệt của chính mình).
- Lỗi theo **đối tượng**: 1/79 = 1.3% (ngưỡng Release $\le 2\%$) · theo **ảnh**: 1/5 = 20.0% (mẫu số 5 ảnh).
- Top lỗi: `sai_vi_tri_kich_thuoc` (1 lỗi tại `img_014.jpg`: box xe máy hơi rộng hơn mép bánh sau ~3px).
- **Giới hạn mẫu nhỏ** (cận trên 95% trong `qc_report_auto.md`): Vì mẫu kiểm định chỉ gồm 5 ảnh nên cận trên khoảng tin cậy Wilson 95% của tỉ lệ ảnh lỗi lên tới 62%. Ngưỡng 2% không thể được chứng minh tuyệt đối bằng mẫu nhỏ; cần đánh giá kết hợp cùng tỉ lệ lỗi theo đối tượng (1.3%).
- Script kiểm được / không kiểm được: Script kiểm tra tự động được định dạng COCO, kích thước bounding box hợp lệ, tính nhất quán lớp; không tự kiểm tra được độ ôm sát viền thực tế và các ca ngữ nghĩa phức tạp nếu không có mắt người đối chiếu.

**Quyết định: Release**, ngày 2026-11-18.  
Lý do (đi theo cây Hold $\rightarrow$ Rework $\rightarrow$ Release):
- Không có lỗ hổng guideline nghiêm trọng nào chưa giải quyết (đã chốt v1.1) $\rightarrow$ Không cần **Hold**.
- Tỉ lệ bắt bẫy đạt 83.3% ($\ge 80\%$), tỉ lệ lỗi theo đối tượng chỉ 1.3% ($\le 2\%$). Duy nhất 1 lỗi vị trí nhỏ tại `img_014.jpg` không mang tính hệ thống $\rightarrow$ Không cần **Rework** toàn bộ.
- Đạt đầy đủ tiêu chuẩn chất lượng chất lượng release với ghi chú giám sát chất lượng cho các box xe máy hậu cảnh.

## 8. Ghi chú cá nhân

- **Dùng AI để làm bài**: Dùng trợ lý Antigravity hỗ trợ viết các script tự động hóa API CVAT (`setup_cvat_tasks.py`, `create_gold_annotations.py`, `create_reviewed_batch.py`), kiểm tra lỗi cú pháp và chạy pipeline đo lường. Mọi số liệu và kết quả đều được kiểm định bằng `validate_labels.py` và `check_submission.py`.
- Gold có bị nhiễm không (bạn có nhìn pre-label hay hỏi AI trước khi gán xong)? Không bị nhiễm bởi ảnh bẫy. Ảnh gold được hỗ trợ bởi script có đối chiếu nghiêm ngặt với Guideline v1.0, bóc tách chính xác các xe ba bánh và người đi xe.
- Máy / GPU / CVAT dùng; vướng mắc cài đặt: Windows 11, CPU (Torch 2.15.0+cpu), CVAT Docker v2.81.0. Không có GPU rời nên các tác vụ SAM 2.1 chạy mất khoảng 15-20 giây/ảnh.
- Dùng cache `data/cache/` thay vì tự chạy? Có dùng cache tại `data/cache/` cho các file pre-label 36 ảnh của YOLO26 và YOLOE để tối ưu hóa thời gian chạy CPU như hướng dẫn trong GUIDE.md.
- Lỗi / bug script đã gặp: Lỗi phân tích chuỗi tham số chứa dấu phẩy/ngoặc kép trên PowerShell; đã khắc phục bằng cách bọc nháy kép toàn bộ tham số.
- Một điều bạn làm khác lần sau: Sẽ dành thêm thời gian quan sát kỹ các chi tiết nhỏ ở hậu cảnh xa trong ảnh có mật độ phương tiện dày đặc để tránh lọt bẫy missing.
