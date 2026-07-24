#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow running without installing the package
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from loguru import logger

from quantinvesting.data.clean import CleanPipeline, QualityChecker
from quantinvesting.data.download import DailyDownloader, FinancialDownloader, MetaDownloader
from quantinvesting.data.download.index import IndexDownloader
from quantinvesting.data.qlib_dump import QlibDumper
from quantinvesting.utils.config import load_config


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Quantinvesting data pipeline CLI")
    p.add_argument("--config", default=None, help="Path to configs/data.yaml")
    p.add_argument(
        "--execute",
        action="store_true",
        help="Actually call APIs / write outputs. Default is dry-run.",
    )

    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("meta", help="Download stock_basic / trade_cal / industry")
    sub.add_parser("daily", help="Download daily / daily_basic / adj_factor by trade_date")
    sub.add_parser("fina", help="Download financial VIP tables by report period")
    sub.add_parser("index", help="Download index daily & weights")
    sub.add_parser("all-download", help="meta -> daily -> fina -> index (dry-run by default)")
    sub.add_parser("clean", help="Run clean pipeline skeleton")
    sub.add_parser("qa", help="Run quality checks on raw data")
    sub.add_parser("dump-qlib", help="Dump clean data to qlib provider (skeleton)")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    cfg = load_config(args.config)
    dry_run = not args.execute

    if dry_run:
        logger.info("DRY-RUN mode (pass --execute to download/write)")

    if args.cmd == "meta":
        MetaDownloader(cfg).run(dry_run=dry_run)
    elif args.cmd == "daily":
        DailyDownloader(cfg).run(dry_run=dry_run)
    elif args.cmd == "fina":
        FinancialDownloader(cfg).run(dry_run=dry_run)
    elif args.cmd == "index":
        IndexDownloader(cfg).run(dry_run=dry_run)
    elif args.cmd == "all-download":
        MetaDownloader(cfg).run(dry_run=dry_run)
        DailyDownloader(cfg).run(dry_run=dry_run)
        FinancialDownloader(cfg).run(dry_run=dry_run)
        IndexDownloader(cfg).run(dry_run=dry_run)
    elif args.cmd == "clean":
        CleanPipeline(cfg).run(dry_run=dry_run)
    elif args.cmd == "qa":
        QualityChecker(cfg).run()
    elif args.cmd == "dump-qlib":
        QlibDumper(cfg).run(dry_run=dry_run)
    else:
        raise SystemExit(f"unknown command: {args.cmd}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
