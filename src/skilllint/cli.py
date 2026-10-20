"""CLI entry point for SkillLint."""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from skilllint import __version__
from skilllint.reporters import render_json, render_sarif, render_text, write_output
from skilllint.scanner import scan_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="skilllint",
        description="Lint AI-agent skills and instruction files for format, links, conflicts, and risky patterns.",
        epilog="Safety: static analysis only. SkillLint never executes instructions or commands found in scanned files.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)
    scan = subparsers.add_parser("scan", help="Scan a skill, instruction file, or directory")
    scan.add_argument("path", nargs="?", default=".", help="File or directory to scan (default: current directory)")
    scan.add_argument("--format", choices=("text", "json", "sarif"), default="text", help="Output format")
    scan.add_argument("--output", help="Write the selected report format to this file")
    scan.add_argument("--strict", action="store_true", help="Return exit code 1 when warnings are found")
    scan.add_argument("--exclude", action="append", default=[], metavar="GLOB", help="Exclude matching relative paths; may be repeated")
    scan.add_argument("--no-color", action="store_true", help="Disable ANSI terminal colors")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command != "scan":
        parser.error("unknown command")
    report = scan_path(args.path, excludes=args.exclude)
    color = (
        args.format == "text"
        and not args.no_color
        and sys.stdout.isatty()
        and "NO_COLOR" not in os.environ
    )
    rendered = {
        "text": lambda: render_text(report, color=color),
        "json": lambda: render_json(report),
        "sarif": lambda: render_sarif(report),
    }[args.format]()
    if args.output:
        try:
            write_output(args.output, rendered)
        except OSError as exc:
            print(f"skilllint: cannot write report ({type(exc).__name__}): {args.output}", file=sys.stderr)
            return 2
        if args.format == "text":
            print(rendered)
        else:
            print(render_text(report, color=color))
        print(f"Report written to {Path(args.output)}", file=sys.stderr)
    else:
        print(rendered)
    return report.exit_code(strict=args.strict)


if __name__ == "__main__":
    raise SystemExit(main())
