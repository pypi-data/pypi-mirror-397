# jsonl2htmlmd

A command-line tool to convert JSONL files into interactive HTML tables with full Markdown rendering support.

Supports:
- GitHub-flavored Markdown
- Syntax highlighting via highlight.js
- Pagination, search, and sorting via DataTables
- Large JSONL datasets
- LLM / SFT dataset visualization

---

## Installation

```bash
pip install jsonl2htmlmd
```


## Usage

```bash
jsonl2htmlmd -i data.jsonl -o output.html
```

## Specify columns:

```bash
jsonl2htmlmd -i data.jsonl -o output.html -f prompt,response,analysis
```

## Arguments
| Argument       | Description                            |
| -------------- | -------------------------------------- |
| `-i, --input`  | Input JSONL file path                  |
| `-o, --output` | Output HTML file path                  |
| `-f, --fields` | Comma-separated field names (optional) |

