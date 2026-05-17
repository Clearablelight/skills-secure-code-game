"""
parser.py — Command parsing for shellbound.

Maps typed shell-like commands to structured action tuples.
"""
from __future__ import annotations
import re
import shlex
from typing import Optional


class Action:
    __slots__ = ("verb", "args", "raw")

    def __init__(self, verb: str, args: list[str], raw: str) -> None:
        self.verb = verb
        self.args = args
        self.raw  = raw

    def first_arg(self) -> Optional[str]:
        return self.args[0] if self.args else None

    def __repr__(self) -> str:
        return f"Action(verb={self.verb!r}, args={self.args!r})"


_DIRECTION_ALIASES: dict[str, str] = {
    "n": "north", "s": "south", "e": "east", "w": "west",
    "north": "north", "south": "south", "east": "east", "west": "west",
}


def parse(raw_input: str) -> Action:
    raw = raw_input.strip()
    if not raw:
        return Action("noop", [], raw)

    try:
        tokens = shlex.split(raw)
    except ValueError:
        tokens = raw.split()

    if not tokens:
        return Action("noop", [], raw)

    verb = tokens[0].lower()
    rest = tokens[1:]

    if verb in ("noop",):
        return Action("noop", [], raw)

    if verb in ("quit", "exit", "q"):
        return Action("quit", [], raw)

    if verb in ("help", "man", "?"):
        return Action("help", [], raw)

    if verb in ("status", "whoami", "stat"):
        return Action("status", [], raw)

    if verb == "pwd":
        return Action("pwd", [], raw)

    if verb == "clear":
        return Action("clear", [], raw)

    if verb in ("ls", "dir", "ll", "la"):
        return Action("ls", [], raw)

    if verb == "cd":
        if not rest:
            return Action("error", ["cd requires a direction (north/south/east/west)"], raw)
        direction = _DIRECTION_ALIASES.get(rest[0].lower())
        if direction is None:
            return Action("error", [f"Unknown direction: '{rest[0]}'. Use north/south/east/west."], raw)
        return Action("cd", [direction], raw)

    if verb in ("rm", "kill", "attack", "del", "delete"):
        if not rest:
            return Action("error", ["rm requires an enemy name (e.g. rm goblin)"], raw)
        target = rest[0].lower()
        return Action("rm", [target], raw)

    if verb in ("cat", "use", "read", "open"):
        if not rest:
            return Action("error", ["cat requires an item name (e.g. cat scroll)"], raw)
        item = rest[0].lower()
        return Action("cat", [item], raw)

    if verb == "grep":
        args_clean = [a for a in rest if not a.startswith("-") and a not in (".", "*")]
        if not args_clean:
            return Action("error", ["grep requires a search pattern (e.g. grep key)"], raw)
        pattern = args_clean[0].lower()
        return Action("grep", [pattern], raw)

    if verb == "find":
        name_arg = _extract_find_name(rest)
        if name_arg is None:
            return Action("error", ['Usage: find . -name "<item>"'], raw)
        return Action("find", [name_arg.lower()], raw)

    if verb == "chmod":
        target_tokens = [t for t in rest if not t.startswith("-")]
        non_octal = [t for t in target_tokens if not re.fullmatch(r"[0-7]+", t)]
        target = non_octal[0].lower() if non_octal else None
        if target is None:
            return Action("error", ["Usage: chmod 777 door"], raw)
        return Action("chmod", [target], raw)

    if verb in ("pickup", "take", "get"):
        if not rest:
            return Action("error", [f"{verb} requires an item name"], raw)
        return Action("pickup", [rest[0].lower()], raw)

    if verb in ("look", "examine", "x", "l"):
        target = rest[0].lower() if rest else ""
        return Action("look", [target], raw)

    if verb in ("inventory", "inv", "i", "bag", "items"):
        return Action("inventory", [], raw)

    return Action("unknown", [verb], raw)


def _extract_find_name(tokens: list[str]) -> Optional[str]:
    for i, tok in enumerate(tokens):
        if tok in ("-name", "--name") and i + 1 < len(tokens):
            val = tokens[i + 1]
            val = val.strip('"\'')
            return val if val else None
    candidates = [t for t in tokens if not t.startswith("-") and t not in (".", "*", "**")]
    return candidates[0].strip('"\'' ) if len(candidates) == 1 else None
