# repomap

Tree-sitter based repository map generator - extract and visualize code structure using PageRank.

## Installation

### From source (using uv)
```bash
git clone https://github.com/cdpath/repomap
cd repomap
uv tool install .
```

### From source (using pip)
```bash
git clone https://github.com/cdpath/repomap
cd repomap
pip install .
```

## Usage

### Generate a Repo Map

```bash
# Basic usage
repomap ./src

# Filter by language
repomap ./src --language python

# Exclude directories
repomap ./src --exclude tests

# Save to file
repomap ./src -o map.md

# Adjust output size
repomap ./src --tokens 8192
```

### Generate a Call Graph

```bash
# Generate call graph from entry point
repomap ./src --graph graph.png --entry main.py

# Limit traversal depth  
repomap ./src --graph graph.png --entry main.py --depth 2

# JSON output (FASTEN adjacency list format)
repomap ./src --graph graph.json --entry main.py

# Focus on files matching a pattern (shows matching files + their neighbors)
repomap ./src --graph graph.dot --focus core
```

**Example call graph:**

![repomap call graph](examples/repomap/repomap.png)

**JSON formats:**

| Filename | Format |
|----------|--------|
| `graph.json` | Simple adjacency list |
| `graph.fasten.json` | FASTEN format |

Simple JSON:
```json
{"cli.py": ["core.py", "graph.py"], "core.py": ["ranking.py"]}
```

[FASTEN JSON](https://github.com/fasten-project/fasten/wiki/Revision-Call-Graph-format#version-2-1):
```json
{"product": "myproject", "graph": {"internalCalls": [["cli.py", "core.py"]]}, ...}
```

## Options

```
--output, -o FILE       Save repo map to file
--graph, -g FILE        Generate call graph (.png, .svg, .pdf, .dot, .json)
--entry FILE            Entry point file - filter to reachable files only
--depth N               Max depth from entry point (default: unlimited)
--min-refs N            Min references for symbol inclusion (default: 1)
--focus PATTERN         Focus graph on files matching pattern
--exclude, -e PATTERN   Exclude paths matching pattern
--language, -l LANG     Filter by language (python, javascript, etc.)
--tokens, -t TOKENS     Max tokens for repo map (default: 4096)
--verbose, -v           Enable verbose output
```

## Default Excludes

Common directories are automatically excluded: `.venv`, `node_modules`, `__pycache__`, `.git`, `dist`, `build`, etc.

## Supported Languages

30+ languages via tree-sitter: Python, JavaScript, TypeScript, Java, Go, Rust, C/C++, C#, Ruby, and more.

## How It Works

1. **Parse** source files using tree-sitter to extract definitions and references
2. **Build** a graph of file interdependencies  
3. **Rank** using PageRank algorithm to identify most important code
4. **Render** as tree-structured markdown or visual call graph

## Example Repo Map Output

```
core.py:
│class RepoMap:
│    def __init__(...)
│    def get_repo_map(...)

ranking.py:
│def get_ranked_tags(...)
│def _get_tags_cached(...)
```

## Attribution

Derived from [aider](https://github.com/Aider-AI/aider)'s repomap by Paul Gauthier. See [NOTICE](NOTICE).

## License

Apache 2.0 - see [LICENSE](LICENSE)
