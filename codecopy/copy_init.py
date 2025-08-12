#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 30.07.2025 at 09:59

@author: piledge
"""

from pathlib import Path
import sys

RED = "\033[31m"
GREEN = "\033[32m"
RESET = "\033[0m"

TEMPLATE = r'''
project_name = "{project_name}"
project_path = r"{project_path}"

allowed_extensions = [".py"]

excluded_dirs = ['favicons']
excluded_files = ["test*.py", "{filename}"]

remove_comments = True

comment = (
    "Führe nur die ausdrücklich genannten Änderungen aus.\n"
    "Gib jede geänderte Datei vollständig von Anfang bis Ende in einem eigenen Codeblock aus, beginnend mit dem Dateipfad.\n"
    "Unveränderte Dateien nicht anzeigen, stattdessen ‹keine Änderung› schreiben.\n"
    "Erhalte Formatierung, Kommentare, Reihenfolge und Imports exakt.\n"
    "Keine Umbenennungen, Auto-Formatierung, neue Sortierungen, unnötige Kommentare und Backslashes.\n"
    "Nutze Best Practices.\n"
    "Änderungen dürfen bestehende Funktionalität nicht beeinträchtigen.\n"
    "Bei Unklarheiten: nachfragen, nicht raten.\n"
)

from codecopy import copy_logic

copy_logic(
    project_name,
    project_path,
    allowed_extensions,
    excluded_dirs,
    excluded_files,
    comment,
    remove_comments,
)
'''


def _default_project_path() -> Path:
    main = sys.modules.get('__main__')
    if hasattr(main, '__file__'):
        return Path(main.__file__).expanduser().resolve().parent
    return Path.cwd()


def copy_init(
        project_path: str | None = None,
        filename: str = "prompt_export.py",
        overwrite: bool = False
) -> None:
    """Create a ready-to-run *prompt_export.py* template in *target_dir*.

    Parameters
    ----------
    project_path : str | None, optional
        Directory in which the template is written. If *None* (default), the
        directory of the calling script—or the current working directory—is
        used.
    filename : str, optional
        Name of the template file (default: ``"prompt_export.py"``).
    overwrite : bool, optional
        If *False* (default) and the file already exists, the function aborts
        and prints an informational message. If *True*, any existing file will
        be overwritten.
    """
    target_dir = Path(project_path).expanduser().resolve() if project_path else _default_project_path()
    target_dir.mkdir(parents=True, exist_ok=True)
    target_file = target_dir / filename

    if target_file.exists() and not overwrite:
        print(f"\n{RED}'{target_file}' existiert bereits – »overwrite=True« setzen, um zu überschreiben.{RESET}")
        return

    project_name = target_dir.name
    project_path = str(target_dir)

    file_content = TEMPLATE.format(
        project_name=project_name,
        project_path=project_path,
        filename=filename
    )
    target_file.write_text(file_content, encoding="utf-8")
    print(f"\n{GREEN}Template nach '{target_file}' geschrieben.{RESET}")

    gitignore_file = target_dir / ".gitignore"
    ignore_entry = f"/{filename}"
    try:
        if gitignore_file.exists():
            lines = gitignore_file.read_text(encoding="utf-8").splitlines()
            if ignore_entry not in [line.strip() for line in lines]:
                with gitignore_file.open("a", encoding="utf-8") as fh:
                    if lines and not lines[-1].endswith("\n"):
                        fh.write("\n")
                    fh.write(f"{ignore_entry}\n")
        else:
            gitignore_file.write_text(f"{ignore_entry}\n", encoding="utf-8")
    except Exception as exc:
        print(f"\n{RED}Konnte '.gitignore' nicht aktualisieren: {exc}{RESET}")
