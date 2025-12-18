def format_toon(result, prefix=""):
    """Convert recursive result to TOON format (tab-separated, compact)."""
    lines = []
    
    # File header
    lines.append(f"{prefix}FILE\t{result['file']}\t{result['type']}\tL{result['level']}")
    
    # DOCX content - PARAGRAPHS
    if "content" in result:
        for i, para in enumerate(result["content"].get("paragraphs", []), 1):
            lines.append(f"{prefix}PARA\t{i}\t{para[:500]}")
        
        # DOCX content - TABLES (FIXED: now shows actual data)
        for t_i, table in enumerate(result["content"].get("tables", []), 1):
            lines.append(f"{prefix}TABLE\t{t_i}\t{len(table)}rows x {len(table[0]) if table else 0}cols")
            
            # Extract table data row by row
            for r_i, row in enumerate(table, 1):
                # Join cells with | separator, truncate long rows
                row_str = "|".join(cell[:100] for cell in row)[:300]
                lines.append(f"{prefix}ROW\t{table_id(t_i, r_i)}\t{row_str}")
    
    # Excel sheets
    if "excel" in result:
        for sheet, rows in result["excel"].items():
            lines.append(f"{prefix}SHEET\t{sheet}\t{len(rows)}rows")
            for r_i, row in enumerate(rows[:20], 1):  # first 20 rows max
                row_str = "\t".join(str(cell)[:50] for cell in row)
                lines.append(f"{prefix}ROW\t{sheet}.{r_i}\t{row_str}")
    
    # Text content
    if "text" in result:
        lines.append(f"{prefix}TEXT\t{len(result['text'])}chars")
        # Split long text into chunks
        chunks = [result['text'][i:i+800] for i in range(0, len(result['text']), 800)]
        for c_i, chunk in enumerate(chunks, 1):
            lines.append(f"{prefix}CHUNK\t{c_i}\t{chunk}")
    
    # Embedded summary
    if "embedded_count" in result and result["embedded_count"]:
        lines.append(f"{prefix}EMBEDDED\t{result['embedded_count']}")
    
    # Children (recursive)
    for child in result.get("children", []):
        lines.extend(format_toon(child, prefix + "  "))
    
    return lines


def table_id(table_num, row_num):
    """Generate unique table.row ID."""
    return f"T{table_num}.R{row_num}"
