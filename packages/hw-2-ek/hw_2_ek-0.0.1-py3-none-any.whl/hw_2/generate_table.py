from latex_generator import generate_table


def main():
    table_data = [
        ["Название", "Количество", "Цена"],
        ["яблоки", "10", "100 руб."],
        ["ананас", "5", "200 руб."],
        ["печенье", "15", "150 руб."],
        ["Итого", "30", "450 руб."]
    ]
    
    latex_code = generate_table(table_data)
    
    with open("table.tex", "w", encoding="utf-8") as f:
        f.write("\\documentclass{article}\n")
        f.write("\\usepackage[utf8]{inputenc}\n")
        f.write("\\usepackage[russian]{babel}\n")
        f.write("\\begin{document}\n\n")
        f.write(latex_code)
        f.write("\n\n\\end{document}\n")


if __name__ == "__main__":
    main()

