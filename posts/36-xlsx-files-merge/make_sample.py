"""Create synthetic input workbooks for the tutorial, never overwrite files."""
from pathlib import Path

from openpyxl import Workbook


def main():
    folder = Path("sample_xlsx")
    folder.mkdir(exist_ok=True)
    samples = {
        "01_seoul.xlsx": [["product", "qty"], ["A", 3], ["B", 2]],
        "02_busan.xlsx": [["qty", "product"], [4, "A"], [1, "C"]],
    }
    for name in samples:
        if (folder / name).exists():
            raise SystemExit(f"Already exists: {folder / name}")
    for name, rows in samples.items():
        book = Workbook()
        book.active.title = "sales"
        for row in rows:
            book.active.append(row)
        book.save(folder / name)
        book.close()
        print(folder / name)


if __name__ == "__main__":
    main()
