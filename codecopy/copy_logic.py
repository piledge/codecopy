#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 27.07.2025 at 17:52

@author: piledge
@source: phil
"""

import fnmatch
import os
from pathlib import Path
import pyperclip
import tiktoken
from io import StringIO
import tokenize

RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RESET = "\033[0m"

EXCLUDE_DIRS_DEFAULT = ["migrations", "__pycache__", "node_modules", ".git", ".idea", ".venv", "venv", ]
EXCLUDE_SUFFIXES_DEFAULT = (".dist", ".build", ".onefile-build")

THRES1_TOKEN = 12500
THRES2_TOKEN = 16000


def is_valid_file(file_path: Path, extensions=None, exclude_files=None):
    if file_path.name == '.gitignore':
        return False
    if file_path.suffix.lower() in ('.ico', '.exe'):
        return False
    if extensions and file_path.suffix not in extensions:
        return False
    if exclude_files and any(fnmatch.fnmatch(file_path.name, pat) for pat in exclude_files):
        return False
    return True


def strip_comments(lines: list[str]) -> list[str]:
    source = "".join(lines)
    kept = []
    for tok in tokenize.generate_tokens(StringIO(source).readline):
        if tok.type == tokenize.COMMENT:
            continue
        kept.append(tok)
    cleaned_code = tokenize.untokenize(kept)
    return cleaned_code.splitlines()


def collect_files_from_path(path: Path, extensions=None, exclude_dirs=None, exclude_files=None):
    collected_files = []
    if path.is_file():
        if is_valid_file(path, extensions, exclude_files):
            collected_files.append(path)
    else:
        for root, dirs, files in os.walk(path):
            dirs[:] = [
                d for d in dirs
                if d.lower() not in EXCLUDE_DIRS_DEFAULT
                   and (exclude_dirs is None or d not in exclude_dirs)
                   and not any(d.lower().endswith(suffix) for suffix in EXCLUDE_SUFFIXES_DEFAULT)
            ]
            for file in files:
                file_path = Path(root) / file
                if is_valid_file(file_path, extensions, exclude_files):
                    collected_files.append(file_path)
    return collected_files


def build_directory_tree(roots, extensions=None, exclude_dirs=None, exclude_files=None):
    if not isinstance(roots, (list, tuple)):
        roots = [roots]
    tree_lines = []

    def recurse(dir_path: Path, prefix=""):
        if not dir_path.is_dir():
            return
        entries = []
        for entry in sorted(dir_path.iterdir()):
            if entry.is_dir():
                name = entry.name
                if (
                        name.lower() in EXCLUDE_DIRS_DEFAULT
                        or (exclude_dirs and name in exclude_dirs)
                        or any(name.lower().endswith(suffix) for suffix in EXCLUDE_SUFFIXES_DEFAULT)
                ):
                    continue
                entries.append(entry)
            else:
                if not is_valid_file(entry, extensions, exclude_files):
                    continue
                entries.append(entry)
        for idx, entry in enumerate(entries):
            connector = '└── ' if idx == len(entries) - 1 else '├── '
            tree_lines.append(f"{prefix}{connector}{entry.name}")
            if entry.is_dir():
                extension = '    ' if idx == len(entries) - 1 else '│   '
                recurse(entry, prefix + extension)

    for root in roots:
        if root.is_dir():
            tree_lines.append(root.name)
            recurse(root)
        elif root.is_file():
            if is_valid_file(root, extensions, exclude_files):
                tree_lines.append(root.name)
    return "\n".join(tree_lines)


def copy_files_to_clipboard(
        project_name,
        project_path,
        allowed_extensions=None,
        exclude_dirs=None,
        exclude_files=None,
        comment=None,
        remove_comments: bool = True,
):
    print(f"\nSuche Dateien und kopiere Inhalte in '{project_name}' ...")
    base_paths = [Path(project_path).resolve()]
    project_root = base_paths[0]
    all_files = []
    for p in base_paths:
        all_files.extend(
            collect_files_from_path(
                p,
                extensions=allowed_extensions,
                exclude_dirs=exclude_dirs,
                exclude_files=exclude_files
            )
        )
    if not all_files:
        print(f"\n{RED}Keine Dateien zum Kopieren gefunden.{RESET}")
        return
    file_token_map = {}
    try:
        _encoding = tiktoken.get_encoding("cl100k_base")
    except Exception:
        _encoding = None
    file_count = len(all_files)
    tree_text = build_directory_tree(base_paths, allowed_extensions, exclude_dirs, exclude_files)

    contents = ["--- Verzeichnis-/Dateistruktur ---", tree_text, ""]
    total_lines = 0
    total_raw_lines = 0

    for f in all_files:
        try:
            with open(f, 'r', encoding='utf-8', errors='replace') as fh:
                lines = fh.readlines()
            total_raw_lines += len(lines)

            if remove_comments:
                cleaned = strip_comments(lines)
            else:
                cleaned = [ln.rstrip("\n") for ln in lines]
            if _encoding is not None:
                file_token_map[f.resolve()] = len(_encoding.encode("\n".join(cleaned)))
            else:
                file_token_map[f.resolve()] = 0
            total_lines += len(cleaned)

            try:
                rel_path = f.relative_to(project_root).as_posix()
            except ValueError:
                rel_path = f.name
            rel_display = f"./{rel_path}"

            contents.append(f"--- Start: {rel_display} ---")
            contents.extend(cleaned)
            contents.append(f"--- Ende:  {rel_display} ---")
        except Exception as e:
            print(f"{RED}Fehler beim Lesen von {f}: {e}{RESET}")
    combined = f"\n".join(contents) + f"{4 * '\n'}{comment}"

    try:
        encoding = tiktoken.get_encoding("cl100k_base")
        token_count = len(encoding.encode(combined))
    except Exception:
        token_count = 0
    tree_console_lines = []

    def recurse_console(dir_path: Path, prefix=""):
        if not dir_path.is_dir():
            return
        entries = []
        for entry in sorted(dir_path.iterdir()):
            if entry.is_dir():
                name = entry.name
                if (
                        name.lower() in EXCLUDE_DIRS_DEFAULT
                        or (exclude_dirs and name in exclude_dirs)
                        or any(name.lower().endswith(suffix) for suffix in EXCLUDE_SUFFIXES_DEFAULT)
                ):
                    continue
                entries.append(entry)
            else:
                if not is_valid_file(entry, allowed_extensions, exclude_files):
                    continue
                entries.append(entry)
        for idx, entry in enumerate(entries):
            connector = '└── ' if idx == len(entries) - 1 else '├── '
            if entry.is_dir():
                tree_console_lines.append(f"{prefix}{connector}{entry.name}")
                extension = '    ' if idx == len(entries) - 1 else '│   '
                recurse_console(entry, prefix + extension)
            else:
                tok = file_token_map.get(entry.resolve(), 0)
                tree_console_lines.append(f"{prefix}{connector}{entry.name} {tok:>6}")

    for root in base_paths:
        if root.is_dir():
            tree_console_lines.append(root.name)
            recurse_console(root)
        elif root.is_file():
            tok = file_token_map.get(root.resolve(), 0)
            tree_console_lines.append(f"{root.name} {tok:>6}")
    max_path_len = 0
    for ln in tree_console_lines:
        stripped = ln.rstrip()
        if stripped and stripped[-1].isdigit():
            path_len = len(ln) - 7
            if path_len > max_path_len:
                max_path_len = path_len
    token_gap = 4
    token_col_start = max_path_len + token_gap

    header_inserted = False
    for idx, original in enumerate(tree_console_lines):
        stripped = original.rstrip()
        if stripped and stripped[-1].isdigit():
            path_part = original[:-7].rstrip()
            token_part = original[-7:]
            pad = token_col_start - len(path_part)
            if pad < 0:
                pad = 0
            tree_console_lines[idx] = f"{path_part}{' ' * pad}{token_part}"
        else:
            if not header_inserted:
                pad = token_col_start - len(original.rstrip())
                if pad < 1:
                    pad = 1
                tree_console_lines[idx] = f"{original}{' ' * pad} Tokens"
                header_inserted = True
    tree_text_console = "\n".join(tree_console_lines)

    try:
        pyperclip.copy(combined)
        print(f"\n{tree_text_console}")
        print(f"\n{GREEN}{file_count} Dateien in die Zwischenablage kopiert.{RESET}")
        print(f"Code-Zeilen:       {total_lines:>6}")
        print(f"Gesamtzeilen:      {total_raw_lines:>6}")
        token_color = RESET
        if token_count > THRES2_TOKEN:
            token_color = RED
        elif token_count > THRES1_TOKEN:
            token_color = YELLOW
        print(f"{token_color}Gesamttokens:      {token_count:>6}{RESET}")
    except Exception as e:
        print(f"\n{RED}Fehler beim Kopieren: {e}{RESET}")


def copy_logic(
        project_name=None,
        project_path=None,
        allowed_extensions=None,
        exclude_dirs=None,
        exclude_files=None,
        comment=None,
        remove_comments: bool = True,
):
    """Copy the project source files to the clipboard as a single structured text blob.
    Parameters
    ----------
    project_name : str | None, optional
        Human‑readable label used solely for status messages. If *None* the
        function attempts to resolve a sensible default from *project_path*.
    project_path : str | Path | None, optional
        Root directory—or single file—whose content should be harvested. When
        *None* (default), the current working directory is used.
    allowed_extensions : Sequence[str] | None, optional
        File‑name suffixes (e.g. ``[".py", ".txt"]``) that must match in
        order for a file to be included. *None* means "no restriction".
    exclude_dirs : Sequence[str] | None, optional
        Additional directory names to skip, relative to *project_path*.
        These extend the internal :data:`EXCLUDE_DIRS_DEFAULT` list rather
        than replacing it.
    exclude_files : Sequence[str] | None, optional
        ``fnmatch`` patterns of file names that should be ignored.
    comment : str | None, optional
        Free‑form text appended after four newline characters at the very end
        of the copied blob. Useful to embed instructions for downstream tools
        or LLMs.
    remove_comments : bool | True, optional
        Controls if code‑comments should be excluded from prompt. When *True*
        all comment‑tokens are stripped safely via :pymod:`tokenize`.
    Examples
    --------
    copy_logic("MyProject", "/path/to/project", allowed_extensions=[".py"], comment="Please refactor.")
    See Also
    --------
    copy_init : Script to create a template for fast and easy prompt-generation.
    """
    copy_files_to_clipboard(
        project_name,
        project_path,
        allowed_extensions,
        exclude_dirs,
        exclude_files,
        comment,
        remove_comments,
    )
