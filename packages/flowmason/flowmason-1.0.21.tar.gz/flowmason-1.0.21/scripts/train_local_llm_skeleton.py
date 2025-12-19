#!/usr/bin/env python3
"""
Skeleton script for fine-tuning a small local LLM for FlowMason.

This is a *template* only: it assumes you run it on a GPU machine with
the necessary libraries installed (transformers, datasets, peft, trl).

Steps:
1. Build the dataset locally from the repo:
   python scripts/build_local_llm_dataset.py -o data/flowmason_local_small.jsonl

2. Copy `data/flowmason_local_small.jsonl` and this script to a GPU box.

3. Install training dependencies:
   pip install transformers datasets peft trl accelerate bitsandbytes

4. Run this script with your chosen base model name.

After training, you'll get a Hugging Face-style model directory which you
can then convert to GGUF for llama.cpp and run via LlamaCppAdapter.
"""

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Skeleton trainer for FlowMason local LLM.")
    parser.add_argument(
        "--base-model",
        type=str,
        required=True,
        help="Base HF model id (e.g. meta-llama/... or qwen/... 3B instruct)",
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=Path("data/flowmason_local_small.jsonl"),
        help="Path to JSONL dataset built from this repo.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("out/flowmason-local-small"),
        help="Output directory for the fine-tuned model.",
    )
    args = parser.parse_args()

    print(
        "\nThis script is a skeleton. Run it on a GPU machine with:\n"
        "  pip install transformers datasets peft trl accelerate bitsandbytes\n"
        "and then implement the actual training loop using the libraries above.\n"
    )
    print(f"Suggested next steps:")
    print(f"- Base model: {args.base_model}")
    print(f"- Dataset:    {args.data}")
    print(f"- Output dir: {args.out_dir}")
    print(
        "\nHigh-level training outline:\n"
        "1) Load dataset from JSONL with `datasets.load_dataset('json', data_files=str(args.data))`.\n"
        "2) Load tokenizer + model from `args.base_model` with transformers.\n"
        "3) Apply QLoRA via PEFT (LoraConfig + get_peft_model).\n"
        "4) Use TRL's SFTTrainer or a standard Trainer to fine-tune on the instruction-style data.\n"
        "5) Save the merged model to `args.out_dir`.\n"
        "\nOnce trained, convert to GGUF with llama.cpp and quantize to Q4_K_M.\n"
    )


if __name__ == "__main__":
    main()

