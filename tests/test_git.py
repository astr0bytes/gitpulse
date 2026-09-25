import unittest

from gitpulse.git import COMMIT_MARKER, FIELD_SEP, parse_log, split_rename


def entry(sha, author, date, subject, numstat=""):
    header = FIELD_SEP.join([sha, author, f"{author.lower()}@example.com", date, subject])
    return f"{COMMIT_MARKER}{header}\n\n{numstat}"


class SplitRenameTest(unittest.TestCase):
    def test_plain_path(self):
        self.assertEqual(split_rename("src/app.py"), ("src/app.py", "src/app.py"))

    def test_full_rename(self):
        self.assertEqual(split_rename("old.py => new.py"), ("old.py", "new.py"))

    def test_braces(self):
        self.assertEqual(split_rename("src/{core => lib}/db.py"), ("src/core/db.py", "src/lib/db.py"))

    def test_braces_empty_side(self):
        self.assertEqual(split_rename("src/{ => utils}/io.py"), ("src/io.py", "src/utils/io.py"))
        self.assertEqual(split_rename("src/{utils => }/io.py"), ("src/utils/io.py", "src/io.py"))


class ParseLogTest(unittest.TestCase):
    def test_basic_fields(self):
        raw = entry("abc123", "Alice", "2024-03-04T10:15:00+01:00", "Add parser", "10\t2\tparser.py\n")
        [commit] = parse_log(raw)
        self.assertEqual(commit.sha, "abc123")
        self.assertEqual(commit.author, "Alice")
        self.assertEqual(commit.subject, "Add parser")
        self.assertEqual(commit.date.hour, 10)
        self.assertEqual((commit.lines_added, commit.lines_deleted), (10, 2))

    def test_binary_files_count_as_zero(self):
        raw = entry("abc", "Bob", "2024-03-04T10:00:00+00:00", "Logo", "-\t-\tlogo.png\n")
        [commit] = parse_log(raw)
        self.assertEqual(commit.files[0].path, "logo.png")
        self.assertEqual(commit.lines_added, 0)

    def test_subject_with_separator_chars(self):
        raw = entry("abc", "Bob", "2024-03-04T10:00:00+00:00", "Fix a => b mapping")
        [commit] = parse_log(raw)
        self.assertEqual(commit.subject, "Fix a => b mapping")
        self.assertEqual(commit.files, [])

    def test_older_commits_follow_rename(self):
        raw = (
            entry("c3", "Alice", "2024-03-06T10:00:00+00:00", "Move", "1\t0\tsrc/{core => lib}/db.py\n")
            + entry("c2", "Alice", "2024-03-05T10:00:00+00:00", "Edit", "3\t1\tsrc/core/db.py\n")
            + entry("c1", "Alice", "2024-03-04T10:00:00+00:00", "Create", "5\t0\tsrc/core/db.py\n")
        )
        paths = [c.files[0].path for c in parse_log(raw)]
        self.assertEqual(paths, ["src/lib/db.py"] * 3)


if __name__ == "__main__":
    unittest.main()
