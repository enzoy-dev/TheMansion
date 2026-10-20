from copy import deepcopy
import json
from pathlib import Path

import pytest

import Json
from Json import carregar_jogo, salvar_jogo, criar_dados_save, dados_para_partida, ErroSave
from jogo import Partida


def em_combate():
    partida = Partida.nova('Vitória', seed=17)
    partida.executar('helena')
    partida.executar('mover:jantar')
    partida.executar('mesa')
    partida.executar('corredor')
    partida.turno('atacar')
    return partida


def test_round_trip_preserves_name_inventory_flags_enemy_and_rng(tmp_path):
    partida = em_combate()
    destino = tmp_path / 'save.json'
    salvar_jogo(partida, destino)
    carregada = carregar_jogo(destino)
    assert criar_dados_save(carregada) == criar_dados_save(partida)
    mensagens = partida.turno('atacar')
    assert carregada.turno('atacar') == mensagens
    assert criar_dados_save(carregada) == criar_dados_save(partida)
    carregada.jogador.adicionar_item('bandagem')
    assert carregada.jogador.quantidade_item('bandagem') != partida.jogador.quantidade_item('bandagem')


def test_failed_replace_preserves_previous_save_and_removes_temporary_file(tmp_path, monkeypatch):
    destino = tmp_path / 'save.json'
    salvar_jogo(Partida.nova('Antes', seed=1), destino)
    anterior = destino.read_bytes()
    def falhar(*args):
        raise OSError('falha simulada')
    monkeypatch.setattr(Json.os, 'replace', falhar)
    with pytest.raises(ErroSave, match='falha simulada'):
        salvar_jogo(Partida.nova('Depois', seed=2), destino)
    assert destino.read_bytes() == anterior
    assert list(tmp_path.iterdir()) == [destino]


def test_failed_serialization_never_overwrites_valid_save(tmp_path):
    destino = tmp_path / 'save.json'
    partida = Partida.nova('Antes')
    salvar_jogo(partida, destino)
    anterior = destino.read_bytes()
    partida.jogador.inventario.append({'nome': 'desconhecido', 'tipo': 'cura', 'quantidade': 1})
    with pytest.raises(ErroSave):
        salvar_jogo(partida, destino)
    assert destino.read_bytes() == anterior


@pytest.mark.parametrize('alterar', [
    lambda d: d.update(versao=999),
    lambda d: d.update(versao=True),
    lambda d: d.update(local='inexistente'),
    lambda d: d.update(status='vitoria'),
    lambda d: d.update(flags={}),
    lambda d: d['flags'].update(mesa='sim'),
    lambda d: d['jogador'].update(vida=-1),
    lambda d: d['jogador'].update(vida=101),
    lambda d: d['jogador'].update(vida=True),
    lambda d: d['jogador'].update(arma_equipada='pistola'),
    lambda d: d['jogador'].update(nome=''),
    lambda d: d['jogador'].update(inventario=[{'nome': 'bandagem', 'tipo': 'cura', 'quantidade': -1}]),
    lambda d: d['jogador'].update(inventario=[{'nome': 'laser', 'tipo': 'arma', 'quantidade': 1}]),
    lambda d: d.update(inimigo_ativo='criatura'),
    lambda d: d.update(vidas_inimigos={'zumbi': 30}),
    lambda d: d.update(rng_state=[3, [1], None]),
])
def test_invalid_json_structure_is_rejected_without_touching_current_game(tmp_path, alterar):
    atual = em_combate()
    estado_antes = deepcopy(criar_dados_save(atual))
    dados = json.loads(json.dumps(criar_dados_save(Partida.nova('Outra'))))
    alterar(dados)
    destino = tmp_path / 'invalid.json'
    destino.write_text(json.dumps(dados), encoding='utf-8')
    with pytest.raises(ErroSave):
        carregar_jogo(destino)
    assert criar_dados_save(atual) == estado_antes


@pytest.mark.parametrize('texto', ['{', '[]', 'null', '{"vida": 50}', '{"versao": 2}'])
def test_broken_saves_remain_intact(tmp_path, texto):
    destino = tmp_path / 'invalid.json'
    destino.write_text(texto)
    with pytest.raises(ErroSave):
        carregar_jogo(destino)
    assert destino.read_text() == texto


def test_missing_save_gives_clear_error(tmp_path):
    with pytest.raises(ErroSave, match='Nenhum save'):
        carregar_jogo(tmp_path / 'missing.json')


def legado():
    return {'vida': 80, 'inventario': [], 'arma_equipada': None,
            'estado': {'itens': dict.fromkeys(['faca_pega', 'chave_pega', 'mesa_explorada', 'pistola_pega'], False),
                       'conversas': dict.fromkeys(['conversa_helena', 'conversa_davi'], False),
                       'locais': dict.fromkeys(['despensa_explorada', 'armario_explorado', 'geladeira_explorada', 'quarto_explorado'], False),
                       'progresso': {'zumbi_derrotado': False},
                       'subsolo': dict.fromkeys(['gerador_ligado', 'boss_derrotado', 'municao_pega', 'bandagem_pega'], False)}}


def test_original_save_is_migrated_in_memory_without_rewriting_file(tmp_path):
    dados = legado()
    dados['inventario'] = [{'nome': 'faca', 'tipo': 'arma', 'quantidade': 1},
                           {'nome': 'chave de caveira', 'tipo': 'chave', 'quantidade': 1}]
    dados['arma_equipada'] = 'faca'
    dados['estado']['itens'].update(faca_pega=True, chave_pega=True)
    dados['estado']['progresso']['zumbi_derrotado'] = True
    destino = tmp_path / 'legacy.json'
    destino.write_text(json.dumps(dados))
    anterior = destino.read_bytes()
    partida = carregar_jogo(destino)
    assert partida.jogador.nome == 'Sobrevivente'
    assert partida.jogador.vida == 80
    assert partida.jogador.arma_equipada.nome == 'faca'
    assert partida.local == 'entrada' and partida.vidas_inimigos['zumbi'] == 0
    assert destino.read_bytes() == anterior


def test_terminal_defeat_can_be_saved_and_loaded(tmp_path):
    partida = Partida.nova('Enzo')
    partida.executar('mover:cozinha')
    partida.jogador.vida = 1
    partida.executar('despensa_forcar')
    salvar_jogo(partida, tmp_path / 'save.json')
    assert carregar_jogo(tmp_path / 'save.json').status == 'derrota'


def test_legacy_partial_supplies_neither_duplicate_nor_disappear():
    dados = legado()
    dados['estado']['subsolo']['municao_pega'] = True
    partida = dados_para_partida(dados)
    # O formato antigo não guardava a localização; simula a volta ao subsolo.
    partida.local = 'subsolo'
    partida.executar('recursos')
    assert partida.jogador.quantidade_item('munição') == 0
    assert partida.jogador.quantidade_item('bandagem') == 1
    partida.executar('recursos')
    assert partida.jogador.quantidade_item('bandagem') == 1


@pytest.mark.parametrize('seed', range(5))
def test_every_reachable_state_in_seeded_walks_can_be_saved(seed):
    import random
    from locais import LOCAIS
    escolher = random.Random(seed)
    partida = Partida.nova('Teste', seed)
    for _ in range(120):
        if partida.terminou:
            break
        if partida.inimigo_ativo:
            partida.turno(escolher.choice(['atacar', 'curar', 'recuar', 'invalida']))
        else:
            partida.executar(escolher.choice(LOCAIS[partida.local].opcoes)[1])
        clone = dados_para_partida(criar_dados_save(partida))
        assert criar_dados_save(clone) == criar_dados_save(partida)
