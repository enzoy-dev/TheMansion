import os
from pathlib import Path
import subprocess
import sys

from interface import executar
from jogo import Partida

ROOT = Path(__file__).resolve().parents[1]


def test_import_does_not_ask_for_input_or_create_save(tmp_path):
    result = subprocess.run([sys.executable, '-c', 'import TheMansion'], cwd=tmp_path,
                            env={**os.environ, 'PYTHONPATH': str(ROOT)}, input='',
                            capture_output=True, text=True, timeout=5)
    assert result.returncode == 0 and result.stdout == ''
    assert not (tmp_path / 'save.json').exists()


def test_eof_exits_without_traceback(tmp_path):
    result = subprocess.run([sys.executable, str(ROOT / 'TheMansion.py')], cwd=tmp_path,
                            input='', capture_output=True, text=True, timeout=5)
    assert result.returncode == 0 and 'Traceback' not in result.stderr
    assert 'Entrada encerrada' in result.stdout


def test_real_cli_new_game_save_and_reload(tmp_path):
    destino = tmp_path / 'save.json'
    first = subprocess.run([sys.executable, str(ROOT / 'TheMansion.py'), '--seed', '7', '--save', str(destino)],
                           input='1\nJogador Teste\n1\n1\ns\nq\n', capture_output=True, text=True, timeout=5)
    assert first.returncode == 0 and destino.exists()
    second = subprocess.run([sys.executable, str(ROOT / 'TheMansion.py'), '--save', str(destino), '--load'],
                            input='i\n0\nq\n', capture_output=True, text=True, timeout=5)
    assert second.returncode == 0
    assert 'Sala de jantar' in second.stdout and 'faca x1' in second.stdout


def test_loading_failure_keeps_current_game(tmp_path):
    partida = Partida.nova('Enzo', seed=1)
    commands = iter(['c', 'q'])
    output = []
    result = executar(partida, tmp_path / 'missing.json', lambda _: next(commands), output.append)
    assert result is partida and result.jogador.nome == 'Enzo'
    assert any('Nenhum save' in mensagem for mensagem in output)


def test_victory_and_defeat_do_not_request_another_input():
    partida = Partida.nova('Enzo')
    partida.status = 'derrota'
    partida.jogador.vida = 0
    output = []
    def unexpected(_):
        raise AssertionError('A partida encerrada não deve pedir comandos')
    executar(partida, entrada=unexpected, saida=output.append)
    assert 'FIM DE JOGO' in output[-1]
    partida.status = 'vitoria'
    output.clear()
    executar(partida, entrada=unexpected, saida=output.append)
    assert 'VITÓRIA' in output[-1]


def test_real_cli_reaches_alternative_ending_and_exits(tmp_path):
    from locais import LOCAIS
    partida = Partida.nova('Teste', seed=7)
    comandos = ['1', 'Teste']
    caminho = ['helena', 'davi', 'mover:cozinha', 'armario', 'despensa_proteger',
               'mover:entrada', 'mover:jantar', 'mesa', 'corredor', 'mover:subsolo',
               'gerador', 'mover:garagem', 'saida_alternativa']
    for acao in caminho:
        while partida.inimigo_ativo and not partida.terminou:
            curar = partida.jogador.vida <= 55 and partida.jogador.quantidade_item('bandagem')
            comandos.append('2' if curar else '1')
            partida.turno('curar' if curar else 'atacar')
        assert not partida.terminou
        opcoes = [codigo for _, codigo in LOCAIS[partida.local].opcoes]
        comandos.append(str(opcoes.index(acao) + 1))
        partida.executar(acao)
    assert partida.status == 'vitoria'
    result = subprocess.run([sys.executable, str(ROOT / 'TheMansion.py'), '--seed', '7'], cwd=tmp_path,
                            input='\n'.join(comandos) + '\n', capture_output=True, text=True, timeout=5)
    assert result.returncode == 0 and '=== VITÓRIA ===' in result.stdout
    assert 'Entrada encerrada' not in result.stdout and 'Traceback' not in result.stderr
    assert not (tmp_path / 'save.json').exists()


def test_real_cli_death_finishes_without_another_menu(tmp_path):
    partida = Partida.nova('Teste', seed=1)
    comandos = ['1', 'Teste', '1', '1', '3']  # jantar, mesa, corredor
    partida.executar('mover:jantar')
    partida.executar('mesa')
    partida.executar('corredor')
    while not partida.terminou:
        comandos.append('4')
        partida.turno('recuar')
        if not partida.terminou:
            comandos.append('3')
            partida.executar('corredor')
    result = subprocess.run([sys.executable, str(ROOT / 'TheMansion.py'), '--seed', '1'], cwd=tmp_path,
                            input='\n'.join(comandos) + '\n', capture_output=True, text=True, timeout=5)
    assert result.returncode == 0 and 'FIM DE JOGO' in result.stdout
    assert 'Entrada encerrada' not in result.stdout and 'Traceback' not in result.stderr
