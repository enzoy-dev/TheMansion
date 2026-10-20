"""Save versionado, validação antes de carregar e substituição atômica do arquivo."""
from copy import deepcopy
import json
import os
from pathlib import Path
import random
import tempfile

from Personagem import Personagem, TIPOS_ITENS
from armas import armas
from inimigo import INIMIGOS
from jogo import Partida, FLAGS, LOCAIS_COMBATE
from locais import LOCAIS

VERSAO_SAVE = 2
MAX_SAVE_BYTES = 1024 * 1024


class ErroSave(ValueError):
    pass


def _inteiro(valor, minimo, maximo):
    if type(valor) is not int or not minimo <= valor <= maximo:
        raise ErroSave('Valor numérico inválido no save.')
    return valor


def _inventario(itens):
    if not isinstance(itens, list) or len(itens) > len(TIPOS_ITENS):
        raise ErroSave('Inventário inválido.')
    vistos = set()
    for item in itens:
        if not isinstance(item, dict) or set(item) != {'nome', 'tipo', 'quantidade'}:
            raise ErroSave('Item inválido no inventário.')
        nome = item['nome']
        if not isinstance(nome, str) or nome not in TIPOS_ITENS or nome in vistos or item['tipo'] != TIPOS_ITENS[nome]:
            raise ErroSave('Item desconhecido, repetido ou com tipo incorreto.')
        _inteiro(item['quantidade'], 1, 10000)
        vistos.add(nome)
    return deepcopy(itens)


def _estado_aleatorio(estado):
    if not isinstance(estado, list) or len(estado) != 3 or type(estado[0]) is not int or estado[0] != 3:
        raise ErroSave('Estado aleatório inválido.')
    valores = estado[1]
    if not isinstance(valores, list) or len(valores) != 625 or estado[2] is not None:
        raise ErroSave('Estado aleatório inválido.')
    for valor in valores[:-1]:
        _inteiro(valor, 0, 2**32 - 1)
    _inteiro(valores[-1], 0, 624)
    rng = random.Random()
    rng.setstate((3, tuple(valores), None))
    return rng


def criar_dados_save(partida):
    return {'versao': VERSAO_SAVE,
            'jogador': {'nome': partida.jogador.nome, 'vida': partida.jogador.vida,
                        'vida_maxima': partida.jogador.vida_maxima,
                        'inventario': deepcopy(partida.jogador.inventario),
                        'arma_equipada': partida.jogador.arma_equipada.nome if partida.jogador.arma_equipada else None},
            'local': partida.local, 'status': partida.status, 'final': partida.final,
            'flags': deepcopy(partida.flags), 'vidas_inimigos': deepcopy(partida.vidas_inimigos),
            'inimigo_ativo': partida.inimigo_ativo, 'rng_state': partida.rng.getstate()}


def _migrar_legado(dados):
    if not isinstance(dados.get('estado'), dict):
        raise ErroSave('Estado do save antigo está ausente ou inválido.')
    estado = dados['estado']
    grupos = {'itens', 'conversas', 'locais', 'progresso', 'subsolo'}
    if set(estado) != grupos or any(not isinstance(grupo, dict) for grupo in estado.values()):
        raise ErroSave('Estrutura do save antigo incompleta.')
    conhecidos = {'itens': {'faca_pega', 'chave_pega', 'mesa_explorada', 'pistola_pega'},
                   'conversas': {'conversa_helena', 'conversa_davi'},
                   'locais': {'despensa_explorada', 'armario_explorado', 'geladeira_explorada', 'quarto_explorado'},
                   'progresso': {'zumbi_derrotado'},
                   'subsolo': {'gerador_ligado', 'boss_derrotado', 'municao_pega', 'bandagem_pega'}}
    for nome, valores in estado.items():
        if set(valores) != conhecidos[nome] or any(type(valor) is not bool for valor in valores.values()):
            raise ErroSave('Flags inválidas no save antigo.')
    partida = Partida.nova(dados.get('nome', 'Sobrevivente'))
    novos = criar_dados_save(partida)
    novos['jogador'].update(vida=dados['vida'], inventario=dados['inventario'],
                            arma_equipada=dados.get('arma_equipada'))
    flags = novos['flags']
    flags.update(mesa=estado['itens']['faca_pega'] or estado['itens']['chave_pega'],
                 gaveta=estado['itens']['chave_pega'], pistola=estado['itens']['pistola_pega'],
                 helena=estado['conversas']['conversa_helena'], davi=estado['conversas']['conversa_davi'],
                 despensa=estado['locais']['despensa_explorada'], armario=estado['locais']['armario_explorado'],
                 ruido=estado['locais']['geladeira_explorada'], quarto=estado['locais']['quarto_explorado'],
                 gerador=estado['subsolo']['gerador_ligado'],
                 recursos_municao=estado['subsolo']['municao_pega'],
                 recursos_bandagem=estado['subsolo']['bandagem_pega'],
                 zumbi_alertado=estado['progresso']['zumbi_derrotado'])
    if estado['progresso']['zumbi_derrotado']:
        novos['vidas_inimigos']['zumbi'] = 0
    if estado['subsolo']['boss_derrotado']:
        novos['vidas_inimigos']['criatura'] = 0
    if dados['vida'] == 0:
        novos['status'] = 'derrota'
    return novos


def dados_para_partida(dados):
    try:
        if not isinstance(dados, dict):
            raise ErroSave('O save precisa ser um objeto JSON.')
        if 'versao' not in dados:
            dados = _migrar_legado(dados)
        # JSON também normaliza tuplas do estado RNG geradas durante migração.
        dados = json.loads(json.dumps(dados, allow_nan=False))
        if type(dados['versao']) is not int or dados['versao'] != VERSAO_SAVE:
            raise ErroSave('Versão de save não suportada.')
        jogador = dados['jogador']
        vida_maxima = _inteiro(jogador['vida_maxima'], 1, 10000)
        vida = _inteiro(jogador['vida'], 0, vida_maxima)
        personagem = Personagem(jogador['nome'], vida_maxima, _inventario(jogador['inventario']))
        personagem.vida = vida
        arma = jogador['arma_equipada']
        if arma is not None:
            if not isinstance(arma, str) or arma not in armas or not personagem.equipar_arma(armas[arma]):
                raise ErroSave('Arma equipada ausente do inventário ou desconhecida.')
        if dados['local'] not in LOCAIS or dados['status'] not in {'em_andamento', 'vitoria', 'derrota'}:
            raise ErroSave('Local ou situação da partida inválido.')
        flags = dados['flags']
        if not isinstance(flags, dict) or set(flags) != set(FLAGS) or any(type(v) is not bool for v in flags.values()):
            raise ErroSave('Flags de progresso inválidas.')
        vidas = dados['vidas_inimigos']
        if not isinstance(vidas, dict) or set(vidas) != set(INIMIGOS):
            raise ErroSave('Inimigos inválidos.')
        for chave, valor in vidas.items():
            _inteiro(valor, 0, INIMIGOS[chave][1])
        ativo = dados['inimigo_ativo']
        if ativo is not None and (not isinstance(ativo, str) or ativo not in INIMIGOS or vidas[ativo] == 0
                                  or dados['local'] != LOCAIS_COMBATE[ativo]):
            raise ErroSave('Combate ativo inconsistente.')
        if (vida == 0) != (dados['status'] == 'derrota') or (dados['status'] != 'em_andamento' and ativo is not None):
            raise ErroSave('Vida e situação da partida não correspondem.')
        final = dados['final']
        if dados['status'] == 'vitoria':
            if final not in {'confronto', 'manutencao'} or dados['local'] != 'garagem' or not flags['gerador']:
                raise ErroSave('Final incompatível com o progresso.')
            if final == 'confronto' and vidas['criatura'] != 0:
                raise ErroSave('A criatura não foi derrotada neste final.')
            if final == 'manutencao' and not flags['davi']:
                raise ErroSave('A rota de manutenção depende de Davi.')
        elif final is not None:
            raise ErroSave('Final definido antes do término da aventura.')
        if flags['mesa'] and any(not personagem.quantidade_item(item) for item in ('faca', 'chave de caveira')):
            raise ErroSave('Itens permanentes da mesa ausentes.')
        if flags['pistola'] and not personagem.quantidade_item('pistola'):
            raise ErroSave('Pistola coletada ausente do inventário.')
        return Partida(personagem, dados['local'], dados['status'], final, deepcopy(flags),
                       deepcopy(vidas), ativo, _estado_aleatorio(dados['rng_state']))
    except ErroSave:
        raise
    except (KeyError, TypeError, ValueError, RecursionError) as exc:
        raise ErroSave('Save inválido ou incompleto; a partida atual não foi alterada.') from exc


def salvar_jogo(partida, caminho='save.json'):
    temporario = None
    try:
        dados = criar_dados_save(partida)
        dados_para_partida(dados)  # Nunca grava um estado inválido sobre um save válido.
        destino = Path(caminho)
        destino.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=destino.parent,
                                         prefix=f'.{destino.name}.', suffix='.tmp', delete=False) as arquivo:
            temporario = Path(arquivo.name)
            json.dump(dados, arquivo, ensure_ascii=False, indent=2, allow_nan=False)
            arquivo.flush()
            os.fsync(arquivo.fileno())
        os.replace(temporario, destino)
    except (OSError, ValueError) as exc:
        raise ErroSave(f'Não foi possível salvar: {exc}') from exc
    finally:
        if temporario is not None:
            try:
                temporario.unlink(missing_ok=True)
            except OSError:
                pass  # Preserva o erro de gravação original se o disco também impedir a limpeza.


def carregar_jogo(caminho='save.json'):
    try:
        with Path(caminho).open('r', encoding='utf-8') as arquivo:
            texto = arquivo.read(MAX_SAVE_BYTES + 1)
        if len(texto.encode('utf-8')) > MAX_SAVE_BYTES:
            raise ErroSave('Save excede o tamanho permitido.')
        return dados_para_partida(json.loads(texto))
    except FileNotFoundError as exc:
        raise ErroSave('Nenhum save encontrado neste caminho.') from exc
    except (OSError, UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ErroSave('Não foi possível ler o save. O arquivo original foi preservado.') from exc
