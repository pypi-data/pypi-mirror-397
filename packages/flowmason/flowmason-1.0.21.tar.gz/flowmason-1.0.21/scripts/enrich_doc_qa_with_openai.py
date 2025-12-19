#!/usr/bin/env python3
"""
Enrich FlowMason doc Q&A seed dataset using an OpenAI model.

This script reads records from data/flowmason_doc_qa_seed.jsonl (as
produced by scripts/split_local_llm_dataset.py), calls an OpenAI chat
model to generate concrete answers, and writes an enriched dataset with
real outputs instead of generic placeholders.

The script does NOT store any API keys. It expects them in environment
variables, for example:

- FLOWMASON_OPENAI_API_KEY
- OPENAI_API_KEY

Usage (from repo root, after sourcing your ~/.zshrc so env vars are set):

    python scripts/enrich_doc_qa_with_openai.py \\
        --input data/flowmason_doc_qa_seed.jsonl \\
        --output data/flowmason_doc_qa_enriched.jsonl \\
        --model gpt-4o-mini \\
        --max-records 200
"""

import argparse
import json
import os
import time
from pathlib import Path
from typing import Dict, Optional

import requests


def get_openai_api_key() -> str:
    """Resolve OpenAI API key from environment."""
    key = os.environ.get("FLOWMASON_OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not key:
        raise RuntimeError(
            "No OpenAI API key found. Set FLOWMASON_OPENAI_API_KEY or OPENAI_API_KEY."
        )
    return key


def call_openai_chat(
    api_key: str,
    model: str,
    question: str,
    documentation: str,
    temperature: float = 0.2,
    max_tokens: int = 512,
) -> str:
    """
    Call OpenAI chat completions API to answer a question using a doc excerpt.
    """
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    system_prompt = (
        "You are FlowMason's product documentation assistant. "
        "Answer questions strictly based on the provided documentation excerpt. "
        "If the excerpt does not contain enough information, say you don't know "
        "and do not invent features or behavior."
    )

    user_prompt = (
        f"Question:\n{question}\n\n"
        "Documentation excerpt:\n"
        f"{documentation}\n\n"
        "Answer using only the information in the excerpt. "
        "Be concise and specific."
    )

    payload: Dict = {
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    if resp.status_code != 200:
        raise RuntimeError(f"OpenAI API error {resp.status_code}: {resp.text}")

    data = resp.json()
    choice = data.get("choices", [{}])[0]
    message = choice.get("message", {})
    return message.get("content", "").strip()


def enrich_doc_qa(
    input_path: Path,
    output_path: Path,
    model: str,
    max_records: Optional[int] = None,
    sleep_seconds: float = 0.3,
) -> None:
    """Enrich fm_doc_qa_seed records with real answers from OpenAI."""
    api_key = get_openai_api_key()

    processed = 0
    skipped = 0

    output_path.parent.mkdir(parents=True, exist_ok=True)
    out = output_path.open("w", encoding="utf-8")

    with input_path.open(encoding="utf-8") as f:
        for line in f:
            if max_records is not None and processed >= max_records:
                break

            if not line.strip():
                continue

            try:
                rec = json.loads(line)
            except Exception:
                skipped += 1
                continue

            if rec.get("task") != "fm_doc_qa_seed":
                # Pass through other tasks unchanged
                out.write(json.dumps(rec, ensure_ascii=False) + "\n")
                continue

            instruction = rec.get("instruction", "")
            input_text = rec.get("input", "")

            # Extract question and documentation from the input field
            # Input pattern: "Question: ...\n\nDocumentation:\n..."
            question = ""
            documentation = ""
            marker = "Documentation:\n"
            if marker in input_text:
                q_part, doc_part = input_text.split(marker, 1)
                question = q_part.replace("Question:", "").strip()
                documentation = doc_part.strip()
            else:
                # Fallback: treat whole input as documentation
                documentation = input_text

            try:
                answer = call_openai_chat(
                    api_key=api_key,
                    model=model,
                    question=question or "Summarize this documentation.",
                    documentation=documentation,
                )
            except Exception as e:
                # On API error, keep original placeholder output and continue
                skipped += 1
                continue

            # Keep original placeholder in case we want to inspect later
            rec["placeholder_output"] = rec.get("output")
            rec["output"] = answer
            rec["model"] = model
            rec["task"] = "fm_doc_qa"  # mark as enriched

            out.write(json.dumps(rec, ensure_ascii=False) + "\n")
            processed += 1

            if sleep_seconds > 0:
                time.sleep(sleep_seconds)

    out.close()

    print(f"Input:  {input_path}")
    print(f"Output: {output_path}")
    print(f"Processed records: {processed}")
    print(f"Skipped records:   {skipped}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Enrich FlowMason doc QA seed dataset using OpenAI."
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
        "--model",
        "-m",
        type=str,
        default="gpt-4o-mini",
        help="OpenAI chat model to use (e.g. gpt-4o-mini, gpt-4o).",
    )
    parser.add_argument(
        "--max-records",
        type=int,
        default=None,
        help="Maximum number of records to enrich (for cost control).",
    )
    parser.add_argument(
        "--sleep-seconds",
        type=float,
        default=0.3,
        help="Sleep between requests to avoid rate limits.",
    )
    args = parser.parse_args()

    enrich_doc_qa(
        input_path=args.input.resolve(),
        output_path=args.output.resolve(),
        model=args.model,
        max_records=args.max_records,
        sleep_seconds=args.sleep_seconds,
    )


if __name__ == "__main__":
    main()

