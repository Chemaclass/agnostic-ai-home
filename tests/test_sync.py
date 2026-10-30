import json
import os
import pathlib
import shutil
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

    def sync(self, allow_notes=False):
        result = subprocess.run([str(SCRIPT)], cwd=self.source, env=self.env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        if allow_notes:
            self.assertTrue(all(line.startswith("  note:") for line in result.stderr.splitlines()), result.stderr)
        else:
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

    def test_shared_specs_keep_each_tools_native_behavior(self):
        root = SCRIPT.parent
        for name in ["agnostic-ai.yaml", "AGNOSTIC_AI.md"]:
            shutil.copy2(root / name, self.source / name)
        for name in ["agents", "skills", "hooks"]:
            shutil.copytree(root / name, self.source / name)
        self.sync(allow_notes=True)

        claude = self.home / ".claude"
        codex = self.home / ".codex"
        for name, claude_model, codex_model, effort in [
            ("locator", "haiku", "gpt-6-luna", "low"),
            ("claim-verifier", "opus", "gpt-6.1-sol", "high"),
            ("reviewer", "opus", "gpt-6.1-sol", "high"),
        ]:
            with self.subTest(agent=name):
                native = (claude / "agents" / f"{name}.md").read_text()
                self.assertIn(f"model: {claude_model}\n", native)
                self.assertIn(f"effort: {effort}\n", native)
                self.assertIn("disallowedTools: Write, Edit, NotebookEdit", native)
                native = (codex / "agents" / f"{name}.toml").read_text()
                self.assertIn(f'model = "{codex_model}"', native)
                self.assertIn(f'model_reasoning_effort = "{effort}"', native)
                self.assertNotIn("sandbox_mode", native)

        for name in ["gh-issues", "i-have-adhd", "pr-value-audit"]:
            with self.subTest(skill=name):
                native = (claude / "skills" / name / "SKILL.md").read_text()
                self.assertIn("disable-model-invocation: true", native)
                policy = (self.home / ".agents/skills" / name / "agents/openai.yaml").read_text()
                self.assertIn("allow_implicit_invocation: false", policy)
        audit = (claude / "skills/pr-value-audit/SKILL.md").read_text()
        self.assertIn("model: opus\n", audit)
        self.assertIn("effort: xhigh\n", audit)

        for path in [claude / "settings.json", codex / "hooks.json"]:
            hooks = json.loads(path.read_text())["hooks"]
            commands = lambda event: [hook["command"] for group in hooks[event] for hook in group["hooks"]]
            self.assertTrue(any("guard-shell.py" in command for command in commands("PreToolUse")))
            self.assertTrue(any("upgrade-and-sync.sh --session-start" in command for command in commands("SessionStart")))
            self.assertIn("PreCompact", hooks)
            self.assertIn("SessionEnd", hooks)

        checked = subprocess.run([str(SCRIPT), "--check"], cwd=self.source, env=self.env, capture_output=True, text=True)
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
