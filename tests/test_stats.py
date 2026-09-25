import unittest
from datetime import datetime, timezone

from gitpulse.git import Commit, FileChange
from gitpulse.stats import (
    activity_by_hour,
    activity_by_weekday,
    author_ranking,
    compute_stats,
    file_hotspots,
    filter_paths,
)


def make_commit(author, day, hour, files):
    date = datetime(2024, 3, day, hour, 0, tzinfo=timezone.utc)
    return Commit(f"{author}{day}{hour}", author, f"{author}@example.com", date, "msg",
                  [FileChange(path, added, deleted) for path, added, deleted in files])


class StatsTest(unittest.TestCase):
    def setUp(self):
        # 2024-03-04 is a Monday
        self.commits = [
            make_commit("alice", 4, 9, [("app.py", 10, 0), ("poetry.lock", 300, 120)]),
            make_commit("alice", 5, 14, [("app.py", 4, 2)]),
            make_commit("bob", 5, 14, [("app.py", 1, 1), ("README.md", 5, 0)]),
        ]

    def test_author_ranking(self):
        ranking = author_ranking(self.commits)
        self.assertEqual([a["author"] for a in ranking], ["alice", "bob"])
        self.assertEqual(ranking[0]["commits"], 2)
        self.assertEqual(ranking[0]["added"], 314)

    def test_hotspots(self):
        top = file_hotspots(self.commits)[0]
        self.assertEqual(top["path"], "app.py")
        self.assertEqual(top["changes"], 3)
        self.assertEqual(top["churn"], 18)
        self.assertEqual(top["authors"], 2)

    def test_activity(self):
        self.assertEqual(activity_by_weekday(self.commits)["Mon"], 1)
        self.assertEqual(activity_by_weekday(self.commits)["Tue"], 2)
        self.assertEqual(activity_by_hour(self.commits)[14], 2)
        self.assertEqual(len(activity_by_hour(self.commits)), 24)

    def test_filter_paths(self):
        commits = filter_paths(self.commits, ["*.lock"])
        paths = {f.path for c in commits for f in c.files}
        self.assertNotIn("poetry.lock", paths)
        self.assertEqual(len(commits), 3)

    def test_compute_stats(self):
        stats = compute_stats(self.commits, top=1)
        self.assertEqual(stats.total_commits, 3)
        self.assertEqual(len(stats.authors), 1)
        self.assertEqual(stats.first_commit[:10], "2024-03-04")
        self.assertEqual(stats.lines_added, 320)


if __name__ == "__main__":
    unittest.main()
