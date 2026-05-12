# Phân tích cụm lỗi

- Loại chạy: real RAG + real RAGAS
- Ngày chạy: 2026-05-12.
- Cỡ mẫu: 3 câu hỏi.
- Model: `gpt-4o-mini` cho generation và judge, `text-embedding-3-small` với 768 dimensions cho embeddings.
- Kiểm soát ổn định: tắt local reranker bằng `DISABLE_RERANKER=1`; giới hạn context gửi vào RAGAS ở mức 2 contexts x 1200 ký tự.
- Runtime quan sát được: khoảng 5.5 phút tổng cộng; RAGAS chấm 12 tasks trong khoảng 4 phút.

## Điểm tổng hợp

| Metric | Score | Lab Min OK | Trạng thái |
|---|---:|---:|---|
| Faithfulness | 0.533 | 0.75 | Chưa đạt |
| Answer Relevancy | 0.524 | 0.70 | Chưa đạt |
| Context Precision | 0.667 | 0.60 | Đạt mức tối thiểu |
| Context Recall | 0.667 | 0.65 | Đạt mức tối thiểu |

## Các câu đã đánh giá

| # | Câu hỏi | F | AR | CP | CR | Avg | Cụm lỗi |
|---|---|---:|---:|---:|---:|---:|---|
| 1 | Tên người nộp thuế và mã số thuế trong tờ khai thuế GTGT Mẫu số 01/GTGT là gì? | 1.00 | 0.80 | 1.00 | 1.00 | 0.95 | C2 |
| 2 | Thuế giá trị gia tăng phải nộp của hoạt động sản xuất kinh doanh trong kỳ 4 năm 2024 là bao nhiêu? | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | C1 |
| 3 | Nghị định 13/2023/NĐ-CP áp dụng đối với những đối tượng nào? | 0.60 | 0.78 | 1.00 | 1.00 | 0.84 | C2 |

## Các cụm lỗi

### Cụm C1: Lỗi truy xuất số liệu/bảng

**Mẫu lỗi:** Câu hỏi về số tiền thuế GTGT phải nộp trả về câu abstention, nghĩa là retrieval/generation chưa tìm được context đủ rõ để trả lời số liệu trực tiếp.

**Ví dụ:**
- Thuế giá trị gia tăng phải nộp của hoạt động sản xuất kinh doanh trong kỳ 4 năm 2024 là bao nhiêu?
- Các câu hỏi số liệu BCTC liên quan nên được kiểm tra thêm ở lần chạy 5-10 câu tiếp theo.

**Nguyên nhân gốc:** BCTC là tài liệu dạng bảng/OCR; quá trình unroll bảng và retrieval có thể bỏ lỡ cặp nhãn-dòng-giá trị chính xác. Việc tắt reranker giúp tránh crash trên Windows nhưng có thể làm giảm chất lượng ranking.

**Hướng khắc phục đề xuất:** Bảo toàn nhãn dòng và giá trị trong chunk ngắn gọn, thêm source-aware filter cho `BCTC.md` khi query có từ khóa thuế/số tiền, và thêm numeric lookup nhẹ trước bước generation.

### Cụm C2: Retrieval tốt nhưng RAGAS vẫn phạt một phần

**Mẫu lỗi:** Các câu hỏi về định danh thuế và pháp lý lấy được evidence liên quan và trả lời khá đúng, nhưng RAGAS vẫn trừ điểm answer relevancy hoặc faithfulness do câu trả lời dài/list nhiều ý.

**Ví dụ:**
- Tên người nộp thuế và mã số thuế trong tờ khai thuế GTGT Mẫu số 01/GTGT là gì?
- Nghị định 13/2023/NĐ-CP áp dụng đối với những đối tượng nào?

**Nguyên nhân gốc:** Câu trả lời nhìn chung grounded, nhưng RAGAS tách câu tiếng Việt thành nhiều statement và có thể phạt formatting hoặc phần diễn giải dư.

**Hướng khắc phục đề xuất:** Tạo chế độ generation riêng cho eval: trả lời ngắn, trực tiếp, ít diễn giải; thêm source snippets/citations ở format ổn định.

