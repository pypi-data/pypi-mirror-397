import subprocess
from pathlib import Path


def run(cmd, cwd):
    return subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True,
    )


def test_creates_dump_file(tmp_path):
    (tmp_path / "a.txt").write_text("hello")

    run(["treedump"], cwd=tmp_path)

    dump = tmp_path / "dump.txt"
    assert dump.exists()
    assert "hello" in dump.read_text()


def test_tree_comes_before_file_contents(tmp_path):
    (tmp_path / "a.txt").write_text("content")

    run(["treedump"], cwd=tmp_path)

    text = (tmp_path / "dump.txt").read_text()

    tree_index = text.index("===== TREE STRUCTURE =====")
    file_index = text.index("===== FILE:")
    assert tree_index < file_index


def test_binary_files_are_ignored(tmp_path):
    # create fake binary
    (tmp_path / "bin.dat").write_bytes(b"\x00\x01\x02\x03")
    (tmp_path / "text.txt").write_text("visible")

    run(["treedump"], cwd=tmp_path)

    text = (tmp_path / "dump.txt").read_text()
    assert "visible" in text
    assert "===== FILE: bin.dat =====" not in text



def test_dump_file_is_not_self_ingested(tmp_path):
    (tmp_path / "a.txt").write_text("hello")

    run(["treedump"], cwd=tmp_path)
    run(["treedump"], cwd=tmp_path)

    text = (tmp_path / "dump.txt").read_text()

    # dump.txt should never appear as a dumped file
    assert "===== FILE: dump.txt =====" not in text


def test_gitignore_overrides_defaults(tmp_path):
    # default would ignore .env, but gitignore allows it
    (tmp_path / ".gitignore").write_text("")
    (tmp_path / ".env").write_text("SECRET=1")

    run(["treedump"], cwd=tmp_path)

    text = (tmp_path / "dump.txt").read_text()
    assert "SECRET=1" in text


def test_builtin_ignores_apply_without_gitignore(tmp_path):
    (tmp_path / ".env").write_text("SECRET=1")

    run(["treedump"], cwd=tmp_path)

    text = (tmp_path / "dump.txt").read_text()
    assert "SECRET=1" not in text


def test_ignore_off_includes_env(tmp_path):
    (tmp_path / ".env").write_text("SECRET=1")

    run(["treedump", "--ignore-off"], cwd=tmp_path)

    text = (tmp_path / "dump.txt").read_text()
    assert "SECRET=1" in text

def test_version_flag():
    result = subprocess.run(
        ["treedump", "--version"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "treedump 0.2.0" in result.stdout
