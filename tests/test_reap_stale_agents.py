import os
import pathlib
import subprocess
import tempfile
import time
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parent.parent / "scripts" / "reap-stale-agents.sh"


class ReapStaleAgentsTest(unittest.TestCase):
    """State dirs only: a stub pgrep keeps the test away from real processes."""

    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp(dir="/tmp")).resolve()
        bin_dir = self.tmp / "bin"
        bin_dir.mkdir()
        stub = bin_dir / "pgrep"
        stub.write_text("#!/bin/sh\nexit 1\n")
        stub.chmod(0o755)
        self.env = dict(os.environ, TMPDIR=str(self.tmp), PATH=f"{bin_dir}:{os.environ['PATH']}")

    def tearDown(self):
        subprocess.run(["rm", "-r", str(self.tmp)], check=True)

    def state_dir(self, name, pid=None, age_seconds=7200):
        path = self.tmp / name
        path.mkdir()
        if pid is not None:
            (path / "broker.pid").write_text(str(pid))
        stamp = time.time() - age_seconds
        os.utime(path, (stamp, stamp))
        return path

    def run_script(self, *args):
        return subprocess.run(["sh", str(SCRIPT), *args], env=self.env, capture_output=True, text=True, check=True)

    def test_removes_a_state_dir_whose_broker_is_dead(self):
        dead = self.state_dir("cxc-dead", pid=999999)
        no_pid = self.state_dir("cxc-nopid")
        self.run_script()
        self.assertFalse(dead.exists())
        self.assertFalse(no_pid.exists())

    def test_keeps_a_state_dir_whose_broker_is_alive(self):
        live = self.state_dir("cxc-live", pid=os.getpid())
        self.run_script()
        self.assertTrue(live.exists())

    def test_keeps_a_fresh_state_dir(self):
        fresh = self.state_dir("cxc-fresh", age_seconds=0)
        self.run_script()
        self.assertTrue(fresh.exists())

    def test_leaves_other_dirs_alone(self):
        other = self.state_dir("not-a-broker")
        self.run_script()
        self.assertTrue(other.exists())

    def test_dry_run_changes_nothing(self):
        dead = self.state_dir("cxc-dead", pid=999999)
        result = self.run_script("--dry-run")
        self.assertTrue(dead.exists())
        self.assertIn("dry run: 1 to reap", result.stdout)


if __name__ == "__main__":
    unittest.main()
