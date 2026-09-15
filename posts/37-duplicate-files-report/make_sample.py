"""Build an isolated synthetic fixture folder, failing if it already exists."""
from pathlib import Path


def main():
    root = Path("duplicate_sample")
    root.mkdir(exist_ok=False)
    (root / "archive").mkdir()
    (root / "report.txt").write_bytes(b"monthly report\n")
    (root / "archive" / "report_copy.txt").write_bytes(b"monthly report\n")
    (root / "different.txt").write_bytes(b"another report\n")
    print(f"created: {root} (3 files)")


if __name__ == "__main__":
    main()
