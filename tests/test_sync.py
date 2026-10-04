import os
import pathlib
import subprocess
import tempfile
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parent.parent / "sync.sh"


class GlobalSync(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.home = pathlib.Path(temporary.name)
        self.source = self.home / ".agnostic-ai"
        self.source.mkdir()
        (self.source / "agnostic-ai.yaml").write_text("targets: [gemini]\n")
        (self.source / "AGNOSTIC_AI.md").write_text("Read the code before editing.\n")
        self.env = dict(os.environ, HOME=str(self.home), AGNOSTIC_AI_HOME=str(self.source))
        for variable in ["GEMINI_CLI_HOME", "CODEX_HOME", "CLAUDE_CONFIG_DIR"]:
            self.env.pop(variable, None)

    def sync(self):
        result = subprocess.run([str(SCRIPT)], cwd=self.source, env=self.env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stderr, "")

    def test_uses_the_home_config_targets(self):
        self.sync()
        content = (self.home / ".gemini/GEMINI.md").read_text()
        self.assertIn("Read the code before editing.", content)
        self.assertFalse((self.home / ".claude").exists())

    def test_legacy_targets_can_select_a_tool_outside_the_home_config(self):
        local = self.source / "local"
        local.mkdir()
        (local / "targets").write_text("codex\n")
        self.sync()
        content = (self.home / ".codex/AGENTS.md").read_text()
        self.assertIn("Read the code before editing.", content)
        self.assertFalse((self.home / ".gemini").exists())
