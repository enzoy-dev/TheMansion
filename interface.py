"""Interface de terminal; nenhuma regra de combate ou gravação é duplicada aqui."""
from armas import armas
from inimigo import INIMIGOS
from Json import carregar_jogo, salvar_jogo, ErroSave
from jogo import Partida
from locais import LOCAIS, descrever
from utilidades import ler_texto, pedir_escolha, EntradaEncerrada

MAPA = '''
Entrada -- Sala de jantar -- Corredor -- Subsolo -- Garagem
   |                           |   |
Cozinha                      Quarto Escritório
'''


def inventario(partida, entrada, saida):
    jogador = partida.jogador
    saida('\nInventário:')
    for item in jogador.inventario:
        saida(f"- {item['nome']} x{item['quantidade']}")
    if not jogador.inventario:
        saida('(vazio)')
    saida('Equipar: 1 - faca | 2 - pistola | 3 - punhos | 0 - voltar. Trocar não gasta turno.')
    escolha = pedir_escolha('Escolha: ', {0, 1, 2, 3}, entrada, saida)
    if escolha == 0:
        return
    if escolha == 3:
        jogador.arma_equipada = None
        saida('Você está usando os punhos.')
        return
    arma = armas['faca' if escolha == 1 else 'pistola']
    saida(f'Você equipou a {arma.nome}.' if jogador.equipar_arma(arma) else 'Você ainda não possui essa arma.')


def iniciar(entrada, saida, caminho, seed=None):
    while True:
        saida('\n=== THE MANSION ===\n1 - Novo jogo\n2 - Carregar jogo\n3 - Sair')
        escolha = pedir_escolha('Escolha: ', {1, 2, 3}, entrada, saida)
        if escolha == 3:
            return None
        if escolha == 2:
            try:
                partida = carregar_jogo(caminho)
                saida(f'Progresso de {partida.jogador.nome} carregado.')
                return partida
            except ErroSave as exc:
                saida(str(exc))
                continue
        while True:
            nome = ler_texto('Qual é o seu nome? ', entrada)
            try:
                partida = Partida.nova(nome, seed)
                break
            except ValueError as exc:
                saida(str(exc))
        saida(f'\n{nome}, você e seus amigos escaparam de criaturas na floresta. A mansão foi o único abrigo.')
        saida('A chuva aperta. Encontrem uma saída e sobrevivam até o amanhecer.')
        return partida


def executar(partida, caminho='save.json', entrada=input, saida=print):
    while not partida.terminou:
        jogador = partida.jogador
        equipada = jogador.arma_equipada.nome if jogador.arma_equipada else 'punhos'
        saida(f'\n[{LOCAIS[partida.local].nome}] Vida: {jogador.vida}/{jogador.vida_maxima} | '
              f'Arma: {equipada} | Munição: {jogador.quantidade_item("munição")} | '
              f'Bandagens: {jogador.quantidade_item("bandagem")}')
        saida(f'Objetivo: {partida.objetivo}')
        if partida.inimigo_ativo:
            chave = partida.inimigo_ativo
            saida(f'Combate: {INIMIGOS[chave][0]} | Vida: {partida.vidas_inimigos[chave]}')
            saida('1 - Atacar\n2 - Usar bandagem\n3 - Trocar arma (sem gastar turno)\n4 - Recuar (perde 6 de vida)')
        else:
            local = LOCAIS[partida.local]
            saida(descrever(partida.local, partida.flags, partida.vidas_inimigos))
            for numero, (texto, _) in enumerate(local.opcoes, 1):
                saida(f'{numero} - {texto}')
        saida('i: inventário | b: bandagem | s: salvar | c: carregar | m: mapa | o: objetivo | q: sair sem salvar')
        comando = ler_texto('Sua ação: ', entrada).lower()
        mensagens = []
        if comando == 'q':
            saida('Você interrompeu a aventura. O progresso não é salvo automaticamente; use s antes de sair.')
            return partida
        if comando == 's':
            try:
                salvar_jogo(partida, caminho)
                mensagens = [f'Jogo salvo em {caminho}.']
            except ErroSave as exc:
                mensagens = [str(exc)]
        elif comando == 'c':
            try:
                nova = carregar_jogo(caminho)
            except ErroSave as exc:
                mensagens = [str(exc)]
            else:
                partida = nova
                mensagens = [f'Progresso de {partida.jogador.nome} carregado.']
        elif comando == 'm':
            mensagens = [MAPA]
        elif comando == 'o':
            mensagens = [partida.objetivo]
        elif comando == 'i' or (comando == '3' and partida.inimigo_ativo):
            inventario(partida, entrada, saida)
        elif comando == 'b':
            if partida.inimigo_ativo:
                mensagens = partida.turno('curar')
            else:
                cura = partida.jogador.usar_bandagem()
                mensagens = [f'Você recuperou {cura} de vida.' if cura else 'Vida cheia ou nenhuma bandagem disponível.']
        elif partida.inimigo_ativo:
            mensagens = partida.turno({'1': 'atacar', '2': 'curar', '4': 'recuar'}.get(comando, 'invalida'))
        else:
            opcoes = LOCAIS[partida.local].opcoes
            if comando.isdecimal() and 1 <= int(comando) <= len(opcoes):
                mensagens = partida.executar(opcoes[int(comando) - 1][1])
            else:
                mensagens = ['Escolha uma opção exibida. Nenhuma ação foi gasta.']
        for mensagem in mensagens:
            saida(mensagem)
    saida('\n=== VITÓRIA ===' if partida.status == 'vitoria' else '\nVocê não resistiu... FIM DE JOGO.')
    return partida


def rodar(caminho='save.json', seed=None, carregar=False, entrada=input, saida=print):
    try:
        if carregar:
            try:
                partida = carregar_jogo(caminho)
                saida(f'Progresso de {partida.jogador.nome} carregado.')
            except ErroSave as exc:
                saida(str(exc))
                return 1
        else:
            partida = iniciar(entrada, saida, caminho, seed)
        if partida is not None:
            executar(partida, caminho, entrada, saida)
        return 0
    except EntradaEncerrada:
        saida('\nEntrada encerrada. O último save foi preservado; alterações não salvas foram descartadas.')
        return 0
