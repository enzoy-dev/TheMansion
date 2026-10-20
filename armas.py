"""Armas imutáveis; o inventário do personagem controla o gasto de munição."""
from dataclasses import dataclass
import random


@dataclass(frozen=True)
class Arma:
    nome: str
    dano_min: int
    dano_max: int
    chance_acerto: int
    usa_municao: bool = False

    def atacar(self, alvo, rng=None) -> int:
        rng = rng or random
        if rng.randint(1, 100) > self.chance_acerto:
            return 0
        dano = rng.randint(self.dano_min, self.dano_max)
        alvo.receber_dano(dano)
        return dano


class Faca(Arma):
    def __init__(self):
        super().__init__('faca', 10, 20, 80)


class Pistola(Arma):
    def __init__(self):
        super().__init__('pistola', 25, 40, 70, True)


faca = Faca()
pistola = Pistola()
punhos = Arma('punhos', 3, 6, 75)
armas = {'faca': faca, 'pistola': pistola}
