# AST-Aware Code Chunking

Location: `scripts/ast_chunker.py`

## Purpose
Produce syntactically coherent code chunks (functions, classes, methods) for vector embeddings and semantic search. Uses Tree-sitter.

## Supported languages
- Python
- JavaScript / JSX
- TypeScript / TSX
- Go
- Rust
- Java

## Quick usage

```python
from scripts.ast_chunker import ASTChunker, chunk_directory

# Single file
chunker = ASTChunker(max_chars=2500)
chunks = chunker.chunk_file("src/main.py")

# Whole directory
chunks = chunk_directory("/path/to/project", max_chars=2500)

for c in chunks:
    print(c.chunk_type, c.name, c.start_line, c.end_line)
    # c.content  → ready for embedding
```

## Design choices
- Prefer function / method / class boundaries over fixed-size windows.
- Oversized nodes are recursively split by child statements.
- Class methods are extracted as separate `method` chunks with `parent_name` set.
- Falls back to simple line-based chunking when no grammar is available.
- Returns rich `CodeChunk` objects (id, file path, lines, type, name, content).

## Integration with embeddings
Each `CodeChunk.content` is the ideal unit to embed with a code-specialized model
(Voyage Code-3, jina-code-embeddings, etc.). Store the metadata (`file_path`,
`start_line`, `name`, `chunk_type`) alongside the vector for citation.
