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


EXCLUDE_DIRS_DEFAULT = ["migrations", "__pycache__", "node_modules", ".git", ".idea", ".venv",]
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RESET = "\033[0m"

n_tokens = 32000
thres1_token = 12500
thres2_token = 16000


def is_valid_file(file_path: Path, extensions=None, exclude_files=None):
    if file_path.suffix.lower() == '.ico':
        return False
    if extensions and file_path.suffix not in extensions:
        return False
    if exclude_files and any(fnmatch.fnmatch(file_path.name, pat) for pat in exclude_files):
        return False
    return True


def strip_comments(lines):
    cleaned = []
    for line in lines:
        part = line.split('#')[0].rstrip('\n')
        if part.strip():
            cleaned.append(part)
    return cleaned


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
                if entry.name.lower() in EXCLUDE_DIRS_DEFAULT or (exclude_dirs and entry.name in exclude_dirs):
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


def copy_files_to_clipboard(project_name, project_path, allowed_extensions=None, exclude_dirs=None, exclude_files=None, comment=None):
    print(f"\nSuche Dateien und kopiere Inhalte in '{project_name}' ...")
    base_paths = [Path(project_path).resolve()]
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
    file_count = len(all_files)
    tree_text = build_directory_tree(base_paths, allowed_extensions, exclude_dirs, exclude_files)
    contents = ["--- Verzeichnisstruktur / Dateien ---", tree_text, ""]
    total_lines = 0
    total_raw_lines = 0
    for f in all_files:
        try:
            with open(f, 'r', encoding='utf-8', errors='replace') as fh:
                lines = fh.readlines()
            total_raw_lines += len(lines)
            cleaned = strip_comments(lines)
            total_lines += len(cleaned)
            contents.append(f"--- Start: {f} ---")
            contents.extend(cleaned)
            contents.append(f"--- Ende:   {f} ---")
        except Exception as e:
            print(f"{RED}Fehler beim Lesen von {f}: {e}{RESET}")
    combined = f"\n".join(contents) + f"{4*'\n'}{comment}"
    try:
        encoding = tiktoken.get_encoding("cl100k_base")
        token_count = len(encoding.encode(combined))
    except Exception:
        token_count = 0
    try:
        pyperclip.copy(combined)
        print(f"\n{tree_text}")
        print(f"\n{GREEN}{file_count} Dateien in die Zwischenablage kopiert.{RESET}")
        print(f"Code-Zeilen:  {total_lines:>6}")
        print(f"Gesamtzeilen: {total_raw_lines:>6}")
        token_color = RESET
        if token_count > thres2_token:
            token_color = RED
        elif token_count > thres1_token:
            token_color = YELLOW
        print(f"{token_color}Tokens:       {token_count:>6}{RESET}")
    except Exception as e:
        print(f"\n{RED}Fehler beim Kopieren: {e}{RESET}")


def copy_logic(project_name=None, project_path=None, allowed_extensions=None, exclude_dirs=None, exclude_files=None, comment=None):
    copy_files_to_clipboard(project_name, project_path, allowed_extensions, exclude_dirs, exclude_files, comment)
