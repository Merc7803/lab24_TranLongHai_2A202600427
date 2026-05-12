# Báo cáo bias của judge

| Loại bias | Cách đo | Kết quả | Cách giảm thiểu |
|---|---:|---|---|
| Position bias | Tỷ lệ bất đồng sau khi swap A/B | 0.0% (0/10) | Nếu hai lượt judge bất đồng thì quy về `tie`. |
| Length bias | Tỷ lệ baseline dài hơn thắng | 10.0% (1/10) | Đưa tiêu chí súc tích vào rubric và giới hạn answer dạng context-only. |

## Nhận xét

Kết quả hiện tại là smoke/local judge trên 10 câu, chưa phải LLM judge thật. Để đạt đúng rubric Phase B, cần chạy thêm:

```powershell
python phase-b/judge.py --limit 30 --llm
```

Sau đó điền `phase-b/human_labels.csv` và chạy:

```powershell
python phase-b/kappa_analysis.py
```
