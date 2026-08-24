"""Read commit history through `git log --numstat`."""

import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

COMMIT_MARKER = "\x1e"
FIELD_SEP = "\x1f"
LOG_FORMAT = COMMIT_MARKER + FIELD_SEP.join(["%H", "%an", "%ae", "%aI", "%s"])


class GitError(Exception):
    pass


@dataclass
class FileChange:
    path: str
    added: int
    deleted: int


@dataclass
class Commit:
    sha: str
    author: str
    email: str
    date: datetime
    subject: str
    files: list[FileChange] = field(default_factory=list)

    @property
    def lines_added(self) -> int:
        return sum(f.added for f in self.files)

    @property
    def lines_deleted(self) -> int:
        return sum(f.deleted for f in self.files)


def run_git(repo: Path, *args: str) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
            errors="replace",
        )
    except FileNotFoundError:
        raise GitError("git executable not found") from None
    except subprocess.CalledProcessError as exc:
        raise GitError(exc.stderr.strip() or "git command failed") from None
    return result.stdout


def read_commits(repo: Path, branch: str = "HEAD", since: str | None = None) -> list[Commit]:
    args = ["log", branch, "--no-merges", "--numstat", f"--format={LOG_FORMAT}"]
    if since:
        args.append(f"--since={since}")
    return parse_log(run_git(repo, *args))


def parse_log(raw: str) -> list[Commit]:
    commits = []
    for block in raw.split(COMMIT_MARKER):
        if not block.strip():
            continue
        header, _, body = block.partition("\n")
        sha, author, email, date, subject = header.split(FIELD_SEP, 4)
        commit = Commit(sha, author, email, datetime.fromisoformat(date), subject)
        for line in body.splitlines():
            parts = line.split("\t")
            if len(parts) != 3:
                continue
            added, deleted, path = parts
            # binary files are reported as "-"
            commit.files.append(
                FileChange(path, int(added) if added != "-" else 0, int(deleted) if deleted != "-" else 0)
            )
        commits.append(commit)
    return commits
