"""Record a real, scripted CLI playthrough; pacing is generated, not human timing."""

import argparse
from contextlib import chdir
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from jogo import Partida
from locais import LOCAIS
from interface import rodar
from versao import __version__


def planned_inputs():
    game = Partida.nova("Sobrevivente", seed=7)
    commands = ["1", "Sobrevivente", "m", "o"]
    route = [
        "helena",
        "davi",
        "mover:cozinha",
        "armario",
        "despensa_proteger",
        "mover:entrada",
        "mover:jantar",
        "mesa",
        "corredor",
        "mover:subsolo",
        "gerador",
        "mover:garagem",
        "saida_alternativa",
    ]
    for action in route:
        for _ in range(100):
            if not game.inimigo_ativo:
                break
            heal = game.jogador.vida <= 55 and game.jogador.quantidade_item("bandagem")
            commands.append("2" if heal else "1")
            game.turno("curar" if heal else "atacar")
        if game.terminou:
            raise RuntimeError("Demo route ended unexpectedly")
        options = [code for _, code in LOCAIS[game.local].opcoes]
        commands.append(str(options.index(action) + 1))
        game.executar(action)
        if action == "mesa":
            commands.extend(["i", "1", "s", "c"])
    if game.final != "manutencao":
        raise RuntimeError("Demo must reach the maintenance ending")
    return commands


def capture_demo():
    commands = iter(planned_inputs())
    text = []
    frames = []
    events = []
    timestamp = 0.0

    def emit(value, pause=0.03):
        nonlocal timestamp
        text.append(value)
        events.append([round(timestamp, 3), "o", value])
        timestamp += pause

    def output(value=""):
        emit(str(value) + "\n")

    def input_value(prompt):
        command = next(commands)
        emit(prompt)
        emit(command + "\n", 2.5)
        frames.append("".join(text))
        return command

    with TemporaryDirectory(prefix="mansion-demo-") as directory, chdir(directory):
        code = rodar(
            caminho=Path("demo-save.json"), seed=7, entrada=input_value, saida=output
        )
    transcript = "".join(text)
    if code != 0 or "=== VITÓRIA ===" not in transcript:
        raise RuntimeError("The real CLI did not finish the recorded route")
    frames.append(transcript)
    return {
        "text": transcript,
        "events": events,
        "frames": frames,
        "duration": timestamp,
    }


def write_recording(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    recording = capture_demo()
    header = {
        "version": 2,
        "width": 120,
        "height": 32,
        "title": f"TheMansion {__version__} — automated seeded playthrough",
        "duration": recording["duration"],
    }
    with (output / "playthrough.cast").open("w", encoding="utf-8") as stream:
        for row in [header, *recording["events"]]:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    (output / "playthrough.txt").write_text(recording["text"], encoding="utf-8")
    return recording


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "docs/demo")
    args = parser.parse_args()
    data = write_recording(args.output)
    print(
        f"Recorded actual CLI output: {len(data['frames'])} frames; maintenance ending."
    )


if __name__ == "__main__":
    main()
