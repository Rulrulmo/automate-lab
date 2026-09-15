import csv
import hashlib
import os

import pytest

from automate_lab.duplicate_files import find_duplicates, main, sha256_file, signature, write_report


def test_names_and_sizes_are_not_content(tmp_path):
    (tmp_path / "a").write_bytes(b"same")
    (tmp_path / "b").write_bytes(b"same")
    (tmp_path / "c").write_bytes(b"diff")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub/a").write_bytes(b"else")
    groups = find_duplicates(tmp_path)
    assert len(groups) == 1
    assert groups[0]["paths"] == ["a", "b"]
    assert groups[0]["sha256"] == hashlib.sha256(b"same").hexdigest()
    assert (tmp_path / "a").read_bytes() == b"same"


def test_empty_files_are_candidates(tmp_path):
    (tmp_path / "a").touch()
    (tmp_path / "b").touch()
    assert find_duplicates(tmp_path)[0]["size_bytes"] == 0


def test_symlinks_and_hardlinks_are_skipped(tmp_path):
    (tmp_path / "a").write_bytes(b"same")
    try:
        (tmp_path / "link").symlink_to(tmp_path / "a")
        (tmp_path / "loop").symlink_to(tmp_path, target_is_directory=True)
        os.link(tmp_path / "a", tmp_path / "hardlink")
    except OSError:
        pytest.skip("Links not supported on this filesystem")
    assert find_duplicates(tmp_path) == []


def test_changed_file_rejected(tmp_path):
    path = tmp_path / "a"
    path.write_bytes(b"old")
    expected = signature(path.stat())
    path.write_bytes(b"new content")
    with pytest.raises(ValueError, match="changed"):
        sha256_file(path, expected)


def test_unique_size_not_hashed(tmp_path, monkeypatch):
    (tmp_path / "a").write_bytes(b"a")
    (tmp_path / "b").write_bytes(b"bb")
    def forbidden(*args):
        raise AssertionError("Unique sizes should not be hashed")
    monkeypatch.setattr("automate_lab.duplicate_files.sha256_file", forbidden)
    assert find_duplicates(tmp_path) == []


def test_csv_roundtrip_and_formula_escaping(tmp_path):
    root = tmp_path / "input"
    root.mkdir()
    (root / "=danger.txt").write_bytes(b"x")
    (root / "a,b.txt").write_bytes(b"x")
    output = tmp_path / "report.csv"
    write_report(root, output, find_duplicates(root))
    assert output.read_bytes().startswith(b"\xef\xbb\xbf")
    with output.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert [r["relative_path"] for r in rows] == ["'=danger.txt", "a,b.txt"]
    with pytest.raises(FileExistsError):
        write_report(root, output, [])


def test_report_cannot_be_an_input_file(tmp_path):
    source = tmp_path / "data.csv"
    source.write_text("original")
    with pytest.raises(ValueError, match="outside"):
        write_report(tmp_path, source, [])
    assert source.read_text() == "original"


def test_cli_with_no_duplicates(tmp_path, capsys):
    root = tmp_path / "in"
    root.mkdir()
    output = tmp_path / "report.csv"
    assert main(["--input", str(root), "--out", str(output)]) == 0
    assert "groups=0 candidate_files=0" in capsys.readouterr().out
    assert len(output.read_text(encoding="utf-8-sig").splitlines()) == 1


def test_scan_error_does_not_create_report(tmp_path, monkeypatch):
    root = tmp_path / "in"
    root.mkdir()
    (root / "a").write_bytes(b"x")
    (root / "b").write_bytes(b"x")
    def fail(*args):
        raise PermissionError("unreadable")
    monkeypatch.setattr("automate_lab.duplicate_files.sha256_file", fail)
    output = tmp_path / "report.csv"
    with pytest.raises(SystemExit) as error:
        main(["--input", str(root), "--out", str(output)])
    assert error.value.code == 1
    assert not output.exists()
