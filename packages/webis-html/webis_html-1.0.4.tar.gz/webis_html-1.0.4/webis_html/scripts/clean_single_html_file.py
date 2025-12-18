#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import json
import sys
from pathlib import Path

# Prefer local source checkout over any installed `webis_html` package.
# This script lives in `webis_html/scripts/`, so the repo root is 2 levels up.
_repo_root = Path(__file__).resolve().parents[2]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from webis_html.core.html_processor import HtmlProcessor
from webis_html.core.dataset_processor import process_json_folder
from webis_html.core.llm_predictor import process_predictions
from webis_html.core.content_restorer import restore_text_from_json
from webis_html.core.llm_clean import run_filter


def main() -> int:
    parser = argparse.ArgumentParser(description="Clean a single HTML file using the Webis pipeline.")
    parser.add_argument("--html", required=True, help="Path to the .html file")
    parser.add_argument("--out", required=True, help="Output directory")
    parser.add_argument(
        "--api-key",
        default=None,
        help="Optional API key for predictor/cleaner (otherwise uses env/config resolution).",
    )
    parser.add_argument(
        "--skip-llm-clean",
        action="store_true",
        help="Skip final large-model text cleaning (keeps node-level predicted_texts).",
    )
    args = parser.parse_args()

    html_path = Path(args.html)
    if not html_path.exists():
        raise SystemExit(f"HTML file not found: {html_path}")

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    if os.environ.get("LLM_PREDICTOR_DEBUG_BATCH", "").strip() in ("1", "true", "True"):
        import webis_html.core.llm_predictor as predictor
        print(f"Using llm_predictor from: {predictor.__file__}")
        print(f"BATCH_SIZE={getattr(predictor, 'BATCH_SIZE', None)} DEBUG_BATCH={getattr(predictor, 'DEBUG_BATCH', None)}")

    processor = HtmlProcessor(html_path.parent, out_dir)
    processor.process_html_file(str(html_path))

    dataset_dir = out_dir / "dataset"
    dataset_dir.mkdir(parents=True, exist_ok=True)
    process_json_folder(out_dir / "content_output", dataset_dir / "extra_datasets.json")

    try:
        with open(dataset_dir / "extra_datasets.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        total_entries = sum(len(v) for v in data.values() if isinstance(v, list))
        batch_size = int(os.environ.get("LLM_PREDICTOR_BATCH_SIZE", "20"))
        expected_requests = (total_entries + max(1, batch_size) - 1) // max(1, batch_size)
        print(f"Prepared {total_entries} nodes; batch_size={batch_size}; expected_requests≈{expected_requests}")
    except Exception:
        pass

    process_predictions(dataset_dir / "extra_datasets.json", dataset_dir / "pred_results.json", api_key=args.api_key)

    predicted_dir = out_dir / "predicted_texts"
    predicted_dir.mkdir(parents=True, exist_ok=True)
    restore_text_from_json(dataset_dir / "pred_results.json", predicted_dir)

    if args.skip_llm_clean:
        print(f"Done. Output: {predicted_dir}")
        return 0

    filtered_dir = out_dir / "filtered_texts"
    filtered_dir.mkdir(parents=True, exist_ok=True)
    run_filter(str(predicted_dir), str(filtered_dir), "deepseek", api_key=args.api_key)
    print(f"Done. Output: {filtered_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
