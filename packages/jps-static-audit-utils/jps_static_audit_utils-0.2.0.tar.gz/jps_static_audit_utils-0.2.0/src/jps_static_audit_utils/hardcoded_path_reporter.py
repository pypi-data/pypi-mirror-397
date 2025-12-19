#!/usr/bin/env python3
"""
perl_hardcoded_path_report.py

Scan Perl (.pl, .pm) files for hard-coded directory or file paths.

Read-only static analysis.
"""

from __future__ import annotations

import getpass
import logging
import os

import socket
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional

import typer

from .logging_helper import setup_logging
from .constants import (
    ABS_PATH_RE, 
    PROGRAM_NAME, 
    PROGRAM_VERSION, 
    REL_PATH_RE, 
    TIMESTAMP_FMT,
    URL_RE, 
    ENV_RE
)

from .writer import write_text, write_json, write_csv
from .finding import Finding

# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def default_outdir() -> Path:
    user = getpass.getuser()
    script = Path(__file__).stem
    ts = datetime.now().strftime(TIMESTAMP_FMT)
    return Path("/tmp") / user / PROGRAM_NAME / script / ts


def standard_header(
    *,
    infile: Optional[Path],
    indir: Optional[Path],
    report_file: Path,
    logfile: Path,
) -> str:
    lines = [
        f"Program:        {PROGRAM_NAME}",
        f"Version:        {PROGRAM_VERSION}",
        f"Timestamp:      {datetime.now().isoformat()}",
        f"User:           {getpass.getuser()}",
        f"Host:           {socket.gethostname()}",
        f"Working dir:    {os.getcwd()}",
        f"Input file:     {infile if infile else 'N/A'}",
        f"Input dir:      {indir if indir else 'N/A'}",
        f"Report file:    {report_file}",
        f"Log file:       {logfile}",
    ]
    return "\n".join(lines)


def is_perl_file(path: Path) -> bool:
    return path.suffix in {".pl", ".pm"}


def strip_inline_comment(line: str) -> str:
    return line.split("#", 1)[0] if "#" in line else line


# --------------------------------------------------------------------------- #
# Core scanning logic
# --------------------------------------------------------------------------- #

def scan_file(path: Path) -> List[Finding]:
    logging.info("Scanning file: %s", path)
    findings: List[Finding] = []
    in_pod = False

    with path.open("r", encoding="utf-8", errors="ignore") as fh:
        for lineno, raw in enumerate(fh, start=1):
            line = raw.rstrip("\n")

            # POD handling
            if line.startswith("="):
                in_pod = True
            if in_pod:
                if line.strip() == "=cut":
                    in_pod = False
                continue

            stripped = strip_inline_comment(line)
            if not stripped.strip():
                continue

            if ENV_RE.search(stripped):
                continue

            for m in ABS_PATH_RE.finditer(stripped):
                path_val = m.group(2)
                if not URL_RE.match(path_val):
                    findings.append(
                        Finding(
                            file=str(path),
                            line=lineno,
                            path=path_val,
                            path_type="absolute",
                            context=line.strip(),
                        )
                    )

            for m in REL_PATH_RE.finditer(stripped):
                findings.append(
                    Finding(
                        file=str(path),
                        line=lineno,
                        path=m.group(2),
                        path_type="relative",
                        context=line.strip(),
                    )
                )

    return findings


def collect_files(indir: Optional[Path], infile: Optional[Path]) -> Iterable[Path]:
    if infile:
        yield infile
        return

    assert indir is not None
    for root, _, files in os.walk(indir):
        for f in files:
            p = Path(root) / f
            if is_perl_file(p):
                yield p


app = typer.Typer(help="Report hard-coded file and directory paths in Perl code")


@app.command()
def scan(
    indir: Optional[Path] = typer.Option(
        None, help="Directory to scan recursively"
    ),
    infile: Optional[Path] = typer.Option(
        None, help="Single Perl file to scan"
    ),
    outdir: Optional[Path] = typer.Option(
        None, help="Output directory"
    ),
    report_file: Optional[Path] = typer.Option(
        None, help="Output report file"
    ),
    logfile: Optional[Path] = typer.Option(
        None, help="Log file"
    ),
    format: str = typer.Option(
        "text", help="Report format: text, json, csv"
    ),
) -> None:
    if not indir and not infile:
        raise typer.BadParameter("Either --indir or --infile must be provided")

    outdir = outdir or default_outdir()
    outdir.mkdir(parents=True, exist_ok=True)

    report_file = report_file or (outdir / f"{PROGRAM_NAME}.{format}")
    logfile = logfile or (outdir / f"{PROGRAM_NAME}.log")

    setup_logging(logfile)

    logging.info("Scan started")
    logging.info("Input dir: %s", indir)
    logging.info("Input file: %s", infile)

    findings: List[Finding] = []
    for f in collect_files(indir, infile):
        findings.extend(scan_file(f))

    header_text = standard_header(
        infile=infile,
        indir=indir,
        report_file=report_file,
        logfile=logfile,
    )

    header_dict = {
        "program": PROGRAM_NAME,
        "version": PROGRAM_VERSION,
        "timestamp": datetime.now().isoformat(),
        "user": getpass.getuser(),
        "host": socket.gethostname(),
        "cwd": os.getcwd(),
        "infile": str(infile) if infile else None,
        "indir": str(indir) if indir else None,
        "report_file": str(report_file),
        "logfile": str(logfile),
    }

    if format == "json":
        write_json(findings, header_dict, report_file)
    elif format == "csv":
        write_csv(findings, header_dict, report_file)
    else:
        write_text(findings, header_text, report_file)

    logging.info(f"Scan completed: {len(findings)} findings")
    typer.echo(f"Wrote report to : {report_file}")
    typer.echo(f"Wrote log file: {logfile}")


if __name__ == "__main__":
    app()
