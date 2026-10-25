import os
import signal
import time
import pathlib
import subprocess
import tempfile
import unittest

# A pre-commit hook sets GIT_DIR and friends, which would point these repos at the outer one.
CLEAN_ENV = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}

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
[ -z "$FAKE_SLOW" ] || sleep "$FAKE_SLOW"
"""


class StubbedTools(unittest.TestCase):
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
        self.env = dict(CLEAN_ENV, HOME=str(self.home), PATH=f"{bin_dir}:{CLEAN_ENV['PATH']}",
                        FAKE_VERSION="1.0.0", FAKE_LOG=str(self.log), CLAUDE_PROJECT_DIR=str(self.project))
        for variable in ["FAKE_IN_SYNC", "FAKE_TOUCH", "FAKE_FAIL", "FAKE_SLOW"]:
            self.env.pop(variable, None)

    def write_script(self, path, body):
        path.write_text(body)
        path.chmod(0o755)

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.project), *args], check=True, capture_output=True, text=True, env=CLEAN_ENV).stdout

    def session_start(self, **env):
        result = subprocess.run([str(SCRIPT), "--session-start"], cwd=self.project, env=dict(self.env, **env),
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def syncs(self):
        return self.log.read_text().splitlines()


class SessionStartSync(StubbedTools):
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

    def test_reports_a_rewrite_of_a_file_that_was_already_dirty(self):
        (self.project / "CLAUDE.md").write_text("mine\n")
        output = self.session_start(FAKE_TOUCH=str(self.project / "CLAUDE.md"))
        self.assertIn("files changed, left uncommitted: CLAUDE.md", output)

    def test_never_syncs_a_worktree(self):
        worktree = self.root / "feature"
        self.git("worktree", "add", "-q", str(worktree))
        self.session_start(CLAUDE_PROJECT_DIR=str(worktree))
        self.assertEqual(self.syncs(), ["global "])
        self.assertEqual(subprocess.run(["git", "-C", str(worktree), "status", "--short"], capture_output=True, text=True, env=CLEAN_ENV).stdout, "")

    def test_never_syncs_the_home_repo(self):
        source = self.home / ".agnostic-ai"
        (source / "agnostic-ai.yaml").write_text("version: 1\n")
        subprocess.run(["git", "init", "-q", str(source)], check=True, env=CLEAN_ENV)
        self.session_start(CLAUDE_PROJECT_DIR=str(source))
        self.assertEqual(self.syncs(), ["global "])

    def test_skips_silently_while_another_session_holds_the_lock(self):
        lock = self.home / ".agnostic-ai/state/synced-versions/.lock"
        lock.mkdir(parents=True)
        self.assertEqual(self.session_start(), "")
        self.assertEqual(self.syncs(), [])
        self.assertTrue(lock.is_dir())

    def test_a_terminated_hook_stops_before_the_project_sync_and_releases_its_lock(self):
        hook = subprocess.Popen([str(SCRIPT), "--session-start"], cwd=self.project, env=dict(self.env, FAKE_SLOW="1"),
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        deadline = time.time() + 10
        while self.syncs() != ["global "] and time.time() < deadline:
            time.sleep(0.05)
        hook.send_signal(signal.SIGTERM)
        self.assertEqual(hook.wait(timeout=10), 0)
        hook.stdout.close()
        hook.stderr.close()
        self.assertEqual(self.syncs(), ["global "])
        self.assertFalse((self.home / ".agnostic-ai/state/synced-versions/.lock").exists())

    def test_a_stamp_for_another_path_does_not_count(self):
        self.session_start()
        stamps = list((self.home / ".agnostic-ai/state/synced-versions").glob("[0-9]*"))
        for stamp in stamps:
            stamp.write_text("1.0.0\n/some/other/path\n")
        self.session_start()
        self.assertEqual(len(self.syncs()), 4)


class SyncEverything(StubbedTools):

    def setUp(self):
        super().setUp()
        self.code = self.root / "code"
        self.make_repo(self.code)
        for name in ["a", "org/b", "org/deep/c", "node_modules/x", "org/b-wt-1"]:
            self.make_repo(self.code / name)
        self.make_repo(self.code / "tool", tool=True)
        subprocess.run(["git", "-C", str(self.code / "org/b"), "worktree", "add", "-q", str(self.code / "org/feature")],
                       check=True, capture_output=True, env=CLEAN_ENV)
        self.env["AGNOSTIC_AI_PROJECTS"] = str(self.code)

    def make_repo(self, path, tool=False):
        path.mkdir(parents=True, exist_ok=True)
        (path / "agnostic-ai.yaml").write_text("version: 1\n")
        if tool:
            (path / "cmd/agnostic-ai").mkdir(parents=True)
        run = lambda *args: subprocess.run(["git", "-C", str(path), *args], check=True, capture_output=True, env=CLEAN_ENV)
        run("init", "-q")
        run("add", "agnostic-ai.yaml")
        run("-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false", "commit", "-q", "-m", "init")

    def run_all(self, *args):
        return subprocess.run([str(SCRIPT), "--no-upgrade", *args], env=self.env, capture_output=True, text=True)

    def synced_dirs(self):
        return sorted(line.split(" ")[1] for line in self.syncs() if line.startswith("sync "))

    def test_finds_main_checkouts_up_to_two_levels_below_the_root(self):
        result = self.run_all()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.synced_dirs(), sorted([str(self.code), str(self.code / "a"), str(self.code / "org/b")]))
        self.assertIn("global setup", result.stdout)

    def test_dry_run_writes_nothing(self):
        result = self.run_all("--dry-run")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("would sync", result.stdout)
        self.assertEqual(self.syncs(), [])
        self.assertFalse((self.home / ".agnostic-ai/state/synced-versions").exists())


if __name__ == "__main__":
    unittest.main()
