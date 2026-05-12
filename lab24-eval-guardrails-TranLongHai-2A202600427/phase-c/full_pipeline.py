"""Lab 24 Phase C.5: full guarded pipeline and latency benchmark."""

from __future__ import annotations

import argparse
import asyncio
import csv
import json
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "phase-c") not in sys.path:
    sys.path.insert(0, str(ROOT / "phase-c"))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from input_guard import InputGuard, check_topic_async, detect_injection_async, refuse_response
from output_guard import OutputGuard


def percentile(values: list[float], pct: int) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = min(len(ordered) - 1, round((pct / 100) * (len(ordered) - 1)))
    return ordered[idx]


async def audit_log(record: dict) -> None:
    path = ROOT / "phase-c" / "audit_log.jsonl"
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


class GuardedPipeline:
    def __init__(self, mock_rag: bool = True, output_mode: str = "mock") -> None:
        self.input_guard = InputGuard()
        self.output_guard = OutputGuard(output_mode)
        self.mock_rag = mock_rag
        self.rag_state: dict = {}

    async def rag_answer(self, user_input: str) -> str:
        if self.mock_rag:
            return "Câu trả lời mẫu dựa trên tài liệu về Nghị định 13, thuế GTGT hoặc BCTC."
        if "pipeline" not in self.rag_state:
            from src.pipeline import build_pipeline

            self.rag_state["pipeline"] = build_pipeline()
        from src.pipeline import run_query

        answer, _ = await asyncio.to_thread(run_query, user_input, *self.rag_state["pipeline"])
        return answer

    async def guarded_pipeline(self, user_input: str) -> tuple[str, dict]:
        timings: dict[str, float] = {}

        t0 = time.perf_counter()
        pii_task = asyncio.create_task(self.input_guard.sanitize_async(user_input))
        topic_task = asyncio.create_task(check_topic_async(user_input))
        injection_task = asyncio.create_task(detect_injection_async(user_input))
        pii_result = await pii_task
        topic_ok, topic_matches = await topic_task
        injection_found, injection_matches = await injection_task
        timings["L1"] = (time.perf_counter() - t0) * 1000

        if injection_found or not topic_ok:
            answer = refuse_response()
            await audit_log({"input": user_input, "blocked": True, "topic": topic_matches, "injection": injection_matches, "timings": timings})
            return answer, timings

        t0 = time.perf_counter()
        answer = await self.rag_answer(pii_result.text)
        timings["L2"] = (time.perf_counter() - t0) * 1000

        t0 = time.perf_counter()
        safe, raw_guard, _ = await self.output_guard.check_async(pii_result.text, answer)
        timings["L3"] = (time.perf_counter() - t0) * 1000
        if not safe:
            answer = refuse_response()

        asyncio.create_task(audit_log({"input": user_input, "answer": answer, "output_guard": raw_guard, "timings": timings}))
        return answer, timings


def load_queries(n: int) -> list[str]:
    with open(ROOT / "test_set.json", encoding="utf-8") as f:
        seed = json.load(f)
    queries = [item["question"] for item in seed]
    while len(queries) < n:
        queries.extend(queries)
    return queries[:n]


async def benchmark(n: int, mock_rag: bool, output_mode: str) -> None:
    pipeline = GuardedPipeline(mock_rag=mock_rag, output_mode=output_mode)
    rows = []
    for i, query in enumerate(load_queries(n), start=1):
        print(f"[{i}/{n}] {i / n * 100:5.1f}% guarded benchmark")
        _, timings = await pipeline.guarded_pipeline(query)
        rows.append({"id": i, "query": query, **timings, "total_ms": sum(timings.values())})

    output = ROOT / "phase-c" / "latency_benchmark.csv"
    with open(output, "w", encoding="utf-8", newline="") as f:
        fieldnames = ["id", "query", "L1", "L2", "L3", "total_ms"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    for layer in ["L1", "L2", "L3", "total_ms"]:
        vals = [float(r.get(layer, 0)) for r in rows]
        print(
            f"{layer}: P50={statistics.median(vals):.1f}ms "
            f"P95={percentile(vals, 95):.1f}ms P99={percentile(vals, 99):.1f}ms"
        )
    print(f"Wrote {output}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=20)
    parser.add_argument("--real-rag", action="store_true", help="Use the real RAG pipeline; may call APIs.")
    parser.add_argument("--output-mode", choices=["mock", "groq"], default="mock")
    args = parser.parse_args()
    asyncio.run(benchmark(args.n, mock_rag=not args.real_rag, output_mode=args.output_mode))


if __name__ == "__main__":
    main()
