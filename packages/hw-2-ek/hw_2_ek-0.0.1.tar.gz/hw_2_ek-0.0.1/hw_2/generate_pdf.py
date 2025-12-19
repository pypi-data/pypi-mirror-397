from latex_generator import generate_table, generate_image
import subprocess
import os


def main():
    table_data = [
        ["Название", "Количество", "Цена"],
        ["яблоки", "10", "100 руб."],
        ["ананас", "5", "200 руб."],
        ["печенье", "15", "150 руб."],
        ["Итого", "30", "450 руб."]
    ]
    
    latex_code = generate_table(table_data)
    image_code = generate_image("52.png", width="0.5\\textwidth", caption="Пример изображения")

    full_document = f"""\\documentclass{{article}}
\\usepackage[utf8]{{inputenc}}
\\usepackage[russian]{{babel}}
\\usepackage{{graphicx}}

\\begin{{document}}

\\section{{Таблица}}
{latex_code}
 
\\section{{Изображение}}
{image_code}

\\end{{document}}"""
    
    with open("document.tex", "w", encoding="utf-8") as f:
        f.write(full_document)
    
    subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", "document.tex"],
        capture_output=True,
        text=True,
        cwd=os.path.dirname(os.path.abspath("document.tex")) or "."
    )


if __name__ == "__main__":
    main()

