# codecopy

Ein Python-Modul zur automatischen Zusammenstellung und Kopie eines Code‑Projekts in die Zwischenablage – ideal als Ausgangspunkt für LLM‑basiertes Refactoring oder Review.

---

## 📦 Features

* **Verzeichnisbaum**: Baut automatisch eine übersichtliche Baumstruktur Deiner Projektdateien auf.
* **Filterung**: Beinhaltet nur definierte Dateiendungen (standardmäßig `.py`), schließt Ordner wie `__pycache__`, `.git`, `.idea` u.v.m. aus.
* **Kommentare entfernen**: Bereinigt Quellcode um Kommentare, um den „Kern“ lesbar zu machen.
* **Zwischenablage**: Kopiert das Ergebnis mitsamt Struktur und Kommentar-Anweisungen direkt in die Zwischenablage.
* **Prompt‑Vorlage**: Mit `copy_init` erzeugst Du auf Knopfdruck eine `prompt_export.py`‑Datei für neue Projekte.

---

## 🚀 Installation

1. Repository klonen

   ```bash
   git clone https://github.com/piledge/codecopy.git
   cd codecopy
   ```
2. Abhängigkeiten installieren

   ```bash
   pip install -r requirements.txt
   ```
3. Optional: Als Paket installieren

   ```bash
   pip install git+https://github.com/piledge/codecopy.git

   # Aktualisieren
   pip install --upgrade --force-reinstall --no-cache-dir git+https://github.com/piledge/codecopy.git
   ```

---

## 🎯 Verwendung

```python
# Variante 1: Kopiere das gesamte aktuelle Projekt (nur .py-Dateien)
from codecopy import copy_logic, copy_init
copy_logic(
    project_name="MeinProjekt", # optional
    project_path="Pfad/zum/Projekt", # optional
    allowed_extensions=[".py"], # optional
    exclude_dirs=[], # optional
    exclude_files=["test_*.py", ".gitignore"], # optional
    comment="Bitte refaktorieren und optimieren."
)

# Variante 2: Erstelle eine prompt_export-Vorlage im Projektordner
from codecopy import copy_logic, copy_init
copy_init(
    project_path="Pfad/zum/Projekt",
    filename="prompt_export.py",
    overwrite=False
)

# Variante 3: Erstelle eine prompt_export-Vorlage mit Default-Werten
from codecopy import copy_init
copy_init()

```

---

## 📄 Lizenz

Dieses Projekt steht unter der MIT License. Siehe `LICENSE` für Details.
