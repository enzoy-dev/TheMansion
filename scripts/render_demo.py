"""Render the recorded terminal text into a silent MP4 using Chromium and FFmpeg."""

import argparse
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.record_demo import write_recording

HTML = """<!doctype html><html lang="pt-BR"><meta charset="utf-8"><style>
*{box-sizing:border-box}body{margin:0;background:#111714;color:#e2e8de;font:18px/1.35 "DejaVu Sans Mono",monospace;padding:24px}
header{font-size:20px;color:#c6dda7;padding:8px 0 20px;border-bottom:1px solid #4b5949}
small{display:block;color:#a5b4a3;font-size:14px;margin-top:9px}
pre{height:655px;overflow:hidden;white-space:pre-wrap;overflow-wrap:anywhere;margin:18px 0 0}
</style><header>TheMansion · demonstração automatizada<small>Seed 7 · percurso real pelo terminal · contém spoilers · sem áudio</small></header><pre id="terminal"></pre></html>"""


def render(output):
    from playwright.sync_api import sync_playwright

    output = Path(output).resolve()
    recording = write_recording(output)
    with TemporaryDirectory(prefix="mansion-video-") as directory:
        directory = Path(directory)
        with sync_playwright() as driver:
            browser = driver.chromium.launch(
                executable_path=os.getenv("CHROMIUM_EXECUTABLE") or None
            )
            page = browser.new_page(
                viewport={"width": 1280, "height": 800}, device_scale_factor=1
            )
            page.set_content(HTML)
            for i, text in enumerate(recording["frames"]):
                page.locator("#terminal").evaluate(
                    "(element,text)=>{element.textContent=text;element.scrollTop=element.scrollHeight}",
                    text,
                )
                page.screenshot(path=str(directory / f"frame-{i:03}.png"))
            browser.close()
        playlist = directory / "frames.txt"
        playlist.write_text(
            "".join(
                f"file 'frame-{i:03}.png'\nduration {4 if i == len(recording['frames']) - 1 else 2.5}\n"
                for i in range(len(recording["frames"]))
            )
            + f"file 'frame-{len(recording['frames']) - 1:03}.png'\n",
            encoding="utf-8",
        )
        subprocess.run(
            [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(playlist),
                "-vf",
                "fps=12",
                "-c:v",
                "libx264",
                "-crf",
                "25",
                "-pix_fmt",
                "yuv420p",
                "-movflags",
                "+faststart",
                str(output / "themansion.mp4"),
            ],
            check=True,
        )
    return output / "themansion.mp4"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "docs/demo")
    print(render(parser.parse_args().output))
