"""Build a source ZIP from an explicit public allowlist, without saves or venvs."""

import argparse
import hashlib
from pathlib import Path
import sys
from zipfile import ZipFile, ZIP_DEFLATED, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from versao import __version__

FILES = (
    "TheMansion.py",
    "versao.py",
    "interface.py",
    "jogo.py",
    "locais.py",
    "Personagem.py",
    "armas.py",
    "inimigo.py",
    "combate.py",
    "Json.py",
    "utilidades.py",
    "README.md",
    "CHANGELOG.md",
    "docs/primeira-partida.md",
    "docs/demo/README.md",
    "docs/demo/playthrough.cast",
    "docs/demo/playthrough.txt",
    "docs/demo/themansion.mp4",
    "requirements-dev.txt",
    "requirements-demo.txt",
    "pytest.ini",
    "scripts/build_release.py",
    "scripts/record_demo.py",
    "scripts/render_demo.py",
    "tests/test_personagem.py",
    "tests/test_jogo.py",
    "tests/test_interface.py",
    "tests/test_save.py",
    "tests/test_release.py",
)


def build(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    name = f"TheMansion-{__version__}"
    archive = output / f"{name}.zip"
    with ZipFile(archive, "w", compression=ZIP_DEFLATED) as target:
        for filename in FILES:
            info = ZipInfo(f"{name}/{filename}", date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            target.writestr(info, (ROOT / filename).read_bytes())
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    checksum = output / "SHA256SUMS.txt"
    checksum.write_text(f"{digest}  {archive.name}\n", encoding="utf-8")
    return archive, checksum


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    for path in build(args.output):
        print(path)


if __name__ == "__main__":
    main()
