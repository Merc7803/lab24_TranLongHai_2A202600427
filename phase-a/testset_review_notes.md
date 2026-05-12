# Ghi chú review test set

Đã review 10 câu đầu tiên trong `phase-a/testset_v1.csv` để kiểm tra: câu hỏi có liên quan tới corpus, có thể trả lời được từ tài liệu, và có phân bố loại câu hỏi tương đối đa dạng.

| # | Loại câu hỏi | Trạng thái | Ghi chú |
|---|---|---|---|
| 1 | simple | đã chỉnh | Đã chỉnh wording để yêu cầu câu trả lời ngắn gọn dựa trên corpus. |
| 2 | reasoning | chấp nhận | Câu hỏi có thể trả lời từ tài liệu hiện có. |
| 3 | multi_context | chấp nhận | Câu hỏi có thể trả lời từ tài liệu hiện có. |
| 4 | simple | chấp nhận | Câu hỏi có thể trả lời từ tài liệu hiện có. |
| 5 | simple | chấp nhận | Câu hỏi có thể trả lời từ tài liệu hiện có. |
| 6 | reasoning | chấp nhận | Câu hỏi có thể trả lời từ tài liệu hiện có. |
| 7 | multi_context | chấp nhận | Câu hỏi có thể trả lời từ tài liệu hiện có. |
| 8 | simple | chấp nhận | Câu hỏi có thể trả lời từ tài liệu hiện có. |
| 9 | simple | chấp nhận | Câu hỏi có thể trả lời từ tài liệu hiện có. |
| 10 | reasoning | chấp nhận | Câu hỏi có thể trả lời từ tài liệu hiện có. |

## Nhận xét chung

- Test set hiện tại được mở rộng từ `test_set.json` để tiết kiệm chi phí, chưa dùng LLM synthetic generation đầy đủ.
- Có đủ các cột `question`, `ground_truth`, `contexts`, `evolution_type`.
- Nên chạy thêm full synthetic generation nếu cần bám sát rubric tuyệt đối và có thêm ngân sách API.
