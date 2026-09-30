#!/usr/bin/env python3
"""Block shell commands the global agreements forbid. Claude and Codex get exit 2; Cursor gets a permission reply."""
import json
import os
import re
import shlex
import sys

PUBLISHING = re.compile(r"\b(git\s+(commit|tag)|gh\s+(pr|issue|release)\s+(create|comment|edit|review))\b")
DASHES = ("\u2014", "\u2013")
SECRET_READERS = {"cat", "less", "more", "head", "tail", "bat", "strings", "xxd", "base64"}
SECRET_PATH = re.compile(r"(^|/)(\.env(?!\.(example|sample|dist|template)$)(\.[\w.-]+)?|id_(rsa|ed25519|ecdsa)[^/]*|auth\.json|credentials[^/]*|\.npmrc|\.pypirc|\.netrc)$")


def command_from(payload):
    tool_input = payload.get("tool_input") or {}
    return tool_input.get("command") or payload.get("command") or ""


def words(command):
    try:
        return shlex.split(command)
    except ValueError:
        return command.split()


def body_files(tokens):
    for flag, value in zip(tokens, tokens[1:]):
        if flag in ("--body-file", "-F", "--file"):
            yield value


def program(seg):
    """The command a segment runs, past sudo, command, env, and VAR=value prefixes."""
    for token in seg:
        name = os.path.basename(token)
        if name in ("sudo", "command", "env", "exec") or "=" in token and not token.startswith("-"):
            continue
        return name
    return ""


def unleased_force_push(seg):
    if program(seg) != "git" or "push" not in seg:
        return False
    args = seg[seg.index("push") + 1:]
    # --force disables the lease check, so it counts even next to --force-with-lease.
    if any(t == "--force" or re.fullmatch(r"-[a-zA-Z]*f[a-zA-Z]*", t) for t in args):
        return True
    return any(t.startswith("+") for t in args) and not any(t.startswith("--force-with-lease") for t in args)


def violation(command):
    tokens = words(command)
    for segment in re.split(r"&&|\|\||;|\|", command):
        seg = words(segment)
        textual = re.search(r"\bgit\s+push\b", segment) and re.search(r"(\s--force(\s|$)|\s-[a-zA-Z]*f[a-zA-Z]*(\s|$)|\s\+\S)", segment) and "--force-with-lease" not in segment
        if textual or unleased_force_push(seg):
            return "Force push without --force-with-lease. Use --force-with-lease so a newer remote commit is not overwritten."
        if program(seg) == "rm" and any(t.startswith("-") and "r" in t.lower() for t in seg[1:]) and any(ch in segment for ch in "*?"):
            return "Recursive rm with a glob. Delete explicitly identified paths after checking `git ls-files` and `git status`."
        if seg and os.path.basename(seg[0]) in SECRET_READERS and any(SECRET_PATH.search(t) for t in seg[1:]):
            return "This would print a secret file. Copy secrets between private files without printing them."
    if PUBLISHING.search(command):
        text = command
        for path in body_files(tokens):
            try:
                with open(os.path.expanduser(path), encoding="utf-8") as f:
                    text += f.read()
            except OSError:
                pass
        if any(d in text for d in DASHES):
            return "Published text contains an em or en dash. Use commas, parentheses, colons, semicolons, or a regular hyphen."
    return None


def main():
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return 0
    reason = violation(command_from(payload))
    if payload.get("hook_event_name") == "beforeShellExecution":
        # Cursor blocks the command when a permission hook prints no valid reply.
        reply = {"permission": "deny", "user_message": reason, "agent_message": reason} if reason else {"permission": "allow"}
        print(json.dumps(reply))
        return 0
    if not reason:
        return 0
    print(reason, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
