"""Aggregate statistics from parsed commits."""

from collections import Counter, defaultdict
from fnmatch import fnmatch
from dataclasses import dataclass

from gitpulse.git import Commit

WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


@dataclass
class RepoStats:
    total_commits: int
    first_commit: str
    last_commit: str
    lines_added: int
    lines_deleted: int
    authors: list[dict]
    hotspots: list[dict]
    by_weekday: dict[str, int]
    by_hour: dict[int, int]


def is_excluded(path: str, patterns: list[str]) -> bool:
    name = path.rsplit("/", 1)[-1]
    return any(fnmatch(path, p) or fnmatch(name, p) for p in patterns)


def filter_paths(commits: list[Commit], patterns: list[str]) -> list[Commit]:
    """Drop file changes matching one of the glob patterns (lockfiles, generated code...)."""
    if not patterns:
        return commits
    for c in commits:
        c.files = [f for f in c.files if not is_excluded(f.path, patterns)]
    return commits


def compute_stats(commits: list[Commit], top: int = 10) -> RepoStats:
    dates = sorted(c.date for c in commits)
    return RepoStats(
        total_commits=len(commits),
        first_commit=dates[0].isoformat(),
        last_commit=dates[-1].isoformat(),
        lines_added=sum(c.lines_added for c in commits),
        lines_deleted=sum(c.lines_deleted for c in commits),
        authors=author_ranking(commits)[:top],
        hotspots=file_hotspots(commits)[:top],
        by_weekday=activity_by_weekday(commits),
        by_hour=activity_by_hour(commits),
    )


def author_ranking(commits: list[Commit]) -> list[dict]:
    data = defaultdict(lambda: {"commits": 0, "added": 0, "deleted": 0})
    for c in commits:
        entry = data[c.author]
        entry["commits"] += 1
        entry["added"] += c.lines_added
        entry["deleted"] += c.lines_deleted
    ranking = [{"author": name, **values} for name, values in data.items()]
    return sorted(ranking, key=lambda a: a["commits"], reverse=True)


def file_hotspots(commits: list[Commit]) -> list[dict]:
    """Most frequently changed files, usually good refactoring candidates."""
    changes = Counter()
    churn = Counter()
    authors = defaultdict(set)
    for c in commits:
        for f in c.files:
            changes[f.path] += 1
            churn[f.path] += f.added + f.deleted
            authors[f.path].add(c.author)
    return [
        {"path": path, "changes": count, "churn": churn[path], "authors": len(authors[path])}
        for path, count in changes.most_common()
    ]


def activity_by_weekday(commits: list[Commit]) -> dict[str, int]:
    counts = Counter(c.date.weekday() for c in commits)
    return {WEEKDAYS[i]: counts.get(i, 0) for i in range(7)}


def activity_by_hour(commits: list[Commit]) -> dict[int, int]:
    counts = Counter(c.date.hour for c in commits)
    return {h: counts.get(h, 0) for h in range(24)}
