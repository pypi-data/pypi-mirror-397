def generate_table(data):
    col_spec = "|" + "|".join(["c"] * len(data[0])) + "|"
    
    format_row = lambda row: " & ".join(map(str, row)) + " \\\\"
    rows = list(map(format_row, data))
    
    table_content = "\\hline\n" + "\n\\hline\n".join(rows) + "\n\\hline"
    
    return f"""\\begin{{table}}[h]
\\centering
\\begin{{tabular}}{{{col_spec}}}
{table_content}
\\end{{tabular}}
\\end{{table}}"""


def generate_image(image_path, width=None, caption=None):
    width_str = f"[width={width}]" if width else ""
    caption_str = f"\\caption{{{caption}}}" if caption else ""
    
    figure_code = f"""\\begin{{figure}}[h]
\\centering
\\includegraphics{width_str}{{{image_path}}}
{caption_str}
\\end{{figure}}"""
    
    return figure_code
