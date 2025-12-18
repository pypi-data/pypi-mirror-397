# DOCX Extractor

[![PyPI version](https://badge.fury.io/py/docx-extractor.svg)](https://badge.fury.io/py/docx-extractor)
[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Recursive DOCX extractor** that handles embedded files (Excel, Word, SQL/TXT) with **compact TOON output format**.

Extracts:
- ✅ DOCX paragraphs & tables (with full cell data)
- ✅ Embedded Excel sheets (all rows/columns)
- ✅ Nested DOCX (recursive up to 5 levels)
- ✅ SQL/TXT files
- ✅ Filters empty content

## 🚀 Quick Start


# Install
pip install docx-extractor

# Extract DOCX to TOON format
docx-extract input.docx -o output.toon

# With options
docx-extract input.docx -o result.toon --depth 3 -v


## 📄 Sample TOON Output


FILE	input.docx	.docx	L0
PARA	1	Project Summary Report
TABLE	1	3rows x 4cols
ROW	T1.R1	Project|Q1|Q2|Q3|Total
ROW	T1.R2	ProjectA|100|150|200|450
ROW	T1.R3	ProjectB|80|120|180|380
EMBEDDED	1
  FILE	sheet1.xlsx	.xlsx	L1
  SHEET	Sales	15rows
  ROW	Sales.1	Product|Units|Price|Total
  ROW	Sales.2	WidgetA|100|25.50|2550.00


## 🛠️ Installation

### From PyPI

pip install docx-extractor


### From Source

git clone https://github.com/yourusername/docx-extractor.git
cd docx-extractor
pip install -e .


## 🎯 Usage


docx-extract [OPTIONS] <docx_file>


**Options:**

-o, --output     Output TOON file (default: extraction.toon)
-d, --depth      Max recursion depth (default: 5)
-v, --verbose    Show preview
-h, --help       Show help


## 🏗️ Package Structure


docx_extractor/
├── core.py          # Main extraction logic
├── processors.py    # Excel/TXT handlers
├── toon_formatter.py # TOON output formatter
└── __init__.py


## 🔧 Programmatic Usage


from docx_extractor import extract_docx_recursive
from docx_extractor.toon_formatter import format_toon

# Extract
result = extract_docx_recursive("input.docx", max_depth=3)

# TOON format
toon_lines = format_toon(result)

# Save
with open("output.toon", "w") as f:
    f.write("\n".join(toon_lines))


## 📊 TOON Format Specification

**Tab-separated, hierarchical, token-efficient:**


TYPE    IDENTIFIER    DATA
FILE    filename.docx .docx    L0
PARA    1             Document title
TABLE   1             3rows x 4cols
ROW     T1.R1         Project|Q1|Q2|Total
SHEET   Sales         15rows
ROW     Sales.1       Product|100|25.50
TEXT    1250chars     First 1000 chars...


## 🧪 Features Tested

- [x] DOCX paragraphs (non-empty only)
- [x] DOCX tables (full cell data)
- [x] Embedded Excel (.xlsx/.xls)
- [x] Nested DOCX (recursive)
- [x] SQL/TXT files
- [x] OLE package stream extraction
- [x] Empty content filtering
- [x] TOON compact output

## 🔍 Dependencies

| Package | Purpose |
|---------|---------|
| `python-docx` | DOCX parsing |
| `openpyxl` | Excel reading |
| `olefile` | OLE embedded extraction |

## ⚙️ Development


# Install dev dependencies
pip install -e .[dev]

# Build package
python -m build

# Test
pytest tests/

# Publish
twine upload dist/*

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- [python-docx](https://python-docx.readthedocs.io/)
- [openpyxl](https://openpyxl.readthedocs.io/)
- [olefile](https://pypi.org/project/olefile/)

---

**Made with ❤️ for document automation**