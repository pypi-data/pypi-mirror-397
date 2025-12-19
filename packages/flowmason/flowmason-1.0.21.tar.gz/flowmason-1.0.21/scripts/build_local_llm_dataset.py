#!/usr/bin/env python3
"""
Build training data for the FlowMason local LLM.

This script scans:
- pipelines/*.pipeline.json
- examples/ (pipeline-like files)
- fmdocs/**/*.md

and emits a JSONL file with instruction-style records that can be used to
fine-tune a small local model for FlowMason-specific tasks:
- NL -> pipeline design
- FlowMason Q&A from docs
- Pipeline explanation

Usage:
    python scripts/build_local_llm_dataset.py \
        --output data/flowmason_local_small.jsonl
"""

import argparse
import json
import os
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


REPO_ROOT = Path(__file__).resolve().parents[1]


def discover_pipeline_files() -> List[Path]:
    """
    Discover candidate pipeline JSON files across the repo.

    We look in:
    - pipelines/ (including examples/)
    - examples/
    - manualtesting/**/pipelines/
    - studio/flowmason_studio/data/templates/
    """
    candidates: List[Path] = []

    def add_if_exists(path: Path) -> None:
        if path.exists():
            candidates.append(path)

    # Top-level pipelines (and nested examples)
    pipelines_root = REPO_ROOT / "pipelines"
    if pipelines_root.exists():
        for path in pipelines_root.rglob("*.pipeline.json"):
            add_if_exists(path)
        for path in pipelines_root.rglob("*pipeline.json"):
            add_if_exists(path)

    # examples/
    examples_root = REPO_ROOT / "examples"
    if examples_root.exists():
        for path in examples_root.rglob("*.json"):
            add_if_exists(path)

    # manualtesting/**/pipelines/*.json
    manual_root = REPO_ROOT / "manualtesting"
    if manual_root.exists():
        for path in manual_root.rglob("pipelines/*.json"):
            add_if_exists(path)

    # Studio templates
    studio_templates = REPO_ROOT / "studio" / "flowmason_studio" / "data" / "templates"
    if studio_templates.exists():
        for path in studio_templates.rglob("*.json"):
            add_if_exists(path)

    # Deduplicate
    unique_paths = sorted(set(candidates))
    return unique_paths


def is_pipeline_config(data: Dict) -> bool:
    """Heuristic check whether a JSON object looks like a pipeline config."""
    if not isinstance(data, dict):
        return False

    if "stages" in data and isinstance(data["stages"], (list, dict)):
        return True

    if data.get("id") and data.get("version") and (
        "input_schema" in data or "output_schema" in data
    ):
        return True

    return False


def load_pipelines() -> List[Tuple[Path, Dict]]:
    """Load pipeline JSON-like files from the repo."""
    results: List[Tuple[Path, Dict]] = []

    for path in discover_pipeline_files():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue

        if not is_pipeline_config(data):
            continue

        results.append((path, data))

    return results


def load_docs() -> List[Tuple[Path, str]]:
    """Load markdown docs from fmdocs/."""
    docs_root = REPO_ROOT / "fmdocs"
    results: List[Tuple[Path, str]] = []

    if not docs_root.exists():
        return results

    for path in docs_root.rglob("*.md"):
        try:
            text = path.read_text(encoding="utf-8")
            # Skip huge aggregated docs by default
            if path.name.upper() == "ALL-IN-ONE.md":
                continue
            results.append((path, text))
        except Exception:
            continue
    return results


def make_nl_to_pipeline_examples(pipelines: List[Tuple[Path, Dict]]) -> Iterable[Dict]:
    """
    Create NL -> pipeline examples from existing pipeline JSON.

    For each pipeline we generate multiple description variants so the
    model sees a richer set of NL formulations.
    """
    for path, data in pipelines:
        name = data.get("name") or data.get("id") or path.stem

        # Base description from pipeline
        base_description = (data.get("description") or "").strip()

        # Stage info
        stages = data.get("stages") or []
        if isinstance(stages, dict):
            stage_values = list(stages.values())
        else:
            stage_values = list(stages)

        stage_names = [
            s.get("name") or s.get("id")
            for s in stage_values
            if isinstance(s, dict) and (s.get("name") or s.get("id"))
            ]
        stage_types = [
            s.get("component_type") or s.get("component")
            for s in stage_values
            if isinstance(s, dict) and (s.get("component_type") or s.get("component"))
        ]

        # I/O fields
        input_schema = data.get("input_schema") or {}
        output_schema = data.get("output_schema") or {}
        input_props = list((input_schema.get("properties") or {}).keys())
        output_props = list((output_schema.get("properties") or {}).keys())

        variants: List[str] = []

        if base_description:
            variants.append(base_description)

        if base_description and stage_names:
            variants.append(
                f"{base_description} It has stages: {', '.join(stage_names)}."
            )

        if stage_types:
            variants.append(
                f"A FlowMason pipeline with components: {', '.join(stage_types)}."
            )

        if input_props or output_props:
            io_bits: List[str] = []
            if input_props:
                io_bits.append(f"takes inputs: {', '.join(input_props)}")
            if output_props:
                io_bits.append(f"produces outputs: {', '.join(output_props)}")
            variants.append(
                f"A FlowMason pipeline that {' and '.join(io_bits)}."
            )

        # Fallback: derive from stages only
        if not variants and stage_names:
            variants.append(f"Pipeline with stages: {', '.join(stage_names)}.")

        if not variants:
            continue

        output_text = json.dumps(data, ensure_ascii=False)

        for idx, desc in enumerate(variants):
            instruction = (
                "Convert this natural language description into a valid "
                "FlowMason pipeline JSON."
            )
            # Slightly vary the prompt across variants
            if idx == 1:
                instruction = (
                    "Given the description of a FlowMason pipeline, generate the "
                    "full pipeline JSON configuration."
                )
            elif idx >= 2:
                instruction = (
                    "From this high-level description, infer the complete "
                    "FlowMason pipeline JSON."
                )

            input_text = f"Name: {name}\nDescription: {desc}"

            yield {
                "instruction": instruction,
                "input": input_text,
                "output": output_text,
                "source": str(path),
                "task": "nl_to_pipeline",
            }


def make_pipeline_explanation_examples(pipelines: List[Tuple[Path, Dict]]) -> Iterable[Dict]:
    """
    Create pipeline explanation tasks.

    For each pipeline we generate multiple instruction variants pointing
    to the same reference explanation, so the model can handle different
    ways users might ask for an explanation.
    """
    for path, data in pipelines:
        name = data.get("name") or data.get("id") or path.stem
        stages = data.get("stages") or []
        if isinstance(stages, dict):
            stage_values = list(stages.values())
        else:
            stage_values = list(stages)

        stage_names = [
            s.get("name") or s.get("id")
            for s in stage_values
            if isinstance(s, dict) and (s.get("name") or s.get("id"))
        ]

        if not stage_values:
            continue

        summary_parts: List[str] = [
            f"The pipeline '{name}' runs {len(stage_values)} stages in sequence."
        ]
        if stage_names:
            summary_parts.append("The stages are: " + ", ".join(stage_names) + ".")

        output_text = " ".join(summary_parts)
        input_text = json.dumps(data, ensure_ascii=False)

        instructions = [
            "Explain what this FlowMason pipeline does in natural language.",
            "Describe, step by step, how this FlowMason pipeline processes its input.",
            "Summarize the purpose and main stages of this FlowMason pipeline.",
        ]

        for instruction in instructions:
            yield {
                "instruction": instruction,
                "input": input_text,
                "output": output_text,
                "source": str(path),
                "task": "pipeline_explanation",
            }


def chunk_text(text: str, max_chars: int = 2000) -> List[str]:
    """Naive text chunking for docs."""
    chunks: List[str] = []
    start = 0
    while start < len(text):
        end = min(len(text), start + max_chars)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end
    return chunks


def make_doc_qa_examples(docs: List[Tuple[Path, str]]) -> Iterable[Dict]:
    """Create simple Q&A examples from docs."""
    for path, text in docs:
        chunks = chunk_text(text, max_chars=1500)
        for chunk in chunks:
            # Very lightweight heuristic questions; intended as seed data.
            title = path.name.replace(".md", "")
            instruction = "Answer the user's question about FlowMason based on the provided documentation excerpt."

            # Template questions
            questions = [
                f"What does this FlowMason document '{title}' describe?",
                f"Summarize the key ideas of this FlowMason document '{title}'.",
            ]

            for q in questions:
                input_text = f"Question: {q}\n\nDocumentation:\n{chunk}"
                # For seed data we can set output to a summary placeholder; humans or a stronger model
                # can refine this later if needed.
                output_text = "Summarize the documentation and answer the question in your own words."

                yield {
                    "instruction": instruction,
                    "input": input_text,
                    "output": output_text,
                    "source": str(path),
                    "task": "fm_doc_qa_seed",
                }


def build_dataset(output_path: Path) -> None:
    """Build the combined dataset and write to JSONL."""
    pipelines = load_pipelines()
    docs = load_docs()

    os.makedirs(output_path.parent, exist_ok=True)

    records: List[Dict] = []

    records.extend(list(make_nl_to_pipeline_examples(pipelines)))
    records.extend(list(make_pipeline_explanation_examples(pipelines)))
    records.extend(list(make_doc_qa_examples(docs)))

    with output_path.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"Wrote {len(records)} records to {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build FlowMason local LLM dataset.")
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("data/flowmason_local_small.jsonl"),
        help="Output JSONL path",
    )
    args = parser.parse_args()

    build_dataset(args.output)


if __name__ == "__main__":
    main()
