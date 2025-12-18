import sys
from pathlib import Path
from importlib.metadata import version

from langpy.core.transpiler import transpile
from langpy.core.lexicon.es import SpanishLexicon
from langpy.core.lexicon.pt import PortugueseLexicon
from langpy.core.lexicon.fr import FrenchLexicon
from langpy.cli.transpile_tree import transpile_tree


EXTENSION_TO_LEXICON = {
    ".pyes": SpanishLexicon,
    ".pypt": PortugueseLexicon,
    ".pyfr": FrenchLexicon,
}


def print_info() -> None:
    print(
        "LangPy — Lexical layer for Python\n\n"
        "Write Python using human-language keywords.\n\n"
        "Supported languages:\n"
        "  .pyes  Spanish\n"
        "  .pypt  Portuguese\n"
        "  .pyfr  French\n\n"
        "Run `langpy --help` for usage."
    )


def print_help() -> None:
    print(
        "Usage:\n"
        "  langpy <file>\n"
        "  langpy --transpile <file>\n\n"
        "Options:\n"
        "  --help        Show this help message and exit\n"
        "  --version     Print package version and exit\n"
        "  --transpile   Transpile source and local LangPy imports to .py\n"
        "  --force       Overwrite existing .py files (only with --transpile)\n\n"
        "Examples:\n"
        "  langpy main.pyes\n"
        "  langpy --transpile main.pyfr\n"
        "  langpy --transpile --force main.pypt"
    )


def main() -> None:
    args = sys.argv[1:]

    # ---- no args ----
    if not args:
        print_info()
        sys.exit(0)

    # ---- informational flags ----
    if "--help" in args:
        print_help()
        sys.exit(0)

    if "--version" in args:
        print(version("langpy"))
        sys.exit(0)

    # ---- flags parsing ----
    transpile_only = "--transpile" in args
    force = "--force" in args

    if force and not transpile_only:
        print("Error: --force can only be used with --transpile")
        sys.exit(1)

    # remaining args should be the file
    files = [a for a in args if not a.startswith("--")]

    if len(files) != 1:
        print("Error: exactly one input file is required")
        sys.exit(1)

    path = Path(files[0])

    if not path.exists() or not path.is_file():
        print(f"Error: file not found: {path}")
        sys.exit(1)

    # ---- transpile mode ----
    if transpile_only:
        try:
            transpile_tree(path, force=force)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

        sys.exit(0)

    # ---- execution mode (default) ----
    if path.suffix not in EXTENSION_TO_LEXICON:
        print(f"Error: unsupported file extension: {path.suffix}")
        sys.exit(1)

    # Python-like behavior: script dir first in sys.path
    script_dir = str(path.parent.resolve())
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)

    source = path.read_text(encoding="utf-8")
    lexicon = EXTENSION_TO_LEXICON[path.suffix]()
    source = transpile(source, lexicon)

    globals_context = {
        "__name__": "__main__",
        "__file__": str(path.resolve()),
        "__builtins__": __builtins__,
    }

    exec(compile(source, str(path), "exec"), globals_context)
