"""
Tiny adapter for directory trees:

- ASCII tree text  -> nested dict Tree
- Tree             -> JSON / YAML
- Tree             -> ASCII tree text
- Tree / specs     -> filesystem plan (dry run)
- Tree / specs     -> real filesystem layout
- Minimal CLI interface (see bottom)

Tree representation:
    {
        "second-brain": {
            ".env": None,              # file
            "data": {                  # dir
                "raw": {
                    "apple_notes_export": {}
                }
            },
            "README.md": None,
        }
    }

Conventions:
- dict value -> directory
- None      -> file

Naming rules (ENFORCED):
1. Names are a single path segment: no "/" or "\\".
2. Names must be non-empty after trimming.
3. Names cannot be ".", "..", "...", or "…".
4. Names cannot contain tree connector / box-drawing chars:
   "├", "└", "│", "─", "|", "+", "`".
5. Inline comments are introduced by " #".
   Anything after " #" on a line is ignored (not part of the name).
6. "..." or "…" as a whole entry is treated as a placeholder and ignored.
7. Within the same parent:
   - A name cannot be both a file and a directory.
   - Conflicting re-definitions raise ValueError.
"""

from __future__ import annotations

import fnmatch
import json
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore[import-untyped]
except ImportError:  # pragma: no cover
    yaml = None  # YAML is optional

Tree = dict[str, "Tree | None"]

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

FORBIDDEN_CHARS = set("├└│─|+`")
RESERVED_NAMES = {".", "..", "...", "…"}

DEFAULT_IGNORE_PATTERNS = [
    "__pycache__",
    "*.pyc",
    ".git",
    ".venv",
    "node_modules",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "*.egg-info",
    ".DS_Store",
]


def _strip_inline_comment(name_section: str) -> str:
    """Strip inline comments starting with '#' when '#' is not the first character.

    Examples:
        "demo.txt  # example" -> "demo.txt"
        "build_processed_views.py# writes ..." -> "build_processed_views.py"
        "#config" -> "#config"  (treated as a real name)
    """
    # Normalize trailing whitespace first
    name_section = name_section.rstrip()

    idx = name_section.find("#")
    if idx > 0:
        # Treat everything from '#' onward as comment
        name_section = name_section[:idx]

    return name_section.strip()


def _find_connector(line: str) -> tuple[int, int] | None:
    """
    Find the last valid tree connector in `line`.

    Returns (prefix_len, name_start), where:
      - prefix_len is the indentation width (chars before connector)
      - name_start is the index of the first character of the entry label

    A connector is only considered valid if it appears in the "tree margin":
    the characters before it are only spaces and vertical bars. This prevents
    '+' or other characters inside comments/text from being misdetected.
    """
    candidates: list[tuple[int, int]] = []
    length = len(line)
    i = 0

    while i < length:
        ch = line[i]

        if ch in ("├", "└", "|", "+", "`"):
            prefix = line[:i]

            # Only allow whitespace or vertical bars in the margin.
            # If there's any other character, this is not a real tree connector.
            if prefix.strip(" │") != "":
                i += 1
                continue

            j = i + 1
            # Consume the run of connector dashes if present
            while j < length and line[j] in ("─", "-"):
                j += 1

            # Require a space after the connector block
            if j < length and line[j] == " ":
                candidates.append((i, j + 1))
                i = j
            else:
                i += 1
        else:
            i += 1

    if not candidates:
        return None

    connector_idx, name_start = candidates[-1]
    return connector_idx, name_start


def _ctx(context: str | None) -> str:
    return f" Context: {context}" if context else ""


def _validate_name(name: str, *, is_dir: bool, context: str | None = None) -> None:
    """Enforce strict naming rules for both parsed and programmatic trees.

    Raises ValueError on violation.
    """
    if not name:
        raise ValueError(f"Invalid empty name.{_ctx(context)}")

    if name in RESERVED_NAMES:
        raise ValueError(f"Invalid reserved name '{name}'.{_ctx(context)}")

    if "/" in name or "\\" in name:
        msg = (
            f"Name '{name}' must be a single path segment "
            f"(no '/' or '\\').{_ctx(context)}"
        )
        raise ValueError(msg)

    if any(ch in FORBIDDEN_CHARS for ch in name):
        msg = (
            f"Name '{name}' contains forbidden tree/box characters "
            f"{FORBIDDEN_CHARS}.{_ctx(context)}"
        )
        raise ValueError(msg)
    # Dots, spaces, etc. are allowed.


def _insert_child(
    parent: Tree,
    name: str,
    *,
    is_dir: bool,
    context: str | None = None,
) -> Tree | None:
    """Insert a child into parent with conflict checks.

    Returns:
        - dict node for directories
        - None for files
    Raises ValueError on type conflicts.
    """
    existing = parent.get(name)

    if existing is None:
        if is_dir:
            node: Tree = {}
            parent[name] = node
            return node
        else:
            parent[name] = None
            return None

    # Already exists:
    if is_dir:
        if isinstance(existing, dict):
            return existing  # OK: directory already present
        raise ValueError(
            f"Conflicting definitions for '{name}': already a file, now a directory."
            f"{_ctx(context)}"
        )
    else:
        if isinstance(existing, dict):
            msg = (
                f"Conflicting definitions for '{name}': already a directory, "
                f"now a file. {_ctx(context)}"
            )
            raise ValueError(msg)
        # already a file; OK
        return None


# ---------------------------------------------------------------------------
# Parsing: ASCII tree text -> Tree
# ---------------------------------------------------------------------------


def parse_ascii_tree(
    text: str,
    include_root_label: bool = True,
) -> Tree:
    """
    Parse an ASCII/Unicode 'tree' style text into a nested Tree dict.

    Behaviors:
    - Empty lines and lines starting with '#' are ignored.
    - Inline comments ' # like this' are stripped.
    - '...' or '…' as entire entry are ignored.
    - Trailing '/' => directory (value = {}).
    - Otherwise => file (value = None).
    - If include_root_label is False, the first top-level 'xxx/' line is
      treated as a visual label; its children become top-level entries.
    - Enforces naming rules + conflict detection.

    Depth heuristic:
    - Uses leading "tree art" width to approximate depth.
      For typical specs:

          root/
          ├─ a.txt
          └─ sub/
             └─ nested.txt

      children of the root label are treated as depth 1.
    """
    root: Tree = {}
    stack = [root]
    first_dir_seen = False  # first real top-level dir (e.g. root/)

    for line_no, raw in enumerate(text.splitlines(), start=1):
        original_line = raw
        line = raw.rstrip("\n")

        if not line.strip():
            continue
        if line.lstrip().startswith("#"):
            continue

        conn = _find_connector(line)
        if conn is not None:
            prefix_len, name_start = conn
            name_section = line[name_start:].strip()

            # Base depth from visual prefix: assume ~3 chars per level.
            base_depth = max(prefix_len // 3, 0)

            # If we've already seen a root label (include_root_label=True),
            # treat subsequent connector lines as children of that root.
            if first_dir_seen and include_root_label:
                depth = base_depth + 1
            else:
                depth = base_depth
        else:
            # No connector: candidate for root label or plain top-level entry.
            depth = 0
            name_section = line.strip()

            if (
                not first_dir_seen
                and name_section.endswith("/")
                and not include_root_label
            ):
                # Visual-only label, skip creating node.
                first_dir_seen = True
                continue

        name_section = _strip_inline_comment(name_section)
        if not name_section:
            continue

        if name_section in ("...", "…"):
            continue

        is_dir = name_section.endswith("/")
        name = name_section[:-1] if is_dir else name_section

        context = f"line {line_no}: {original_line!r}"
        _validate_name(name, is_dir=is_dir, context=context)

        # Clamp depth into current stack bounds
        if depth < 0:
            depth = 0
        if depth >= len(stack):
            depth = len(stack) - 1

        parent = stack[depth]
        node = _insert_child(parent, name, is_dir=is_dir, context=context)

        if is_dir:
            if node is None:
                raise RuntimeError("Directory node creation failed unexpectedly.")

            # Maintain stack for children at depth+1
            if len(stack) > depth + 1:
                stack[depth + 1] = node
                stack = stack[: depth + 2]
            else:
                stack.append(node)

            # Mark the first top-level directory we see
            if depth == 0 and not first_dir_seen:
                first_dir_seen = True
        # Files do not extend stack

    return root


# ---------------------------------------------------------------------------
# Tree <-> JSON / YAML
# ---------------------------------------------------------------------------


def _validate_tree(tree: Tree, context_prefix: str = "") -> None:
    """Validate a Tree structure against naming + type rules."""
    if not isinstance(tree, dict):
        raise ValueError("Tree root must be a dict.")

    for name, child in tree.items():
        ctx = f"{context_prefix}/{name}" if context_prefix else name
        is_dir = isinstance(child, dict)
        _validate_name(name, is_dir=is_dir, context=f"tree path '{ctx}'")

        if child is not None and not isinstance(child, dict):
            raise ValueError(
                f"Invalid node at '{ctx}': value must be dict (dir) or None (file)."
            )

        if isinstance(child, dict):
            _validate_tree(child, context_prefix=ctx)


def to_json(tree: Tree, **dumps_kwargs: Any) -> str:
    """Serialize a Tree to JSON string."""
    _validate_tree(tree)
    if "indent" not in dumps_kwargs:
        dumps_kwargs["indent"] = 2
    if "sort_keys" not in dumps_kwargs:
        dumps_kwargs["sort_keys"] = True
    return json.dumps(tree, **dumps_kwargs)


def from_json(data: str) -> Tree:
    """Parse a JSON string into a Tree."""
    obj = json.loads(data)
    if not isinstance(obj, dict):
        raise ValueError("JSON root must be an object (mapping).")
    _validate_tree(obj)
    return obj  # type: ignore[return-value]


def to_yaml(tree: Tree, **dump_kwargs: Any) -> str:
    """Serialize a Tree to YAML string."""
    _validate_tree(tree)
    if yaml is None:
        raise ImportError("PyYAML is not installed. `pip install pyyaml`.")
    if "sort_keys" not in dump_kwargs:
        dump_kwargs["sort_keys"] = True
    result: str = yaml.safe_dump(tree, **dump_kwargs)
    return result


def from_yaml(data: str) -> Tree:
    """Parse a YAML string into a Tree."""
    if yaml is None:
        raise ImportError("PyYAML is not installed. `pip install pyyaml`.")
    obj = yaml.safe_load(data)
    if not isinstance(obj, dict):
        raise ValueError("YAML root must be a mapping.")
    _validate_tree(obj)
    return obj  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Filesystem -> Tree
# ---------------------------------------------------------------------------


def _matches_any_pattern(name: str, patterns: list[str]) -> bool:
    """Check if name matches any of the glob patterns."""
    return any(fnmatch.fnmatch(name, pattern) for pattern in patterns)


def from_fs(
    root: str | Path,
    include_root_label: bool = True,
    ignore_patterns: list[str] | None = None,
) -> Tree:
    """Traverse a filesystem directory and generate a Tree spec.

    Args:
        root: Directory to traverse
        include_root_label: If True, include root dirname as top-level key
        ignore_patterns: Glob patterns to exclude. Pass None for defaults,
                        empty list [] to include everything.

    Returns:
        Tree dict representing the directory structure

    Raises:
        NotADirectoryError: If root doesn't exist or isn't a directory
    """
    root_path = Path(root).resolve()

    if not root_path.exists():
        raise NotADirectoryError(f"Path does not exist: {root_path}")
    if not root_path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {root_path}")

    # Use default patterns if None, empty list means no filtering
    if ignore_patterns is None:
        ignore_patterns = DEFAULT_IGNORE_PATTERNS

    def _scan_dir(directory: Path) -> Tree:
        result: Tree = {}
        try:
            entries = sorted(directory.iterdir(), key=lambda p: p.name)
        except PermissionError:
            return result  # Skip directories we can't read

        for entry in entries:
            name = entry.name

            # Skip if matches ignore pattern
            if _matches_any_pattern(name, ignore_patterns):
                continue

            # Skip symlinks for portability
            if entry.is_symlink():
                continue

            if entry.is_dir():
                result[name] = _scan_dir(entry)
            elif entry.is_file():
                result[name] = None
            # Skip special files (sockets, devices, etc.)

        return result

    tree = _scan_dir(root_path)

    if include_root_label:
        return {root_path.name: tree}
    return tree


# ---------------------------------------------------------------------------
# Tree -> ASCII
# ---------------------------------------------------------------------------


def to_ascii_tree(tree: Tree) -> str:
    """
    Render a Tree (nested dict) into a Unicode 'tree' view.
    Directories get '/', files do not.
    """
    _validate_tree(tree)
    lines: list[str] = []

    def walk(node: Tree, prefix: str = "") -> None:
        items = list(node.items())
        last_idx = len(items) - 1

        for i, (name, value) in enumerate(items):
            is_last = i == last_idx
            connector = "└─ " if is_last else "├─ "
            is_dir = isinstance(value, dict)
            line = f"{prefix}{connector}{name}{'/' if is_dir else ''}"
            lines.append(line)

            if is_dir and value:
                child_prefix = prefix + ("   " if is_last else "│  ")
                walk(value, child_prefix)

    walk(tree, "")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Tree -> Filesystem (plan + apply)
# ---------------------------------------------------------------------------


def plan_fs_from_tree(
    tree: Tree,
    root: str | Path,
) -> dict[str, Any]:
    """
    Compute a non-destructive plan of how the given Tree would map onto
    the filesystem under `root`.

    Returns a dict:
        {
          "root": "<absolute root path>",
          "dirs_to_create": [str, ...],
          "files_to_create": [str, ...],
          "dirs_exist": [str, ...],
          "files_exist": [str, ...],
          "conflicts": [str, ...],
        }

    All paths are relative to `root`.
    """
    _validate_tree(tree)

    root_path = Path(root).resolve()
    dirs_to_create: list[str] = []
    files_to_create: list[str] = []
    dirs_exist: list[str] = []
    files_exist: list[str] = []
    conflicts: list[str] = []

    def rel(p: Path) -> str:
        try:
            return str(p.relative_to(root_path))
        except ValueError:
            return str(p)

    def _recurse(node: Tree, base: Path) -> None:
        for name, child in node.items():
            path = base / name
            expected_dir = isinstance(child, dict)

            if path.exists():
                if path.is_dir():
                    if expected_dir:
                        dirs_exist.append(rel(path))
                        if child:
                            _recurse(child, path)
                    else:
                        conflicts.append(
                            f"Expected file but found directory at '{rel(path)}'"
                        )
                elif path.is_file():
                    if expected_dir:
                        conflicts.append(
                            f"Expected directory but found file at '{rel(path)}'"
                        )
                    else:
                        files_exist.append(rel(path))
                else:
                    conflicts.append(
                        f"Existing path is neither file nor directory at '{rel(path)}'"
                    )
            else:
                if expected_dir:
                    dirs_to_create.append(rel(path))
                    if child:
                        _recurse(child, path)
                else:
                    files_to_create.append(rel(path))

    _recurse(tree, root_path)
    return {
        "root": str(root_path),
        "dirs_to_create": dirs_to_create,
        "files_to_create": files_to_create,
        "dirs_exist": dirs_exist,
        "files_exist": files_exist,
        "conflicts": conflicts,
    }


def create_fs_from_tree(
    tree: Tree,
    root: str | Path,
    create_files: bool = True,
    exist_ok: bool = True,
) -> Path:
    """
    Materialize a Tree into a real directory structure.

    Args:
        tree: nested dict representation (validated).
        root: target root directory (created if needed).
        create_files: if False, only directories are created.
        exist_ok: passed to mkdir for directories.

    Returns:
        Path to root.
    """
    _validate_tree(tree)
    root_path = Path(root)
    root_path.mkdir(parents=True, exist_ok=True)

    def _recurse(node: Tree, base: Path) -> None:
        for name, child in node.items():
            path = base / name
            if isinstance(child, dict):
                path.mkdir(parents=True, exist_ok=exist_ok)
                _recurse(child, path)
            else:
                if create_files:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.touch(exist_ok=True)

    _recurse(tree, root_path)
    return root_path


def create_fs_from_ascii(
    ascii_text: str,
    root: str | Path,
    include_root_label: bool = True,
    create_files: bool = True,
    exist_ok: bool = True,
) -> Path:
    tree = parse_ascii_tree(ascii_text, include_root_label=include_root_label)
    return create_fs_from_tree(tree, root, create_files=create_files, exist_ok=exist_ok)


def create_fs_from_json(
    json_text: str,
    root: str | Path,
    create_files: bool = True,
    exist_ok: bool = True,
) -> Path:
    tree = from_json(json_text)
    return create_fs_from_tree(tree, root, create_files=create_files, exist_ok=exist_ok)


def create_fs_from_yaml(
    yaml_text: str,
    root: str | Path,
    create_files: bool = True,
    exist_ok: bool = True,
) -> Path:
    tree = from_yaml(yaml_text)
    return create_fs_from_tree(tree, root, create_files=create_files, exist_ok=exist_ok)


# ---------------------------------------------------------------------------
# Tiny CLI wrapper
# ---------------------------------------------------------------------------


def main() -> None:
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="Tree adapter: convert tree specs and create directory structures."
    )

    spec_group = parser.add_mutually_exclusive_group(required=True)
    spec_group.add_argument(
        "--from-ascii",
        "-A",
        metavar="PATH",
        help="Load tree spec from an ASCII tree text file.",
    )
    spec_group.add_argument(
        "--from-json",
        "-J",
        metavar="PATH",
        help="Load tree spec from a JSON file.",
    )
    spec_group.add_argument(
        "--from-yaml",
        "-Y",
        metavar="PATH",
        help="Load tree spec from a YAML file.",
    )
    spec_group.add_argument(
        "--from-fs",
        "-F",
        metavar="PATH",
        help="Generate tree spec by scanning a filesystem directory.",
    )

    parser.add_argument(
        "--root",
        "-R",
        default=".",
        help="Target root directory (default: current directory).",
    )
    parser.add_argument(
        "--no-root-label",
        action="store_true",
        help=(
            "When using --from-ascii or --from-fs, treat the root "
            "directory name as a label only (exclude from tree structure)."
        ),
    )
    parser.add_argument(
        "--ignore",
        nargs="*",
        metavar="PATTERN",
        help=(
            "Glob patterns to ignore when using --from-fs. "
            "Default: __pycache__, .git, *.pyc, .venv, node_modules, etc. "
            "Use --ignore with no args to disable default ignores."
        ),
    )
    parser.add_argument(
        "--plan",
        "-p",
        action="store_true",
        help="Print a filesystem plan (dry run).",
    )
    parser.add_argument(
        "--apply",
        "-a",
        action="store_true",
        help="Apply the spec: create directories/files under --root.",
    )
    parser.add_argument(
        "--no-files",
        action="store_true",
        help="When applying, create only directories (no files).",
    )
    parser.add_argument(
        "--print-tree",
        action="store_true",
        help="Print the normalized ASCII tree for the loaded spec.",
    )
    parser.add_argument(
        "--print-json",
        action="store_true",
        help="Print the JSON representation of the loaded spec.",
    )
    parser.add_argument(
        "--print-yaml",
        action="store_true",
        help="Print the YAML representation of the loaded spec (requires PyYAML).",
    )

    args = parser.parse_args()

    # Load Tree
    try:
        if args.from_ascii:
            text = Path(args.from_ascii).read_text(encoding="utf-8")
            tree = parse_ascii_tree(text, include_root_label=not args.no_root_label)
        elif args.from_json:
            text = Path(args.from_json).read_text(encoding="utf-8")
            tree = from_json(text)
        elif args.from_yaml:
            text = Path(args.from_yaml).read_text(encoding="utf-8")
            tree = from_yaml(text)
        elif args.from_fs:
            # args.ignore is None if not specified, [] if --ignore with no args
            ignore = args.ignore if args.ignore is not None else None
            if ignore is not None and len(ignore) == 0:
                ignore = []  # Explicit empty list disables defaults
            tree = from_fs(
                args.from_fs,
                include_root_label=not args.no_root_label,
                ignore_patterns=ignore,
            )
        else:
            parser.error("No input spec provided.")
    except Exception as e:
        print(f"Error loading spec: {e}", file=sys.stderr)
        sys.exit(1)

    # If no explicit actions requested, default to --plan
    if not any(
        [args.plan, args.apply, args.print_tree, args.print_json, args.print_yaml]
    ):
        args.plan = True

    # Execute actions
    try:
        if args.print_tree:
            print(to_ascii_tree(tree))
            print()  # spacing

        if args.print_json:
            print(to_json(tree))
            print()

        if args.print_yaml:
            if yaml is None:
                print(
                    "PyYAML is not installed; cannot print YAML.",
                    file=sys.stderr,
                )
            else:
                print(to_yaml(tree))
                print()

        if args.plan:
            plan = plan_fs_from_tree(tree, args.root)
            print(json.dumps(plan, indent=2, sort_keys=True))
            print()

        if args.apply:
            root_path = create_fs_from_tree(
                tree,
                args.root,
                create_files=not args.no_files,
                exist_ok=True,
            )
            print(f"Created structure under: {root_path}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":  # pragma: no cover
    main()
