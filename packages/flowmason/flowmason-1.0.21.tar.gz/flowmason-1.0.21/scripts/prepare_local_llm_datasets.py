#!/usr/bin/env python3
"""
End-to-end dataset preparation for the FlowMason local LLM.

This script orchestrates the full pipeline:

1. Build the combined dataset from this repo:
   - scripts/build_local_llm_dataset.py
   - Output: data/flowmason_local_small.jsonl

2. Split into:
   - Supervised pipeline tasks (nl_to_pipeline, pipeline_explanation)
     -> data/flowmason_local_small_supervised.jsonl
   - Doc Q&A seed tasks (fm_doc_qa_seed)
     -> data/flowmason_doc_qa_seed.jsonl

3. Enrich doc Q&A seed tasks using the FlowMason pipeline
   pipelines/doc_qa_enricher.pipeline.json:
   - scripts/enrich_doc_qa_with_pipeline.py
   - Output: data/flowmason_doc_qa_enriched.jsonl

4. Sync the final datasets into the sibling training repo:
   ../flowmason-llm/data/

Usage (from this repo root, after your provider API keys are configured):

    python scripts/prepare_local_llm_datasets.py

After this completes, you should have in ../flowmason-llm/data/:
    - flowmason_local_small.jsonl
    - flowmason_local_small_supervised.jsonl
    - flowmason_doc_qa_seed.jsonl
    - flowmason_doc_qa_enriched.jsonl

These files can then be copied to your GPU box for training.
"""

import shutil
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
LLM_ROOT = REPO_ROOT.parent / "flowmason-llm"
LLM_DATA_DIR = LLM_ROOT / "data"


def run_step(args: list[str], description: str) -> None:
    """Run a subprocess step and fail fast on error."""
    print(f"\n=== {description} ===")
    print("Command:", " ".join(args))
    result = subprocess.run(args, cwd=REPO_ROOT)
    if result.returncode != 0:
        print(f"\n[ERROR] Step failed: {description}")
        sys.exit(result.returncode)


def main() -> None:
    # Ensure data dir exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # 1) Build combined dataset
    run_step(
        [
            sys.executable,
            "scripts/build_local_llm_dataset.py",
            "-o",
            str(DATA_DIR / "flowmason_local_small.jsonl"),
        ],
        "Building combined dataset (flowmason_local_small.jsonl)",
    )

    # 2) Split into supervised + doc_qa_seed
    run_step(
        [
            sys.executable,
            "scripts/split_local_llm_dataset.py",
            "--input",
            str(DATA_DIR / "flowmason_local_small.jsonl"),
        ],
        "Splitting into supervised + doc_qa_seed datasets",
    )

    # 3) Enrich doc_qa_seed using the doc_qa_enricher pipeline
    run_step(
        [
            sys.executable,
            "scripts/enrich_doc_qa_with_pipeline.py",
            "--input",
            str(DATA_DIR / "flowmason_doc_qa_seed.jsonl"),
            "--output",
            str(DATA_DIR / "flowmason_doc_qa_enriched.jsonl"),
        ],
        "Enriching doc_qa_seed records using doc_qa_enricher pipeline",
    )

    # 4) Sync to ../flowmason-llm/data
    if not LLM_ROOT.exists():
        print(
            f"\n[WARNING] Training repo not found at {LLM_ROOT}. "
            "Skipping copy step. Create the flowmason-llm folder next to this repo "
            "if you want automatic sync."
        )
        return

    LLM_DATA_DIR.mkdir(parents=True, exist_ok=True)

    files_to_copy = [
        "flowmason_local_small.jsonl",
        "flowmason_local_small_supervised.jsonl",
        "flowmason_doc_qa_seed.jsonl",
        "flowmason_doc_qa_enriched.jsonl",
    ]

    print(f"\n=== Copying datasets to {LLM_DATA_DIR} ===")
    for name in files_to_copy:
        src = DATA_DIR / name
        if not src.exists():
            print(f"[WARNING] Source file not found, skipping: {src}")
            continue
        dst = LLM_DATA_DIR / name
        shutil.copy2(src, dst)
        print(f"Copied {src} -> {dst}")

    print("\nAll dataset preparation steps completed.")
    print(f"Training datasets are ready under: {LLM_DATA_DIR}")


if __name__ == "__main__":
    main()

