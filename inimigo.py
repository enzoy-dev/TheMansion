from dataclasses import dataclass
import random


@dataclass
class Inimigo:
    nome: str
    vida: int
    dano_min: int = 10
    dano_max: int = 15
    chance_acerto: int = 70

    def esta_vivo(self):
        return self.vida > 0

    def receber_dano(self, dano):
        self.vida = max(0, self.vida - dano)

    def atacar(self, alvo, rng=None):
        rng = rng or random
        if rng.randint(1, 100) > self.chance_acerto:
            return 0
        return alvo.receber_dano(rng.randint(self.dano_min, self.dano_max))


# id: nome, vida máxima, dano mínimo, dano máximo, chance de acerto
INIMIGOS = {'zumbi': ('Zumbi do corredor', 30, 8, 13, 65),
            'rastejante': ('Rastejante da despensa', 20, 5, 9, 60),
            'criatura': ('A Criatura', 100, 12, 20, 65)}
