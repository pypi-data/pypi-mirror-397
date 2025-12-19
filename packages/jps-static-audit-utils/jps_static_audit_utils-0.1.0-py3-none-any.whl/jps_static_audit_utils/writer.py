import csv
import json
import logging

from dataclasses import asdict
from pathlib import Path
from typing import List

from .finding import Finding


logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# Writers
# --------------------------------------------------------------------------- #

def write_text(
    findings: List[Finding],
    header: str,
    report_file: Path,
) -> None:
    report_file.parent.mkdir(parents=True, exist_ok=True)
    with report_file.open("w", encoding="utf-8") as fh:
        fh.write(header + "\n")
        fh.write("=" * 80 + "\n\n")

        for f in findings:
            fh.write(f"File:    {f.file}\n")
            fh.write(f"Line:    {f.line}\n")
            fh.write(f"Type:    {f.path_type}\n")
            fh.write(f"Path:    {f.path}\n")
            fh.write(f"Context: {f.context}\n")
            fh.write("-" * 60 + "\n")

    logger.info("Text report written: %s", report_file)


def write_json(
    findings: List[Finding],
    header: dict,
    report_file: Path,
) -> None:
    report_file.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "header": header,
        "findings": [asdict(f) for f in findings],
    }
    with report_file.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)

    logger.info("JSON report written: %s", report_file)


def write_csv(
    findings: List[Finding],
    header: dict,
    report_file: Path,
) -> None:
    report_file.parent.mkdir(parents=True, exist_ok=True)
    with report_file.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        for k, v in header.items():
            writer.writerow([f"# {k}", v])
        writer.writerow([])

        writer.writerow(["file", "line", "path_type", "path", "context"])
        for f in findings:
            writer.writerow(
                [f.file, f.line, f.path_type, f.path, f.context]
            )

    logger.info("CSV report written: %s", report_file)

