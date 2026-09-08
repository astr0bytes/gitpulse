# gitpulse

Quick statistics for a git repository: who commits, which files change the most, and when the work happens.

Only the standard library is used. `git` needs to be in your `PATH`.

## Install

```
git clone <repo-url> gitpulse
cd gitpulse
python3 main.py --help
```

Python 3.10 or later.

## Usage

```
python3 main.py /path/to/repo
python3 main.py . --since "6 months ago" --top 15
python3 main.py . --branch develop
python3 main.py . -f markdown -o REPORT.md
python3 main.py . -f json | jq '.hotspots[0]'
```

Output formats are `text` (default), `markdown` and `json`.

Hotspots are files sorted by number of commits touching them. The churn column is the sum of added and deleted lines over the period.

Authors are grouped using the repository `.mailmap` if there is one, so commits made with an old email or a misspelled name end up under the same person.
