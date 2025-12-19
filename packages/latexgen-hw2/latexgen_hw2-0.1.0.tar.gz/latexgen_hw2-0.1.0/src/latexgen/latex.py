def latex_table(table: list[list[str]]) -> str:
    if not table:
        return ""

    header = "|" + "|".join(["c"] * len(table[0])) + "|"
    content = [
        "\\begin{center}",
        "\\begin{tabular}{ " + header + " } ",
        "\\hline"
    ]

    for line in table:
        content.append(" & ".join(line) + " \\\\")

    content.extend([
        "\\hline",
        "\\end{tabular}",
        "\\end{center}"
    ])

    return "\n".join(content)


def latex_image(image_path: str):
    return "\\begin{center}\n" \
           f"\\includegraphics[width=0.6\\textwidth]{{{image_path}}}\n" \
           "\\end{center}"


def build_latex(content: str, dest_path: str):
    text = "\n".join([
        "\\documentclass{article}",
        "\\usepackage{graphicx}",
        "\\begin{document}",
        content,
        "\\end{document}"
    ])
    with open(dest_path, "w", encoding="utf-8") as file:
        file.write(text)
