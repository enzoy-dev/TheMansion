"""Regras de um turno, sem input/print; ações inválidas não gastam turno."""
from dataclasses import dataclass


@dataclass(frozen=True)
class ResultadoTurno:
    mensagens: tuple[str, ...]
    gastou_turno: bool
    recuou: bool = False


def resolver_turno(jogador, inimigo, acao, rng):
    if not jogador.esta_vivo() or not inimigo.esta_vivo():
        return ResultadoTurno(('Este combate já terminou.',), False)
    if acao == 'recuar':
        dano = jogador.receber_dano(6)
        return ResultadoTurno((f'Você recua pela passagem e perde {dano} de vida.',), True, True)
    if acao == 'atacar':
        ataque = jogador.atacar(inimigo, rng)
        if not ataque.executado:
            return ResultadoTurno(('Sem munição. Troque para a faca ou recue; nenhuma ação foi gasta.',), False)
        mensagem = f'Ataque com {ataque.arma}: {ataque.dano} de dano.' if ataque.dano else f'Você errou o ataque com {ataque.arma}.'
    elif acao == 'curar':
        cura = jogador.usar_bandagem()
        if not cura:
            return ResultadoTurno(('Não foi possível curar: vida cheia ou nenhuma bandagem. Nenhum turno gasto.',), False)
        mensagem = f'Você recuperou {cura} de vida com a bandagem.'
    else:
        return ResultadoTurno(('Opção inválida. Nenhum turno foi gasto.',), False)
    mensagens = [mensagem]
    if inimigo.esta_vivo():
        dano = inimigo.atacar(jogador, rng)
        mensagens.append(f'{inimigo.nome} causou {dano} de dano.' if dano else f'{inimigo.nome} errou o ataque.')
    else:
        mensagens.append(f'{inimigo.nome} foi derrotado.')
    return ResultadoTurno(tuple(mensagens), True)
