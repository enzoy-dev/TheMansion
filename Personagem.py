from copy import deepcopy
from dataclasses import dataclass
from typing import TypedDict

from armas import Arma, punhos

CURA_BANDAGEM = 40
TIPOS_ITENS = {'faca': 'arma', 'pistola': 'arma', 'munição': 'munição',
               'bandagem': 'cura', 'chave de caveira': 'chave', 'fusível': 'peça'}


class Item(TypedDict):
    nome: str
    tipo: str
    quantidade: int


def inteiro_positivo(valor):
    if type(valor) is not int or valor <= 0:
        raise ValueError('A quantidade deve ser um inteiro positivo.')


@dataclass(frozen=True)
class Ataque:
    executado: bool
    dano: int
    arma: str


class Personagem:
    def __init__(self, nome: str, vida: int = 100, inventario: list[Item] | None = None):
        if not isinstance(nome, str) or not 1 <= len(nome.strip()) <= 100:
            raise ValueError('O nome deve ter entre 1 e 100 caracteres.')
        inteiro_positivo(vida)
        self.nome = nome.strip()
        self.vida_maxima = vida
        self._vida = vida
        self.inventario = deepcopy(inventario) if inventario is not None else []
        self.arma_equipada: Arma | None = None

    @property
    def vida(self):
        return self._vida

    @vida.setter
    def vida(self, valor):
        if type(valor) is not int:
            raise ValueError('Vida deve ser um inteiro.')
        self._vida = max(0, min(valor, self.vida_maxima))

    def equipar_arma(self, arma):
        if self.quantidade_item(arma.nome) == 0:
            return False
        self.arma_equipada = arma
        return True

    def atacar(self, inimigo, rng=None):
        arma = self.arma_equipada or punhos
        if arma.usa_municao and not self.usar_item('munição'):
            return Ataque(False, 0, arma.nome)
        return Ataque(True, arma.atacar(inimigo, rng), arma.nome)

    def adicionar_item(self, nome_item, tipo=None, quantidade=1):
        inteiro_positivo(quantidade)
        if nome_item not in TIPOS_ITENS or (tipo is not None and tipo != TIPOS_ITENS[nome_item]):
            raise ValueError('Item ou tipo desconhecido.')
        for item in self.inventario:
            if item['nome'] == nome_item:
                item['quantidade'] += quantidade
                return
        self.inventario.append({'nome': nome_item, 'tipo': TIPOS_ITENS[nome_item], 'quantidade': quantidade})

    def quantidade_item(self, nome_item):
        return next((item['quantidade'] for item in self.inventario if item['nome'] == nome_item), 0)

    def usar_item(self, nome_item, quantidade=1):
        inteiro_positivo(quantidade)
        for item in self.inventario:
            if item['nome'] == nome_item and item['quantidade'] >= quantidade:
                item['quantidade'] -= quantidade
                if not item['quantidade']:
                    self.inventario.remove(item)
                return True
        return False

    def usar_bandagem(self):
        if self.vida == 0 or self.vida == self.vida_maxima or not self.usar_item('bandagem'):
            return 0
        return self.curar(CURA_BANDAGEM)

    def receber_dano(self, dano):
        inteiro_positivo(dano)
        antes = self.vida
        self.vida -= dano
        return antes - self.vida

    def curar(self, quantidade):
        inteiro_positivo(quantidade)
        antes = self.vida
        self.vida += quantidade
        return self.vida - antes

    def esta_vivo(self):
        return self.vida > 0
