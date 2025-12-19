#!/usr/bin/env python3
"""
Enrich FlowMason doc Q&A seed dataset using a FlowMason pipeline.

This uses the `pipelines/doc_qa_enricher.pipeline.json` pipeline, which
in turn calls your configured LLM provider via the `generator` node.

It reads records from `data/flowmason_doc_qa_seed.jsonl` (created by
scripts/split_local_llm_dataset.py), runs the pipeline per record to
generate a concrete answer based on the documentation excerpt, and
writes an enriched JSONL file.

Important:
- This script expects your provider API keys to be available via
  environment variables (e.g. OPENAI_API_KEY, ANTHROPIC_API_KEY).
- It uses FlowMason's auto_discover() to load lab components.

Usage (from repo root, after sourcing your shell so env vars are set):

    python scripts/enrich_doc_qa_with_pipeline.py \\
        --input data/flowmason_doc_qa_seed.jsonl \\
        --output data/flowmason_doc_qa_enriched.jsonl
"""

import argparse
import asyncio
import json
from pathlib import Path
from typing import Dict, Optional, Tuple

from flowmason_core.api import FlowMason


def parse_question_and_doc(input_text: str) -> Tuple[str, str]:
    """
    Extract question and documentation from the input field.

    Expected pattern:
        "Question: ...\\n\\nDocumentation:\\n..."
    """
    question = ""
    documentation = input_text

    marker = "Documentation:\n"
    if marker in input_text:
        q_part, doc_part = input_text.split(marker, 1)
        question = q_part.replace("Question:", "").strip()
        documentation = doc_part.strip()

    return question, documentation


async def enrich_record(
    pipeline,
    record: Dict,
) -> Optional[Dict]:
    """
    Run the doc_qa_enricher pipeline for a single record.

    Returns an enriched record or None on failure.
    """
    if record.get("task") != "fm_doc_qa_seed":
        # Pass through non-doc-qa-seed tasks unchanged
        return record

    input_text = record.get("input", "")
    question, documentation = parse_question_and_doc(input_text)

    # If we somehow have no documentation, skip
    if not documentation:
        return None

    try:
        result = await pipeline.run(
            {
                "question": question or "Summarize this documentation.",
                "documentation": documentation,
            }
        )
    except Exception:
        return None

    content = ""
    if result.output and isinstance(result.output, dict):
        # Generator node Output has 'content'
        content = result.output.get("content") or ""

    if not content:
        return None

    enriched = dict(record)
    enriched["placeholder_output"] = record.get("output")
    enriched["output"] = content
    enriched["task"] = "fm_doc_qa"  # mark as enriched

    return enriched


async def enrich_doc_qa_with_pipeline(
    input_path: Path,
    output_path: Path,
    max_records: Optional[int] = None,
) -> None:
    """
    Enrich doc QA seed records using the FlowMason doc_qa_enricher pipeline.
    """
    fm = FlowMason(auto_load_env=True)
    # Ensure lab components (including generator) are registered
    fm.registry.auto_discover()

    pipeline = fm.load_pipeline("pipelines/doc_qa_enricher.pipeline.json")

    processed = 0
    written = 0
    skipped = 0

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with input_path.open(encoding="utf-8") as fin, output_path.open(
        "w", encoding="utf-8"
    ) as fout:
        for line in fin:
            if max_records is not None and processed >= max_records:
                break

            if not line.strip():
                continue

            try:
                rec = json.loads(line)
            except Exception:
                skipped += 1
                continue

            enriched = await enrich_record(pipeline, rec)
            processed += 1

            if enriched is None:
                skipped += 1
                continue

            fout.write(json.dumps(enriched, ensure_ascii=False) + "\n")
            written += 1

    print(f"Input:    {input_path}")
    print(f"Output:   {output_path}")
    print(f"Processed records: {processed}")
    print(f"Written records:   {written}")
    print(f"Skipped records:   {skipped}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Enrich FlowMason doc QA seed dataset using the doc_qa_enricher pipeline."
    )
    parser.add_argument(
        "--input",
        "-i",
        type=Path,
        default=Path("data/flowmason_doc_qa_seed.jsonl"),
        help="Input JSONL path with fm_doc_qa_seed records.",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("data/flowmason_doc_qa_enriched.jsonl"),
        help="Output JSONL path for enriched records.",
    )
    parser.add_argument(
        "--max-records",
        type=int,
        default=None,
        help="Maximum number of records to process (for testing/cost control).",
    )
    args = parser.parse_args()

    asyncio.run(
        enrich_doc_qa_with_pipeline(
            input_path=args.input.resolve(),
            output_path=args.output.resolve(),
            max_records=args.max_records,
        )
    )


if __name__ == "__main__":
    main()

