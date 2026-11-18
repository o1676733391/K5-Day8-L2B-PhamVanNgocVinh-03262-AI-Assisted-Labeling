# Thông tin học viên

- Họ và tên: Phạm Văn Ngọc Vinh
- MSHV: 03262
- Lớp (L2 / L3 / khác): L2B
- Tài khoản GitHub: o1676733391
- Repo bài nộp (URL): https://github.com/o1676733391/K5-Day8-L2B-PhamVanNgocVinh-03262-AI-Assisted-Labeling
- Commit chốt bài (hash): 9470223
- Máy: Windows 11, không có GPU (CPU: Intel/AMD, Torch 2.15.0+cpu)
- CVAT (Docker): v2.81.0

## Kết quả tóm tắt (điền cuối bài; số lấy từ `submission/qc/*`, kèm mẫu số)

- Máy: accepted / edited / deleted: 283 / 44 / 32 (mẫu số: 359 box máy); added: 16 (mẫu số: 343 đối tượng)
- So với gold: precision / recall của **máy**: 66.0% / 78.6% (mẫu số: 42 đối tượng gold)
- Bắt bẫy: 10/12 = 83.3%
- Thời gian: gán tay 5.5 phút/ảnh (22 phút / 4 ảnh); duyệt có pre-label 3.0 phút/ảnh (72 phút / 24 ảnh)
- Lỗi QC: 20.0% theo ảnh (1/5), 1.3% theo đối tượng (1/79)
- **Quyết định:** Release — lý do một dòng: Tỉ lệ lỗi theo đối tượng thấp (1.3% <= 2%), bắt bẫy đạt 83.3% (>= 80%) và đã hoàn thiện calibration guideline v1.1.
