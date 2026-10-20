"""Mapa e textos: as transições e consequências ficam em jogo.py."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Local:
    nome: str
    descricao: str
    opcoes: tuple[tuple[str, str], ...]


LOCAIS = {
    'entrada': Local('Entrada da mansão',
        'A chuva apaga os rastros na floresta. Helena e Davi esperam junto à porta.\n'
        'Precisamos encontrar uma saída antes do amanhecer.',
        (('Sala de jantar', 'mover:jantar'), ('Cozinha', 'mover:cozinha'),
         ('Conversar com Helena', 'helena'), ('Conversar com Davi', 'davi'))),
    'jantar': Local('Sala de jantar',
        'A mesa está posta para pessoas que nunca voltaram. Uma porta com fechadura de caveira leva ao corredor.',
        (('Examinar a mesa', 'mesa'), ('Vasculhar a gaveta', 'gaveta'),
         ('Abrir a porta do corredor', 'corredor'), ('Voltar à entrada', 'mover:entrada'))),
    'cozinha': Local('Cozinha',
        'O armário pende sobre pratos quebrados. A despensa emperrou. Um ruído vem da geladeira.',
        (('Abrir o armário', 'armario'), ('Forçar a despensa (perde 8 de vida)', 'despensa_forcar'),
         ('Proteger a mão com uma bandagem e abrir a despensa', 'despensa_proteger'),
         ('Investigar o ruído (risco de combate)', 'ruido'), ('Voltar à entrada', 'mover:entrada'))),
    'corredor': Local('Corredor',
        'O cheiro de podridão vem das escadas. Um quarto e um escritório ficam nas laterais.',
        (('Entrar no quarto', 'mover:quarto'), ('Entrar no escritório', 'mover:escritorio'),
         ('Descer ao subsolo', 'mover:subsolo'), ('Voltar à sala de jantar', 'mover:jantar'))),
    'quarto': Local('Quarto abandonado',
        'A cama foi arrastada contra a parede. Há marcas de unhas junto à janela vedada.',
        (('Examinar os lençóis', 'quarto'), ('Voltar ao corredor', 'mover:corredor'))),
    'escritorio': Local('Escritório',
        'Livros úmidos cobrem o chão. Uma gaveta de metal parece intacta.',
        (('Abrir a gaveta de metal', 'pistola'), ('Voltar ao corredor', 'mover:corredor'))),
    'subsolo': Local('Subsolo',
        'Um gerador antigo alimenta duas portas de aço. Atrás da esquerda, algo respira.\n'
        'A porta da garagem possui uma passagem de manutenção estreita.',
        (('Procurar recursos', 'recursos'), ('Reparar o gerador', 'gerador'),
         ('Enfrentar a criatura', 'criatura'), ('Examinar a porta da garagem', 'mover:garagem'),
         ('Voltar ao corredor', 'mover:corredor'))),
    'garagem': Local('Acesso à garagem',
        'Um carro antigo espera do outro lado. O bloqueio principal responde à sala da criatura.',
        (('Abrir a passagem principal', 'saida_principal'),
         ('Usar a passagem de manutenção (ajuda de Davi e um fusível)', 'saida_alternativa'),
         ('Voltar ao subsolo', 'mover:subsolo'))),
}

RECUOS = {'zumbi': 'jantar', 'rastejante': 'entrada', 'criatura': 'corredor'}


def descrever(local, flags, vidas_inimigos):
    texto = LOCAIS[local].descricao
    if local == 'jantar' and flags['mesa']:
        texto += '\nA mesa já foi vasculhada; a chave e a faca foram recolhidas.'
    if local == 'cozinha':
        if flags['despensa']:
            texto = texto.replace('A despensa emperrou.', 'A despensa está aberta e vazia.')
        if flags['armario']:
            texto += '\nO armário já foi examinado.'
    if local == 'corredor' and vidas_inimigos['zumbi'] == 0:
        texto += '\nO corpo do zumbi continua imóvel junto à parede.'
    if local == 'quarto' and flags['quarto']:
        texto += '\nVocê já examinou os lençóis.'
    if local == 'escritorio' and flags['pistola']:
        texto += '\nA gaveta de metal agora está vazia.'
    if local == 'subsolo' and flags['gerador']:
        texto += '\nO gerador está funcionando. Não precisa de outro reparo.'
    if local in {'subsolo', 'garagem'} and vidas_inimigos['criatura'] == 0:
        texto += '\nA criatura foi derrotada e o bloqueio principal da garagem foi liberado.'
    return texto
