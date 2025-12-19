#!/usr/bin/env python3

from latex_generator import generate_table_latex


def main() -> None:
    data = [
        ["Игрок",              "Титулы НБА", "Очки за карьеру"],
        ["Майкл Джордан",      "6",          "32292"],
        ["Карим Абдул-Джаббар","6",          "38387"],
        ["Коби Брайант",       "5",          "33643"],
        ["Уилт Чемберлен",     "2",          "31419"],
        ["Мэджик Джонсон",     "5",          "17707"],
    ]

    table_code = generate_table_latex(data)

    document = r"""\documentclass{article}
                \usepackage[utf8]{inputenc}
                \usepackage[russian]{babel}

                \begin{document}

                Таблица: Dеличайшие игроки НБА, их чемпионства и очки за карьеру.

                """ + table_code + r"""

                \end{document}
                """

    with open("table_nba_legends.tex", "w", encoding="utf-8") as f:
        f.write(document)


if __name__ == "__main__":
    main()