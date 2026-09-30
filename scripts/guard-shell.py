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


WRAPPERS = {"sudo", "command", "env", "exec", "time", "nice", "nohup", "xargs"}
WRAPPER_FLAGS_WITH_VALUE = {"-u", "-g", "-n", "-I"}
GIT_OPTIONS_WITH_VALUE = {"-C", "-c", "--git-dir", "--work-tree", "--namespace"}
SHELLS = {"sh", "bash", "zsh", "dash"}


def command_words(seg):
    """The words of the command a segment runs, past wrappers such as sudo and env, their flags, and VAR=value prefixes."""
    i, wrapped = 0, False
    while i < len(seg):
        token = seg[i]
        name = os.path.basename(token)
        if name in WRAPPERS:
            wrapped, i = True, i + 1
        elif wrapped and token.startswith("-"):
            i += 2 if token in WRAPPER_FLAGS_WITH_VALUE else 1
        elif "=" in token and not token.startswith("-"):
            i += 1
        else:
            return [name] + seg[i + 1:]
    return []


def git_subcommand(args):
    i = 0
    while i < len(args):
        if args[i] in GIT_OPTIONS_WITH_VALUE:
            i += 2
        elif args[i].startswith("-"):
            i += 1
        else:
            return args[i], args[i + 1:]
    return None, []


def unleased_force_push(cmd):
    if cmd[:1] != ["git"]:
        return False
    subcommand, args = git_subcommand(cmd[1:])
    if subcommand != "push":
        return False
    # --force disables the lease check, so it counts even next to --force-with-lease.
    if any(t == "--force" or re.fullmatch(r"-[a-zA-Z]*f[a-zA-Z]*", t) for t in args):
        return True
    leases = [t[len("--force-with-lease"):] for t in args if t.startswith("--force-with-lease")]
    if "" in leases:
        return False
    leased = {branch(lease.lstrip("=").split(":")[0]) for lease in leases}
    # A lease protects the remote ref, so it must name the refspec destination.
    return any(t.startswith("+") and branch(t[1:].split(":")[-1]) not in leased for t in args)


def branch(ref):
    return ref.removeprefix("refs/heads/")


def shell_script(cmd):
    if cmd[:1] and cmd[0] in SHELLS:
        for flag, script in zip(cmd[1:], cmd[2:]):
            if re.fullmatch(r"-[a-zA-Z]*c", flag):
                return script
    return None


def violation(command):
    tokens = words(command)
    for segment in re.split(r"&&|\|\||[;|&\n()]", command):
        seg = words(segment)
        cmd = command_words(seg)
        textual = re.search(r"\bgit\s+push\b", segment) and re.search(r"(\s--force(\s|$)|\s-[a-zA-Z]*f[a-zA-Z]*(\s|$)|\s\+\S)", segment) and "--force-with-lease" not in segment
        if textual or unleased_force_push(cmd):
            return "Force push without --force-with-lease. Use --force-with-lease so a newer remote commit is not overwritten."
        if cmd[:1] == ["rm"] and any(t.startswith("-") and "r" in t.lower() for t in cmd[1:]) and any(ch in segment for ch in "*?"):
            return "Recursive rm with a glob. Delete explicitly identified paths after checking `git ls-files` and `git status`."
        if cmd[:1] and cmd[0] in SECRET_READERS and any(SECRET_PATH.search(t) for t in cmd[1:]):
            return "This would print a secret file. Copy secrets between private files without printing them."
        script = shell_script(cmd)
        if script and violation(script):
            return violation(script)
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
