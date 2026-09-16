#!/usr/bin/env python3
"""gitpulse - commit statistics and hotspots for a git repository."""

import argparse
import sys
from pathlib import Path

from gitpulse import __version__
from gitpulse.git import GitError, read_commits
from gitpulse.report import RENDERERS
from gitpulse.stats import compute_stats, filter_paths


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="gitpulse", description=__doc__)
    parser.add_argument("repo", nargs="?", default=".", type=Path, help="path to the repository")
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("--since", help="e.g. '3 months ago', '2025-01-01'")
    parser.add_argument("--branch", default="HEAD")
    parser.add_argument("-x", "--exclude", action="append", default=[], metavar="GLOB",
                        help="ignore matching paths, e.g. '*.lock' (repeatable)")
    parser.add_argument("--top", type=int, default=10, help="number of entries per ranking")
    parser.add_argument("-f", "--format", choices=sorted(RENDERERS), default="text")
    parser.add_argument("-o", "--output", type=Path, help="write the report to a file")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        commits = read_commits(args.repo, branch=args.branch, since=args.since)
    except GitError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if not commits:
        print("No commits found.", file=sys.stderr)
        return 1

    commits = filter_paths(commits, args.exclude)
    stats = compute_stats(commits, top=args.top)
    output = RENDERERS[args.format](stats)

    if args.output:
        args.output.write_text(output)
        print(f"Report written to {args.output}")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
