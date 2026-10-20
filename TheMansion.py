"""Ponto de entrada: importar este módulo não inicia uma partida."""
import argparse
from pathlib import Path

from interface import rodar


def main(argv=None):
    parser = argparse.ArgumentParser(description='TheMansion: uma aventura de sobrevivência no terminal.')
    parser.add_argument('--seed', type=int, help='Semente opcional para repetir a mesma sequência aleatória')
    parser.add_argument('--save', type=Path, default=Path('save.json'), help='Caminho do save (padrão: save.json)')
    parser.add_argument('--load', action='store_true', help='Carregar diretamente o save, sem criar outra partida')
    args = parser.parse_args(argv)
    return rodar(args.save, args.seed, args.load)


if __name__ == '__main__':
    raise SystemExit(main())
