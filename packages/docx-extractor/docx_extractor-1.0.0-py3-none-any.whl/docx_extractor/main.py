#!/usr/bin/env python3
import sys
import argparse
from pathlib import Path

try:
    from docx_extractor import extract_docx_recursive
    from docx_extractor.toon_formatter import format_toon
except ImportError:
    print("Install package: pip install -e .")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Extract DOCX recursively to TOON format")
    parser.add_argument("docx", help="Input DOCX file")
    parser.add_argument("-o", "--output", default="extraction.toon", help="Output TOON file")
    parser.add_argument("-d", "--depth", type=int, default=5, help="Max recursion depth")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if not Path(args.docx).exists():
        print(f"Error: {args.docx} not found")
        sys.exit(1)
    
    print(f"Extracting {args.docx} (max depth: {args.depth})")
    
    # Extract
    result = extract_docx_recursive(args.docx, max_depth=args.depth)
    
    # Convert to TOON
    toon_lines = format_toon(result)
    
    # Save
    with open(args.output, "w", encoding="utf-8") as f:
        f.write("\n".join(toon_lines))
    
    print(f"✓ Saved {len(toon_lines)} lines to {args.output}")
    
    if args.verbose:
        print("\nPreview:")
        for line in toon_lines[:20]:
            print(line)


if __name__ == "__main__":
    main()
