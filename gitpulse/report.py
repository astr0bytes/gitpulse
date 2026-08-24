"""Render statistics as plain text, Markdown or JSON."""

import json
from dataclasses import asdict

from gitpulse.stats import RepoStats

BAR_WIDTH = 30


def _bar(value: int, maximum: int) -> str:
    if maximum == 0:
        return ""
    return "#" * round(value / maximum * BAR_WIDTH)


def render_text(stats: RepoStats) -> str:
    out = [
        "=== gitpulse ===",
        f"Commits : {stats.total_commits}",
        f"Period  : {stats.first_commit[:10]} to {stats.last_commit[:10]}",
        f"Lines   : +{stats.lines_added} / -{stats.lines_deleted}",
        "",
        "--- Authors ---",
    ]
    for a in stats.authors:
        out.append(f"{a['author'][:28]:28} {a['commits']:6} commits  +{a['added']}/-{a['deleted']}")

    out += ["", "--- Hotspots (most changed files) ---"]
    for h in stats.hotspots:
        out.append(f"{h['changes']:5}x  churn={h['churn']:<7} authors={h['authors']:<3} {h['path']}")

    out += ["", "--- Activity by weekday ---"]
    peak = max(stats.by_weekday.values())
    for day, count in stats.by_weekday.items():
        out.append(f"{day}  {count:5}  {_bar(count, peak)}")

    out += ["", "--- Activity by hour ---"]
    peak = max(stats.by_hour.values())
    for hour, count in stats.by_hour.items():
        out.append(f"{hour:02}h  {count:5}  {_bar(count, peak)}")
    return "\n".join(out)


def render_markdown(stats: RepoStats) -> str:
    out = [
        "# gitpulse report",
        "",
        f"- **Commits**: {stats.total_commits}",
        f"- **Period**: {stats.first_commit[:10]} to {stats.last_commit[:10]}",
        f"- **Lines**: +{stats.lines_added} / -{stats.lines_deleted}",
        "",
        "## Authors",
        "",
        "| Author | Commits | Added | Deleted |",
        "|---|---:|---:|---:|",
    ]
    out += [f"| {a['author']} | {a['commits']} | {a['added']} | {a['deleted']} |" for a in stats.authors]
    out += ["", "## Hotspots", "", "| File | Changes | Churn | Authors |", "|---|---:|---:|---:|"]
    out += [f"| `{h['path']}` | {h['changes']} | {h['churn']} | {h['authors']} |" for h in stats.hotspots]
    out += ["", "## Activity by weekday", "", "| Day | Commits |", "|---|---:|"]
    out += [f"| {d} | {c} |" for d, c in stats.by_weekday.items()]
    return "\n".join(out) + "\n"


def render_json(stats: RepoStats) -> str:
    return json.dumps(asdict(stats), indent=2, ensure_ascii=False)


RENDERERS = {
    "text": render_text,
    "markdown": render_markdown,
    "json": render_json,
}
