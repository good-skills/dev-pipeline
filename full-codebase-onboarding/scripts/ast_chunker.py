#!/usr/bin/env python3
"""
AST-aware code chunker using Tree-sitter.

Produces syntactically coherent chunks (functions, classes, methods)
suitable for vector embeddings and semantic code search.

Supported languages (via tree-sitter grammars):
  python, javascript, typescript, tsx, go, rust, java

Usage:
  from ast_chunker import ASTChunker
  chunker = ASTChunker(max_chars=2000)
  chunks = chunker.chunk_file("path/to/file.py")
  # or
  chunks = chunker.chunk_source(source_code, language="python", file_path="example.py")
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from tree_sitter import Language, Parser, Node

# ---------------------------------------------------------------------------
# Language setup
# ---------------------------------------------------------------------------

_LANGUAGE_MODULES = {
    "python": "tree_sitter_python",
    "javascript": "tree_sitter_javascript",
    "typescript": "tree_sitter_typescript",
    "tsx": "tree_sitter_typescript",
    "go": "tree_sitter_go",
    "rust": "tree_sitter_rust",
    "java": "tree_sitter_java",
}

_EXTENSION_MAP = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".mjs": "javascript",
    ".ts": "typescript",
    ".tsx": "tsx",
    ".go": "go",
    ".rs": "rust",
    ".java": "java",
}

# Node types that represent meaningful semantic units
_FUNCTION_TYPES = {
    "function_definition",          # Python
    "function_declaration",         # JS/TS, C-like
    "method_definition",            # JS/TS
    "method_declaration",           # Java, Go
    "function_item",                # Rust
    "arrow_function",               # JS/TS
    "generator_function_declaration",
    "function",                     # some grammars
}

_CLASS_TYPES = {
    "class_definition",             # Python
    "class_declaration",            # JS/TS, Java
    "class_specifier",              # C++
    "impl_item",                    # Rust
    "struct_item",                  # Rust
    "interface_declaration",        # Java, TS
    "enum_declaration",
    "type_alias_declaration",
    "trait_item",                   # Rust
}

_MODULE_LEVEL_TYPES = {
    "import_statement",
    "import_from_statement",
    "import_declaration",
    "package_declaration",
    "use_declaration",              # Rust
}


def _load_language(lang: str) -> Optional[Language]:
    mod_name = _LANGUAGE_MODULES.get(lang)
    if not mod_name:
        return None
    try:
        mod = __import__(mod_name)
        if lang == "typescript":
            return Language(mod.language_typescript())
        if lang == "tsx":
            return Language(mod.language_tsx())
        return Language(mod.language())
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class CodeChunk:
    """A single AST-derived code chunk."""
    id: str
    file_path: str
    language: str
    chunk_type: str                 # "function" | "class" | "method" | "module" | "other"
    name: str
    content: str
    start_line: int
    end_line: int
    start_byte: int
    end_byte: int
    parent_name: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def char_count(self) -> int:
        return len(self.content)

    @property
    def non_whitespace_count(self) -> int:
        return sum(1 for c in self.content if not c.isspace())

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "file_path": self.file_path,
            "language": self.language,
            "chunk_type": self.chunk_type,
            "name": self.name,
            "content": self.content,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "parent_name": self.parent_name,
            "char_count": self.char_count,
            "metadata": self.metadata,
        }


# ---------------------------------------------------------------------------
# Chunker
# ---------------------------------------------------------------------------

class ASTChunker:
    """
    AST-aware chunker.

    Parameters
    ----------
    max_chars : int
        Soft maximum characters per chunk. Oversized nodes are recursively split.
    min_chars : int
        Tiny sibling nodes below this size are merged when possible.
    include_module_level : bool
        Whether to emit top-level imports / module statements as chunks.
    """

    def __init__(
        self,
        max_chars: int = 2500,
        min_chars: int = 40,
        include_module_level: bool = False,
    ):
        self.max_chars = max_chars
        self.min_chars = min_chars
        self.include_module_level = include_module_level
        self._parsers: dict[str, Parser] = {}
        self._languages: dict[str, Language] = {}

    def _get_parser(self, language: str) -> Optional[Parser]:
        if language in self._parsers:
            return self._parsers[language]
        lang_obj = _load_language(language)
        if lang_obj is None:
            return None
        parser = Parser(lang_obj)
        self._languages[language] = lang_obj
        self._parsers[language] = parser
        return parser

    def detect_language(self, file_path: str | Path) -> Optional[str]:
        ext = Path(file_path).suffix.lower()
        return _EXTENSION_MAP.get(ext)

    def chunk_file(self, file_path: str | Path) -> list[CodeChunk]:
        path = Path(file_path)
        language = self.detect_language(path)
        if language is None:
            return []
        try:
            source = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return []
        return self.chunk_source(source, language=language, file_path=str(path))

    def chunk_source(
        self,
        source: str,
        language: str,
        file_path: str = "<memory>",
    ) -> list[CodeChunk]:
        parser = self._get_parser(language)
        if parser is None:
            return self._fallback_chunk(source, language, file_path)

        src_bytes = bytes(source, "utf-8", errors="replace")
        tree = parser.parse(src_bytes)
        root = tree.root_node

        chunks: list[CodeChunk] = []
        self._walk(root, src_bytes, file_path, language, chunks, parent_name=None)

        # Merge very small adjacent "other" chunks if needed
        chunks = self._merge_small_chunks(chunks)
        return chunks

    def _walk(
        self,
        node: Node,
        src_bytes: bytes,
        file_path: str,
        language: str,
        chunks: list[CodeChunk],
        parent_name: Optional[str],
    ) -> None:
        node_type = node.type
        text = self._node_text(node, src_bytes)

        if node_type in _FUNCTION_TYPES:
            name = self._extract_name(node, src_bytes) or "<anonymous>"
            chunk_type = "method" if parent_name else "function"
            self._emit_or_split(
                node, src_bytes, file_path, language, chunks,
                chunk_type=chunk_type, name=name, parent_name=parent_name,
            )
            return  # do not descend further into function body for separate chunks

        if node_type in _CLASS_TYPES:
            name = self._extract_name(node, src_bytes) or "<anonymous>"
            # Emit the class itself (signature + docstring area) only if small;
            # otherwise just walk children so methods become separate chunks.
            if len(text) <= self.max_chars:
                self._emit_or_split(
                    node, src_bytes, file_path, language, chunks,
                    chunk_type="class", name=name, parent_name=parent_name,
                )
            # Always walk children so methods are extracted
            for child in node.children:
                self._walk(child, src_bytes, file_path, language, chunks, parent_name=name)
            return

        if self.include_module_level and node_type in _MODULE_LEVEL_TYPES:
            name = self._extract_name(node, src_bytes) or node_type
            self._emit_or_split(
                node, src_bytes, file_path, language, chunks,
                chunk_type="module", name=name, parent_name=None,
            )
            return

        # Recurse into children
        for child in node.children:
            self._walk(child, src_bytes, file_path, language, chunks, parent_name)

    def _emit_or_split(
        self,
        node: Node,
        src_bytes: bytes,
        file_path: str,
        language: str,
        chunks: list[CodeChunk],
        chunk_type: str,
        name: str,
        parent_name: Optional[str],
    ) -> None:
        text = self._node_text(node, src_bytes)
        if len(text) <= self.max_chars:
            chunks.append(self._make_chunk(
                node, src_bytes, file_path, language, chunk_type, name, parent_name
            ))
            return

        # Oversized: try to split by direct children statements
        child_chunks = []
        for child in node.children:
            child_text = self._node_text(child, src_bytes)
            if not child_text.strip():
                continue
            if len(child_text) <= self.max_chars:
                child_chunks.append(self._make_chunk(
                    child, src_bytes, file_path, language, "other",
                    name=f"{name}::{child.type}", parent_name=name,
                ))
            else:
                # Recurse deeper
                self._walk(child, src_bytes, file_path, language, chunks, parent_name=name)

        if child_chunks:
            chunks.extend(child_chunks)
        else:
            # Last resort: emit the whole node even if large
            chunks.append(self._make_chunk(
                node, src_bytes, file_path, language, chunk_type, name, parent_name
            ))

    def _make_chunk(
        self,
        node: Node,
        src_bytes: bytes,
        file_path: str,
        language: str,
        chunk_type: str,
        name: str,
        parent_name: Optional[str],
    ) -> CodeChunk:
        content = self._node_text(node, src_bytes)
        cid = self._chunk_id(file_path, name, node.start_point[0], node.end_point[0])
        return CodeChunk(
            id=cid,
            file_path=file_path,
            language=language,
            chunk_type=chunk_type,
            name=name,
            content=content,
            start_line=node.start_point[0] + 1,
            end_line=node.end_point[0] + 1,
            start_byte=node.start_byte,
            end_byte=node.end_byte,
            parent_name=parent_name,
            metadata={
                "node_type": node.type,
            },
        )

    def _extract_name(self, node: Node, src_bytes: bytes) -> Optional[str]:
        # Common field name across many grammars
        name_node = node.child_by_field_name("name")
        if name_node:
            return self._node_text(name_node, src_bytes).strip()

        # Fallback: look for identifier children
        for child in node.children:
            if child.type in ("identifier", "type_identifier", "property_identifier"):
                return self._node_text(child, src_bytes).strip()
        return None

    @staticmethod
    def _node_text(node: Node, src_bytes: bytes) -> str:
        return src_bytes[node.start_byte:node.end_byte].decode("utf-8", errors="replace")

    @staticmethod
    def _chunk_id(file_path: str, name: str, start: int, end: int) -> str:
        raw = f"{file_path}:{name}:{start}:{end}"
        return hashlib.sha1(raw.encode()).hexdigest()[:16]

    def _merge_small_chunks(self, chunks: list[CodeChunk]) -> list[CodeChunk]:
        if not chunks:
            return chunks
        # Currently we keep all semantic units; merging is conservative
        # to avoid destroying function/class boundaries.
        return chunks

    def _fallback_chunk(
        self, source: str, language: str, file_path: str
    ) -> list[CodeChunk]:
        """Simple line-based fallback when no grammar is available."""
        lines = source.splitlines(keepends=True)
        chunks = []
        buf: list[str] = []
        start_line = 1
        for i, line in enumerate(lines, 1):
            buf.append(line)
            text = "".join(buf)
            if len(text) >= self.max_chars or i == len(lines):
                content = "".join(buf)
                if content.strip():
                    cid = self._chunk_id(file_path, f"block_{start_line}", start_line, i)
                    chunks.append(CodeChunk(
                        id=cid,
                        file_path=file_path,
                        language=language,
                        chunk_type="other",
                        name=f"block_{start_line}_{i}",
                        content=content,
                        start_line=start_line,
                        end_line=i,
                        start_byte=0,
                        end_byte=0,
                    ))
                buf = []
                start_line = i + 1
        return chunks


# ---------------------------------------------------------------------------
# Convenience helpers
# ---------------------------------------------------------------------------

def chunk_directory(
    root: str | Path,
    extensions: Optional[set[str]] = None,
    max_chars: int = 2500,
    exclude_dirs: Optional[set[str]] = None,
) -> list[CodeChunk]:
    """
    Walk a directory and chunk all supported source files.
    """
    root = Path(root)
    extensions = extensions or set(_EXTENSION_MAP.keys())
    exclude_dirs = exclude_dirs or {
        "node_modules", ".git", "__pycache__", "dist", "build",
        ".venv", "venv", "target", "vendor", ".next", "coverage",
    }

    chunker = ASTChunker(max_chars=max_chars)
    all_chunks: list[CodeChunk] = []

    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in exclude_dirs for part in path.parts):
            continue
        if path.suffix.lower() not in extensions:
            continue
        all_chunks.extend(chunker.chunk_file(path))

    return all_chunks


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        # Demo with inline Python
        demo = '''
import os
from typing import List

def fibonacci(n: int) -> int:
    """Return the n-th Fibonacci number."""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

class Calculator:
    """Simple calculator."""

    def add(self, a: float, b: float) -> float:
        return a + b

    def multiply(self, a: float, b: float) -> float:
        return a * b

def main():
    calc = Calculator()
    print(calc.add(2, 3))
'''
        chunker = ASTChunker(max_chars=800)
        chunks = chunker.chunk_source(demo, language="python", file_path="demo.py")
        for c in chunks:
            print(f"[{c.chunk_type}] {c.name}  (L{c.start_line}-{c.end_line}, {c.char_count} chars)")
            print(c.content[:120].replace("\n", " ") + ("..." if len(c.content) > 120 else ""))
            print("-" * 60)
    else:
        target = Path(sys.argv[1])
        if target.is_file():
            chunks = ASTChunker().chunk_file(target)
        else:
            chunks = chunk_directory(target)
        print(json.dumps([c.to_dict() for c in chunks], indent=2))
