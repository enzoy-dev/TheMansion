import hashlib
from pathlib import Path
import subprocess
import sys
from zipfile import ZipFile

from scripts.build_release import build
from scripts.record_demo import capture_demo
from versao import __version__


def test_archive_is_reproducible_and_runs_without_the_checkout(tmp_path):
    archive, checksum = build(tmp_path / "release")
    original = archive.read_bytes()
    build(tmp_path / "release")
    assert archive.read_bytes() == original
    assert checksum.read_text().split()[0] == hashlib.sha256(original).hexdigest()
    with ZipFile(archive) as package:
        assert all(not Path(name).name.endswith(".json") for name in package.namelist())
        assert not any(
            ".venv" in name or "__pycache__" in name for name in package.namelist()
        )
        package.extractall(tmp_path / "extracted")
    folder = tmp_path / "extracted" / f"TheMansion-{__version__}"
    version = subprocess.run(
        [sys.executable, "TheMansion.py", "--version"],
        cwd=folder,
        capture_output=True,
        text=True,
        check=True,
    )
    assert __version__ in version.stdout
    run = subprocess.run(
        [sys.executable, "TheMansion.py"],
        cwd=folder,
        input="3\n",
        capture_output=True,
        text=True,
        timeout=5,
    )
    assert run.returncode == 0 and "Traceback" not in run.stderr


def test_demo_reaches_victory_and_records_save_load_without_touching_player_save(
    tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    player = tmp_path / "save.json"
    player.write_text("personal file, do not read or overwrite")
    before = player.read_bytes()
    data = capture_demo()
    assert "=== VITÓRIA ===" in data["text"]
    assert "Jogo salvo em demo-save.json" in data["text"]
    assert "Progresso de Sobrevivente carregado" in data["text"]
    assert player.read_bytes() == before
    assert not (tmp_path / "demo-save.json").exists()
