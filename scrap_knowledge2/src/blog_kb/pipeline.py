from __future__ import annotations

import argparse
import json

import uvicorn

from .api import app
from .service import run_pipeline, run_preprocess, run_scrape


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Blog KB scraping and preprocessing pipeline")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run scrape + preprocess")
    run_parser.add_argument("--max-per-source", type=int, default=10)

    scrape_parser = subparsers.add_parser("scrape", help="Only scrape and store raw data")
    scrape_parser.add_argument("--max-per-source", type=int, default=10)

    subparsers.add_parser("preprocess", help="Only preprocess latest raw data")

    serve_parser = subparsers.add_parser("serve", help="Run the FastAPI service")
    serve_parser.add_argument("--host", default="127.0.0.1")
    serve_parser.add_argument("--port", type=int, default=8000)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "run":
        result = run_pipeline(max_per_source=args.max_per_source)
    elif args.command == "scrape":
        result = {"raw": run_scrape(max_per_source=args.max_per_source)}
    elif args.command == "serve":
        uvicorn.run(app, host=args.host, port=args.port)
        return
    else:
        result = {"processed": run_preprocess()}
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
