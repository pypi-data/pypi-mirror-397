def generate_table(data):
    if not data or not all(isinstance(row, list) for row in data):
        raise ValueError("Input must be a 2D list")

    cols = len(data[0])

    col_spec = "|" + "|".join(["c"] * cols) + "|"

    def format_row(row):
        return " & ".join(map(str, row)) + r" \\"

    rows = map(format_row, data)

    table = (
        r"\begin{tabular}{" + col_spec + "}\n"
        r"\hline" + "\n"
        + "\n\\hline\n".join(rows) + "\n"
        r"\hline" + "\n"
        r"\end{tabular}"
    )

    return table

def generate_image(image_path, width="0.5\\textwidth"):
    image = (
        "\\begin{figure}[h]\n"
        "\\centering\n"
        f"\\includegraphics[width={width}]{{{image_path}}}\n"
        "\\end{figure}"
    )

    return image

