# Lab 24 - Hệ thống Evaluation & Guardrail hoàn chỉnh

## Tổng quan

Repo này mở rộng nền tảng Production RAG của Day 18 để hoàn thành Lab 24. Phần triển khai bổ sung pipeline đánh giá RAGAS chi phí thấp, LLM-as-Judge dạng pairwise và absolute scoring, hiệu chỉnh với Cohen's kappa, guardrails đầu vào/đầu ra, benchmark độ trễ và blueprint triển khai production. 


## Tóm tắt kết quả

### Phase A: RAGAS

- `phase-a/testset_v1.csv`: test set 50 câu, có nhãn `simple`, `reasoning`, `multi_context`.
- `phase-a/ragas_results.csv`: kết quả chạy thật mới nhất trên 3 câu.
- `phase-a/ragas_summary.json`: điểm tổng hợp mới nhất: faithfulness 0.533, answer relevancy 0.524, context precision 0.667, context recall 0.667.
- `phase-a/failure_analysis.md`: phân tích failure từ lần chạy thật 3 câu. Lỗi chính là truy xuất bảng/số liệu BCTC chưa bắt đúng dòng giá trị.

### Phase B: LLM-as-Judge

- `phase-b/pairwise_results.csv`: judge pairwise có swap-and-average để giảm position bias.
- `phase-b/absolute_scores.csv`: chấm điểm tuyệt đối theo 4 tiêu chí.
- `phase-b/to_label.csv` và `phase-b/human_labels.csv`: template để gán nhãn thủ công.
- `phase-b/kappa_analysis.py`: script tính Cohen's kappa.
- `phase-b/judge_bias_report.md`: báo cáo position bias và length bias.

### Phase C: Guardrails

- Input guard kết hợp Presidio fallback với regex tiếng Việt cho email, số điện thoại, CCCD/CMND và mã số thuế.
- Topic validator dùng rule-based, giới hạn trong phạm vi Nghị định 13, bảo vệ dữ liệu cá nhân, thuế, GTGT, BCTC và DHA Surfaces.
- Injection detector bắt các mẫu DAN, tiết lộ prompt, ignore-instruction, role-play bypass và obfuscation.
- Output guard mặc định dùng mock mode; có thể chạy Groq Llama Guard 3 để validate thật thủ công.
- Full-stack benchmark ghi số liệu phục vụ P50/P95/P99 vào `phase-c/latency_benchmark.csv`.

### Phase D: Blueprint

Xem `phase-d/blueprint.md` để biết SLOs, sơ đồ kiến trúc, alert playbook và phân tích chi phí.


## Kiểm soát chi phí

Code tách riêng smoke validation và full rubric run. CI và smoke run local dùng mock RAG hoặc heuristic scoring mặc định. Các lệnh gọi RAGAS, OpenAI judge, Groq Llama Guard hoặc real RAG pipeline đều cần flag rõ ràng để chỉ chạy khi đã chấp nhận chi phí. Real RAGAS run dùng gpt-4o-mini, OpenAI embeddings, tắt local reranker và giới hạn context (--max-eval-contexts 2 --max-eval-context-chars 1200) để tránh prompt judge quá lớn. Một lần chạy 10 câu chưa giới hạn context từng bị ước lượng kéo dài nhiều giờ vì RAGAS nhận context quá dài.

---

