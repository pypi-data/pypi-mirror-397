from latex import generate_table

def main():
    data = [
        ["Brand", "Year", "Price"],
        ["Mercedes", 1995, 1000],
        ["BMW", 2003, 15000],
        ["Porshe", 2025, 200000],
    ]

    table_latex = generate_table(data)

    document = r"""
\documentclass{article}
\begin{document}

""" + table_latex + r"""

\end{document}
"""

    with open("example.tex", "w", encoding="utf-8") as f:
        f.write(document)

if __name__ == "__main__":
    main()
