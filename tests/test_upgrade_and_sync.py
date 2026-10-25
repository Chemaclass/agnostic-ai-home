import os
import pathlib
import subprocess
import tempfile
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parent.parent / "scripts" / "upgrade-and-sync.sh"

# Stub agnostic-ai: reports $FAKE_VERSION, drifts unless $FAKE_IN_SYNC, logs each sync, and
# rewrites $FAKE_TOUCH or fails with $FAKE_FAIL when asked.
FAKE_CLI = """#!/bin/sh
if [ "$1" = --version ]; then echo "agnostic-ai version $FAKE_VERSION"; exit 0; fi
case " $* " in *" --check "*) [ -n "$FAKE_IN_SYNC" ]; exit $? ;; esac
echo "sync $PWD $*" >> "$FAKE_LOG"
[ -z "$FAKE_FAIL" ] || { echo "$FAKE_FAIL" >&2; exit 1; }
[ -z "$FAKE_TOUCH" ] || echo generated > "$FAKE_TOUCH"
"""

FAKE_GLOBAL_SYNC = """#!/bin/sh
case " $* " in *" --check "*) [ -n "$FAKE_IN_SYNC" ]; exit $? ;; esac
echo "global $*" >> "$FAKE_LOG"
"""


class SessionStartSync(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = pathlib.Path(temporary.name).resolve()
        self.home = self.root / "home"
        source = self.home / ".agnostic-ai"
        source.mkdir(parents=True)
        self.write_script(source / "sync.sh", FAKE_GLOBAL_SYNC)
        bin_dir = self.root / "bin"
        bin_dir.mkdir()
        self.write_script(bin_dir / "agnostic-ai", FAKE_CLI)
        self.project = self.root / "project"
        self.project.mkdir()
        (self.project / "agnostic-ai.yaml").write_text("version: 1\n")
        (self.project / "CLAUDE.md").write_text("old\n")
        self.git("init", "-q")
        self.git("add", ".")
        self.git("-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false", "commit", "-q", "-m", "init")
        self.log = self.root / "sync.log"
        self.log.write_text("")
        self.env = dict(os.environ, HOME=str(self.home), PATH=f"{bin_dir}:{os.environ['PATH']}",
                        FAKE_VERSION="1.0.0", FAKE_LOG=str(self.log), CLAUDE_PROJECT_DIR=str(self.project))
        for variable in ["FAKE_IN_SYNC", "FAKE_TOUCH", "FAKE_FAIL"]:
            self.env.pop(variable, None)

    def write_script(self, path, body):
        path.write_text(body)
        path.chmod(0o755)

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.project), *args], check=True, capture_output=True, text=True).stdout

    def session_start(self, **env):
        result = subprocess.run([str(SCRIPT), "--session-start"], cwd=self.project, env=dict(self.env, **env),
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def syncs(self):
        return self.log.read_text().splitlines()

    def test_syncs_once_per_installed_version_and_stays_silent(self):
        self.assertEqual(self.session_start(), "")
        self.assertEqual(self.syncs(), ["global ", f"sync {self.project} sync --keep-edits"])
        self.session_start()
        self.assertEqual(len(self.syncs()), 2)
        self.session_start(FAKE_VERSION="1.1.0")
        self.assertEqual(len(self.syncs()), 4)

    def test_skips_the_write_when_already_in_sync(self):
        self.assertEqual(self.session_start(FAKE_IN_SYNC="1"), "")
        self.assertEqual(self.syncs(), [])

    def test_reports_tracked_files_the_sync_changed_without_committing(self):
        head = self.git("rev-parse", "HEAD")
        output = self.session_start(FAKE_TOUCH=str(self.project / "CLAUDE.md"))
        self.assertIn("files changed, left uncommitted: CLAUDE.md", output)
        self.assertEqual(self.git("rev-parse", "HEAD"), head)

    def test_a_failed_sync_never_fails_the_session_and_retries_next_time(self):
        output = self.session_start(FAKE_FAIL="[AAI-005] requires 0.9.0")
        self.assertIn("this project: failed: [AAI-005] requires 0.9.0", output)
        self.session_start(FAKE_FAIL="[AAI-005] requires 0.9.0")
        self.assertEqual(self.syncs().count(f"sync {self.project} sync --keep-edits"), 2)

    def test_ignores_a_directory_without_agnostic_ai(self):
        (self.project / "agnostic-ai.yaml").unlink()
        self.session_start()
        self.assertEqual(self.syncs(), ["global "])


if __name__ == "__main__":
    unittest.main()
