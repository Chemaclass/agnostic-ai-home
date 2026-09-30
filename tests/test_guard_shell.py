import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parent.parent / "scripts" / "guard-shell.py"

BLOCKED = [
    "git push --force",
    "git push -f origin main",
    "git push origin +main",
    "git status && git push --force",
    "git push --force-with-lease && git push --force",
    "git -C repo push --force",
    'bash -c "git push --force origin main"',
    "git -c push.default=current push -f",
    "git push --force-with-lease --force",
    "sudo rm -rf build/*",
    "/bin/rm -rf build/*",
    "rm -rf build/*",
    "rm -r ./*.tmp",
    "cat .env",
    "cat .env.local",
    "head ~/.ssh/id_ed25519",
    "less ~/.codex/auth.json",
    'git commit -m "fix \u2014 the bug"',
    'gh pr create --title t --body "one \u2013 two"',
]

ALLOWED = [
    "git push --force-with-lease",
    "git push origin main",
    "git push --follow-tags",
    "git push --force-with-lease=main origin +main",
    "git -C repo push origin main",
    "git log --format=%H -- push",
    "rm -rf build",
    "rm *.log",
    "cat .env.example",
    "cat README.md",
    'git commit -m "fix - the bug"',
    'echo "not published \u2014 fine"',
]


def run(command, event="PreToolUse"):
    payload = {"hook_event_name": event, "tool_input": {"command": command}}
    return subprocess.run([sys.executable, str(SCRIPT)], input=json.dumps(payload), capture_output=True, text=True)


class ClaudeAndCodex(unittest.TestCase):
    def test_blocks(self):
        for command in BLOCKED:
            with self.subTest(command=command):
                result = run(command)
                self.assertEqual(result.returncode, 2)
                self.assertTrue(result.stderr.strip())

    def test_allows(self):
        for command in ALLOWED:
            with self.subTest(command=command):
                self.assertEqual(run(command).returncode, 0)

    def test_reads_dashes_from_a_body_file(self):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as body:
            body.write("Summary \u2014 details\n")
        self.addCleanup(pathlib.Path(body.name).unlink)
        self.assertEqual(run(f"gh pr create --title t --body-file {body.name}").returncode, 2)

    def test_ignores_invalid_json(self):
        result = subprocess.run([sys.executable, str(SCRIPT)], input="not json", capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)


class Cursor(unittest.TestCase):
    def reply(self, command):
        result = run(command, event="beforeShellExecution")
        self.assertEqual(result.returncode, 0)
        return json.loads(result.stdout)

    def test_denies_with_a_reason(self):
        reply = self.reply("git push --force")
        self.assertEqual(reply["permission"], "deny")
        self.assertIn("--force-with-lease", reply["agent_message"])

    def test_allows_explicitly(self):
        self.assertEqual(self.reply("git status"), {"permission": "allow"})


if __name__ == "__main__":
    unittest.main()
