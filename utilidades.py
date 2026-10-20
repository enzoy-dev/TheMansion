class EntradaEncerrada(Exception):
    """EOF ou interrupção do jogador, tratados pelo controlador do terminal."""


def ler_texto(mensagem, entrada=None):
    try:
        return (entrada or input)(mensagem).strip()
    except (EOFError, KeyboardInterrupt) as exc:
        raise EntradaEncerrada from exc


def pedir_escolha(mensagem, opcoes=None, entrada=None, saida=print):
    while True:
        texto = ler_texto(mensagem, entrada)
        try:
            valor = int(texto)
        except ValueError:
            saida('Escolha inválida. Digite um dos números exibidos.')
            continue
        if opcoes is None or valor in opcoes:
            return valor
        saida('Escolha inválida. Digite um dos números exibidos.')
