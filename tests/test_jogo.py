import pytest

from armas import faca, pistola
from jogo import Partida
from inimigo import INIMIGOS
from locais import LOCAIS


def mesa(partida):
    partida.executar('mover:jantar')
    partida.executar('mesa')


def vencer_combate(partida):
    for _ in range(100):
        if partida.terminou or not partida.inimigo_ativo:
            return
        if partida.jogador.vida <= 55 and partida.jogador.quantidade_item('bandagem'):
            partida.turno('curar')
        else:
            if partida.jogador.arma_equipada == pistola and not partida.jogador.quantidade_item('munição'):
                partida.jogador.equipar_arma(faca)
            partida.turno('atacar')
    pytest.fail('Combate não terminou após 100 turnos')


def preparar_subsolo(partida):
    partida.executar('helena')
    partida.executar('davi')
    mesa(partida)
    partida.executar('corredor')
    vencer_combate(partida)
    assert not partida.terminou
    partida.executar('mover:quarto')
    partida.executar('quarto')
    partida.executar('mover:corredor')
    partida.executar('mover:escritorio')
    partida.executar('pistola')
    partida.executar('mover:corredor')
    partida.executar('mover:subsolo')
    partida.executar('recursos')


def test_full_confrontation_route_can_win():
    partida = Partida.nova('Enzo', seed=7)
    preparar_subsolo(partida)
    partida.executar('gerador')
    partida.jogador.equipar_arma(pistola)
    partida.executar('criatura')
    vencer_combate(partida)
    assert partida.vidas_inimigos['criatura'] == 0
    partida.executar('mover:garagem')
    partida.executar('saida_principal')
    assert partida.status == 'vitoria' and partida.final == 'confronto'
    from Json import dados_para_partida, criar_dados_save
    assert dados_para_partida(criar_dados_save(partida)).status == 'vitoria'
    local = partida.local
    partida.executar('mover:subsolo')
    assert partida.local == local


def test_full_alternative_route_avoids_boss_and_spends_one_fuse():
    partida = Partida.nova('Enzo', seed=7)
    partida.executar('helena')
    partida.executar('davi')
    partida.executar('mover:cozinha')
    partida.executar('armario')
    vida = partida.jogador.vida
    partida.executar('despensa_proteger')
    assert partida.jogador.vida == vida
    assert partida.jogador.quantidade_item('fusível') == 1
    partida.executar('mover:entrada')
    mesa(partida)
    partida.executar('corredor')
    vencer_combate(partida)
    partida.executar('mover:subsolo')
    partida.executar('gerador')
    assert partida.jogador.quantidade_item('fusível') == 1
    partida.executar('mover:garagem')
    partida.executar('saida_alternativa')
    assert partida.status == 'vitoria' and partida.final == 'manutencao'
    from Json import dados_para_partida, criar_dados_save
    assert dados_para_partida(criar_dados_save(partida)).final == 'manutencao'
    assert partida.vidas_inimigos['criatura'] == INIMIGOS['criatura'][1]
    assert partida.jogador.quantidade_item('fusível') == 0


def test_helena_prevents_ambush_and_does_not_give_infinite_supplies():
    sem = Partida.nova('Sem ajuda', seed=1)
    com = Partida.nova('Com ajuda', seed=1)
    com.executar('helena')
    com.executar('helena')
    assert com.jogador.quantidade_item('bandagem') == 1
    for partida in [sem, com]:
        mesa(partida)
        partida.executar('corredor')
    assert sem.jogador.vida == 92 and com.jogador.vida == 100


def test_invalid_combat_action_and_empty_pistol_do_not_give_enemy_a_turn():
    partida = Partida.nova('Enzo', seed=1)
    mesa(partida)
    partida.executar('corredor')
    partida.jogador.adicionar_item('pistola')
    partida.jogador.equipar_arma(pistola)
    antes = (partida.jogador.vida, partida.rng.getstate(), dict(partida.vidas_inimigos))
    partida.turno('invalida')
    partida.turno('atacar')
    assert (partida.jogador.vida, partida.rng.getstate(), partida.vidas_inimigos) == antes


def test_retreat_preserves_enemy_life_and_does_not_repeat_ambush():
    partida = Partida.nova('Enzo', seed=1)
    mesa(partida)
    partida.executar('corredor')
    partida.turno('atacar')
    restante = partida.vidas_inimigos['zumbi']
    vida = partida.jogador.vida
    partida.turno('recuar')
    assert partida.jogador.vida == vida - 6 and partida.local == 'jantar'
    partida.executar('corredor')
    assert partida.vidas_inimigos['zumbi'] == restante
    assert partida.jogador.vida == vida - 6


def test_risky_supply_choice_can_kill_and_stops_all_actions():
    partida = Partida.nova('Enzo')
    partida.executar('mover:cozinha')
    partida.jogador.vida = 5
    partida.executar('despensa_forcar')
    assert partida.status == 'derrota'
    assert partida.jogador.quantidade_item('fusível') == 0
    partida.executar('armario')
    assert partida.jogador.quantidade_item('bandagem') == 0


def test_supplies_and_random_events_cannot_be_farmed():
    partida = Partida.nova('Enzo', seed=7)
    mesa(partida)
    partida.executar('gaveta')
    antes = (partida.rng.getstate(), list(partida.jogador.inventario))
    partida.executar('gaveta')
    partida.executar('mesa')
    assert (partida.rng.getstate(), partida.jogador.inventario) == antes
    partida.executar('mover:entrada')
    partida.executar('mover:cozinha')
    partida.executar('armario')
    quantidade = partida.jogador.quantidade_item('bandagem')
    partida.executar('armario')
    assert partida.jogador.quantidade_item('bandagem') == quantidade


def test_davi_is_optional_and_using_fuse_changes_available_exit():
    partida = Partida.nova('Enzo', seed=7)
    partida.executar('mover:cozinha')
    partida.executar('despensa_forcar')
    partida.executar('mover:entrada')
    mesa(partida)
    partida.executar('corredor')
    vencer_combate(partida)
    partida.executar('mover:subsolo')
    partida.executar('gerador')
    assert partida.flags['gerador']
    assert partida.jogador.quantidade_item('fusível') == 0
    partida.executar('mover:garagem')
    partida.executar('saida_alternativa')
    assert not partida.terminou
    partida.executar('saida_principal')
    assert not partida.terminou


def test_map_has_no_unknown_destinations():
    for local in LOCAIS.values():
        for _, acao in local.opcoes:
            if acao.startswith('mover:'):
                assert acao.split(':')[1] in LOCAIS


def test_death_in_combat_finishes_before_any_more_exploration():
    partida = Partida.nova('Enzo', seed=1)
    mesa(partida)
    partida.executar('corredor')
    partida.jogador.vida = 1
    partida.turno('recuar')
    assert partida.jogador.vida == 0 and partida.status == 'derrota'
    assert partida.inimigo_ativo is None
    partida.executar('mesa')
    assert partida.jogador.vida == 0


def test_noise_encounter_cannot_be_rerolled_after_retreat():
    partida = Partida.nova('Enzo', seed=1)
    partida.executar('mover:cozinha')
    partida.executar('ruido')
    assert partida.inimigo_ativo == 'rastejante'
    partida.turno('atacar')
    restante = partida.vidas_inimigos['rastejante']
    partida.turno('recuar')
    partida.executar('mover:cozinha')
    estado_rng = partida.rng.getstate()
    partida.executar('ruido')
    assert partida.vidas_inimigos['rastejante'] == restante
    assert partida.rng.getstate() == estado_rng
    vencer_combate(partida)
    assert not partida.terminou
    municao = partida.jogador.quantidade_item('munição')
    partida.executar('ruido')
    assert partida.jogador.quantidade_item('munição') == municao
