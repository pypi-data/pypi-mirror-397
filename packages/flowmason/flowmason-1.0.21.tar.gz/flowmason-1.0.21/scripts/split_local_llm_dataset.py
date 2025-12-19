#!/usr/bin/env python3
"""
Split the combined local LLM dataset into:

- Supervised pipeline tasks (nl_to_pipeline, pipeline_explanation)
- Doc Q&A seed tasks (fm_doc_qa_seed)

This avoids training on placeholder outputs for doc Q&A while still
letting you use the pipeline tasks immediately and refine the doc
examples later.

Usage (from repo root):
    python scripts/split_local_llm_dataset.py \
        --input data/flowmason_local_small.jsonl
"""

import argparse
import json
from pathlib import Path
from typing import Dict


def split_dataset(input_path: Path) -> None:
    """Split the dataset into supervised and doc Q&A seed files."""
    supervised_path = input_path.with_name(
        input_path.stem + "_supervised" + input_path.suffix
    )
    docqa_path = input_path.with_name("flowmason_doc_qa_seed" + input_path.suffix)

    supervised_out = supervised_path.open("w", encoding="utf-8")
    docqa_out = docqa_path.open("w", encoding="utf-8")

    counts: Dict[str, int] = {}

    with input_path.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue

            task = rec.get("task", "unknown")
            counts[task] = counts.get(task, 0) + 1

            if task == "fm_doc_qa_seed":
                docqa_out.write(json.dumps(rec, ensure_ascii=False) + "\n")
            else:
                supervised_out.write(json.dumps(rec, ensure_ascii=False) + "\n")

    supervised_out.close()
    docqa_out.close()

    print(f"Input: {input_path}")
    print(f"Wrote supervised pipeline tasks to: {supervised_path}")
    print(f"Wrote doc Q&A seed tasks to:      {docqa_path}")
    print("Task counts:", counts)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Split FlowMason local LLM dataset into supervised and doc QA seed sets."
    )
    parser.add_argument(
        "--input",
        "-i",
        type=Path,
        default=Path("data/flowmason_local_small.jsonl"),
        help="Combined dataset JSONL path.",
    )
    args = parser.parse_args()

    split_dataset(args.input.resolve())


if __name__ == "__main__":
    main()

