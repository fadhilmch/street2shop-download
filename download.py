"""Street2Shop dataset exporter.

Downloads the community Hugging Face copy of the Street2Shop dataset
(petr7555/street2shop) and writes the legacy on-disk layout (images +
metadata JSONs) used by the original evaluation and triplet-training
code. The dataset itself is never committed to this repository.
"""

import argparse
import sys

from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table

from downloader import CATEGORIES, DATASET_ID, export_dataset


def parse_arguments(argv=None):
    parser = argparse.ArgumentParser(
        prog="download.py",
        description="Export the Street2Shop dataset from Hugging Face "
        "to the legacy on-disk layout.",
    )
    parser.add_argument(
        "--classes",
        nargs="+",
        default=CATEGORIES,
        choices=CATEGORIES,
        metavar="CLASS",
        help="categories to export [default: all]",
    )
    parser.add_argument(
        "--split",
        choices=["train", "test", "all"],
        default="all",
        help="which protocol split(s) to export [default: all]",
    )
    parser.add_argument(
        "--image_dir",
        default="images/",
        help="output images directory [default: images/]",
    )
    parser.add_argument(
        "--meta_dir",
        default="meta/json/",
        help="output metadata directory [default: meta/json/]",
    )
    parser.add_argument(
        "--max_num_samples",
        type=int,
        default=None,
        help="maximum pairs exported per category per split",
    )
    parser.add_argument(
        "--crop",
        action="store_true",
        help="crop each street photo using the bounding box data",
    )
    parser.add_argument(
        "--report",
        default="export_report.json",
        help="path for the JSON export report [default: export_report.json]",
    )
    return parser.parse_args(argv)


def _make_progress(console):
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
        console=console,
        disable=not console.is_interactive,
    )


def _print_summary(console, report):
    images = report["images"]
    meta = report["metadata"]
    table = Table(title="Export summary", show_header=True)
    table.add_column("Metric", style="bold")
    table.add_column("Value", justify="right")
    table.add_row("Rows seen", str(meta["rows_seen"]))
    table.add_row("Invalid rows skipped", str(meta["rows_invalid"]))
    table.add_row("Images saved", str(images["saved"]))
    table.add_row("Images already on disk", str(images["skipped_existing"]))
    table.add_row("Images failed/missing", str(images["failed_or_missing"]))
    table.add_row("Crops applied", str(report["crops"]["applied"]))
    table.add_row("Crops failed (saved uncropped)", str(report["crops"]["failed"]))
    table.add_row("Metadata files written", str(meta["files_written"]))
    console.print(table)


def main(argv=None):
    args = parse_arguments(argv)
    console = Console()
    console.print(
        Panel.fit(
            f"[bold]Street2Shop exporter[/bold]\n"
            f"source: [link=https://huggingface.co/datasets/{DATASET_ID}]"
            f"{DATASET_ID}[/link] (community copy)\n"
            f"classes: {', '.join(args.classes)}\n"
            f"split: {args.split}   crop: {'on' if args.crop else 'off'}"
            + (
                f"   max/class/split: {args.max_num_samples}"
                if args.max_num_samples
                else ""
            ),
            border_style="cyan",
        )
    )
    with _make_progress(console) as progress:
        report = export_dataset(
            classes=args.classes,
            split=args.split,
            image_dir=args.image_dir,
            meta_dir=args.meta_dir,
            crop=args.crop,
            max_num_samples=args.max_num_samples,
            report_path=args.report,
            progress=progress,
        )
    _print_summary(console, report)
    console.print(f"[green]Report written to {args.report}[/green]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
