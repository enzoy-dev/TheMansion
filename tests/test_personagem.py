import random

import pytest

from Personagem import Personagem, CURA_BANDAGEM
from armas import faca, pistola
from inimigo import Inimigo


def test_gun_consumes_ammo_even_when_it_misses():
    class SempreErra:
        def randint(self, minimo, maximo):
            return maximo
    jogador = Personagem('Enzo')
    jogador.adicionar_item('pistola')
    jogador.adicionar_item('munição', quantidade=2)
    assert jogador.equipar_arma(pistola)
    inimigo = Inimigo('Teste', 100)
    ataque = jogador.atacar(inimigo, SempreErra())
    assert ataque.executado and ataque.dano == 0
    assert jogador.quantidade_item('munição') == 1
    jogador.atacar(inimigo, SempreErra())
    assert not jogador.atacar(inimigo).executado
    assert inimigo.vida == 100


def test_knife_and_fists_do_not_require_ammo():
    jogador = Personagem('Enzo')
    inimigo = Inimigo('Teste', 100)
    assert jogador.atacar(inimigo, random.Random(1)).executado
    jogador.adicionar_item('faca')
    jogador.equipar_arma(faca)
    assert jogador.atacar(inimigo, random.Random(1)).executado
    assert jogador.quantidade_item('munição') == 0


def test_bandage_caps_life_and_does_not_get_wasted_at_full_life():
    jogador = Personagem('Enzo')
    jogador.adicionar_item('bandagem', quantidade=2)
    assert jogador.usar_bandagem() == 0
    assert jogador.quantidade_item('bandagem') == 2
    jogador.receber_dano(60)
    assert jogador.usar_bandagem() == CURA_BANDAGEM
    assert jogador.usar_bandagem() == 20
    assert jogador.vida == 100 and jogador.quantidade_item('bandagem') == 0


@pytest.mark.parametrize('quantidade', [0, -1, True, 1.5])
def test_invalid_item_quantities_are_rejected(quantidade):
    jogador = Personagem('Enzo')
    with pytest.raises(ValueError):
        jogador.adicionar_item('bandagem', quantidade=quantidade)
    with pytest.raises(ValueError):
        jogador.usar_item('bandagem', quantidade)
    assert jogador.inventario == []


def test_inventory_copies_do_not_share_mutable_objects():
    inventario = [{'nome': 'bandagem', 'tipo': 'cura', 'quantidade': 1}]
    primeiro = Personagem('Um', inventario=inventario)
    segundo = Personagem('Dois', inventario=inventario)
    primeiro.usar_item('bandagem')
    assert segundo.quantidade_item('bandagem') == inventario[0]['quantidade'] == 1
