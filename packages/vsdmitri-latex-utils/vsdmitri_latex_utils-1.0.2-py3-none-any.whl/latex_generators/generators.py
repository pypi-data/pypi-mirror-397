def generate_document_template(content):
    return f"""\\documentclass{{article}}
\\usepackage{{graphicx}}
\\begin{{document}}
{content}
\\end{{document}}
"""


def generate_table(data):
    _HLINE = "\\hline"

    if not data:
        return ""

    rows_strs = "\n".join(
        " & ".join(str(cell) for cell in row) + " \\\\ " + _HLINE for row in data
    )
    table = f"""\\begin{{tabular}}{{{"|" + "c|" * len(data[0])}}}
{_HLINE}
{rows_strs}
\\end{{tabular}}"""

    return table


def generate_image(path, caption=None):
    _TEXT_WIDTH = 0.5

    caption_line = f"\\caption{{{caption}}}\n" if caption else ""
    image = f"""\\begin{{figure}}[h]
\\centering
\\includegraphics[width={_TEXT_WIDTH}\\textwidth]{{{path}}}
{caption_line}\\end{{figure}}"""
    return image
