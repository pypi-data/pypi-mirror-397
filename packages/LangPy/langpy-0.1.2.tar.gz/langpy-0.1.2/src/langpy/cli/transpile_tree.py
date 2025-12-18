from pathlib import Path
import tokenize
from io import StringIO

from langpy.core.transpiler import transpile
from langpy.core.lexicon.es import SpanishLexicon
from langpy.core.lexicon.pt import PortugueseLexicon
from langpy.core.lexicon.fr import FrenchLexicon


EXTENSION_TO_LEXICON = {
    ".pyes": SpanishLexicon,
    ".pypt": PortugueseLexicon,
    ".pyfr": FrenchLexicon,
}

SUPPORTED_EXTENSIONS = tuple(EXTENSION_TO_LEXICON.keys())


def transpile_tree(entry_path: Path, *, force: bool = False) -> list[Path]:
    if not entry_path.exists() or not entry_path.is_file():
        raise FileNotFoundError(entry_path)

    entry_path = entry_path.resolve()

    processed: set[Path] = set()
    pending: list[Path] = [entry_path]
    generated: list[Path] = []

    # mismo criterio que en ejecución: script dir primero
    search_paths = [entry_path.parent]

    while pending:
        current = pending.pop()

        if current in processed:
            continue

        output_py = _transpile_file(current, force=force)
        generated.append(output_py)
        processed.add(current)

        source = current.read_text(encoding="utf-8")

        lexicon_cls = EXTENSION_TO_LEXICON[current.suffix]
        lexicon = lexicon_cls()
        python_source = transpile(source, lexicon)

        imports = _collect_imports(python_source)

        for fullname in imports:
            resolved = _resolve_module(fullname, search_paths)
            if resolved and resolved not in processed:
                pending.append(resolved)

    return generated


def _collect_imports(source: str) -> set[str]:
    imports: set[str] = set()

    tokens = tokenize.generate_tokens(StringIO(source).readline)
    it = iter(tokens)

    for tok in it:
        # import foo.bar
        if tok.type == tokenize.NAME and tok.string == "import":
            next_tok = next(it, None)
            if next_tok and next_tok.type == tokenize.NAME:
                imports.add(next_tok.string)

        # from foo.bar import baz
        elif tok.type == tokenize.NAME and tok.string == "from":
            next_tok = next(it, None)
            if next_tok and next_tok.type == tokenize.NAME:
                imports.add(next_tok.string)

    return imports


def _resolve_module(fullname: str, search_paths: list[Path]) -> Path | None:
    parts = fullname.split(".")
    module_name = parts[-1]

    for base in search_paths:
        base_path = Path(base)

        # módulo suelto: modulo.<ext>
        for ext in SUPPORTED_EXTENSIONS:
            candidate = base_path / f"{module_name}{ext}"
            if candidate.is_file():
                return candidate.resolve()

        # paquete: modulo/__init__.<ext>
        package_dir = base_path / module_name
        if package_dir.is_dir():
            for ext in SUPPORTED_EXTENSIONS:
                init_file = package_dir / f"__init__{ext}"
                if init_file.is_file():
                    return init_file.resolve()

    return None


def _transpile_file(path: Path, *, force: bool) -> Path:
    if path.suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported extension: {path.suffix}")

    output = path.with_suffix(".py")

    if output.exists() and not force:
        raise FileExistsError(output)

    lexicon_cls = EXTENSION_TO_LEXICON[path.suffix]
    lexicon = lexicon_cls()

    source = path.read_text(encoding="utf-8")
    result = transpile(source, lexicon)

    output.write_text(result, encoding="utf-8")
    return output
