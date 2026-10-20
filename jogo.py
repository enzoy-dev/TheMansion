"""Estado e regras da aventura; interface e persistência são independentes."""
from dataclasses import dataclass, field
import random

from Personagem import Personagem
from armas import faca, pistola
from combate import resolver_turno
from inimigo import Inimigo, INIMIGOS
from locais import LOCAIS, RECUOS

FLAGS = ('mesa', 'gaveta', 'armario', 'despensa', 'ruido', 'ruido_criatura', 'quarto',
         'pistola', 'recursos_municao', 'recursos_bandagem', 'helena', 'davi', 'gerador', 'zumbi_alertado')
LOCAIS_COMBATE = {'zumbi': 'corredor', 'rastejante': 'cozinha', 'criatura': 'subsolo'}


@dataclass
class Partida:
    jogador: Personagem
    local: str = 'entrada'
    status: str = 'em_andamento'
    final: str | None = None
    flags: dict = field(default_factory=lambda: dict.fromkeys(FLAGS, False))
    vidas_inimigos: dict = field(default_factory=lambda: {key: data[1] for key, data in INIMIGOS.items()})
    inimigo_ativo: str | None = None
    rng: random.Random = field(default_factory=random.Random, repr=False)

    @classmethod
    def nova(cls, nome, seed=None):
        return cls(Personagem(nome, 100), rng=random.Random(seed))

    @property
    def terminou(self):
        return self.status != 'em_andamento'

    @property
    def objetivo(self):
        if self.terminou:
            return 'A aventura terminou.'
        if self.inimigo_ativo:
            return 'Sobreviva ao encontro ou recue; o inimigo conserva a vida restante.'
        if not self.flags['mesa']:
            return 'Procure uma arma e uma chave na sala de jantar.'
        if self.vidas_inimigos['zumbi']:
            return 'Atravesse o corredor. Prepare recursos e converse com seus aliados.'
        if not self.flags['gerador']:
            return 'Ligue o gerador do subsolo: use um fusível ou peça orientação a Davi.'
        return 'Escape pela garagem: derrote a criatura ou use a manutenção com Davi e um fusível.'

    def _atualizar(self):
        if not self.jogador.esta_vivo():
            self.status = 'derrota'
            self.inimigo_ativo = None

    def _encontro(self, chave):
        self.inimigo_ativo = chave
        return [f"{INIMIGOS[chave][0]} bloqueia o caminho. Vida restante: {self.vidas_inimigos[chave]}."]

    def _mover(self, destino):
        self.local = destino
        mensagens = [f'Você chega a {LOCAIS[destino].nome}.']
        if destino == 'corredor' and self.vidas_inimigos['zumbi'] > 0:
            if not self.flags['zumbi_alertado']:
                self.flags['zumbi_alertado'] = True
                if self.flags['helena']:
                    mensagens.append('O aviso de Helena permite evitar a emboscada.')
                else:
                    self.jogador.receber_dano(8)
                    mensagens.append('A criatura salta da sombra: você perde 8 de vida na emboscada.')
            self._atualizar()
            if not self.terminou:
                mensagens += self._encontro('zumbi')
        return mensagens

    def _coletar(self, flag, itens, mensagem):
        if self.flags[flag]:
            return ['Você já examinou este lugar; não há novos recursos.']
        for nome, quantidade in itens:
            self.jogador.adicionar_item(nome, quantidade=quantidade)
        self.flags[flag] = True
        return [mensagem]

    def executar(self, acao):
        if self.terminou:
            return ['A partida já terminou.']
        if self.inimigo_ativo:
            return ['Resolva o combate ou recue antes de explorar.']
        if acao not in {codigo for _, codigo in LOCAIS[self.local].opcoes}:
            return ['Essa ação não está disponível aqui.']
        mensagens = self._executar(acao)
        self._atualizar()
        return mensagens

    def _executar(self, acao):
        if acao.startswith('mover:'):
            return self._mover(acao.split(':')[1])
        if acao == 'mesa':
            mensagens = self._coletar('mesa', [('faca', 1), ('chave de caveira', 1)],
                'Sob a toalha da mesa, você encontra uma faca e uma chave em forma de caveira.')
            if self.jogador.arma_equipada is None:
                self.jogador.equipar_arma(faca)
            return mensagens
        if acao == 'gaveta':
            if self.flags['gaveta']:
                return ['A gaveta já foi vasculhada.']
            item = 'munição' if self.rng.randint(1, 2) == 1 else 'bandagem'
            return self._coletar('gaveta', [(item, 2 if item == 'munição' else 1)],
                                 f'Uma gaveta escondida guarda {item}.')
        if acao == 'corredor':
            if not self.jogador.quantidade_item('chave de caveira'):
                return ['A porta está trancada. Procure a chave na mesa.']
            return self._mover('corredor')
        if acao == 'armario':
            return self._coletar('armario', [('bandagem', 1)], 'Você segura os pratos antes que caiam e encontra uma bandagem.')
        if acao in {'despensa_forcar', 'despensa_proteger'}:
            if self.flags['despensa']:
                return ['A despensa está vazia. Você já recolheu os recursos.']
            if acao == 'despensa_proteger':
                if not self.jogador.usar_item('bandagem'):
                    return ['Você precisa de uma bandagem para proteger a mão.']
                custo = 'A bandagem protege sua mão e é consumida.'
            else:
                self.jogador.receber_dano(8)
                if not self.jogador.esta_vivo():
                    return ['O metal corta sua mão. Você perde 8 de vida e cai antes de abrir a despensa.']
                custo = 'Você força a porta, corta a mão e perde 8 de vida.'
            return [custo] + self._coletar('despensa', [('munição', 4), ('fusível', 1)],
                'Entre as caixas, você encontra 4 munições e um fusível intacto.')
        if acao == 'ruido':
            if self.flags['ruido']:
                if self.flags['ruido_criatura'] and self.vidas_inimigos['rastejante']:
                    return self._encontro('rastejante')
                return ['Você já investigou o ruído. Não resta nada aqui.']
            self.flags['ruido'] = True
            if self.rng.randint(1, 100) <= 50:
                self.flags['ruido_criatura'] = True
                return ['Você abre a geladeira; algo se arrasta de trás dela!'] + self._encontro('rastejante')
            self.jogador.adicionar_item('bandagem')
            return ['O ruído era de uma prateleira solta. Você encontra uma bandagem atrás dela.']
        if acao == 'quarto':
            return self._coletar('quarto', [('bandagem', 1)], 'Uma bandagem está escondida entre os lençóis.')
        if acao == 'pistola':
            mensagens = self._coletar('pistola', [('pistola', 1), ('munição', 2)],
                'Na gaveta, você encontra uma pistola e 2 munições. Use o inventário para equipá-la.')
            return mensagens
        if acao == 'helena':
            if self.flags['helena']:
                return ['Helena: Fique atento ao corredor. Meu último curativo já está com você.']
            self.flags['helena'] = True
            self.jogador.adicionar_item('bandagem')
            return ['Helena entrega uma bandagem: "Há algo atrás da porta do corredor. Não deixe que te surpreenda."',
                    'Consequência: você evitará o dano inicial da emboscada.']
        if acao == 'davi':
            if self.flags['davi']:
                return ['Davi: Posso orientar o reparo do gerador sem gastar um fusível. Guarde um para a manutenção.']
            self.flags['davi'] = True
            return ['Davi desenha os cabos na poeira: "Eu te explico como ligar o gerador. Não gaste o fusível."',
                    'Ele também indica a passagem de manutenção: um fusível pode abrir a rota sem enfrentar a criatura.']
        if acao == 'recursos':
            mensagens = []
            if not self.flags['recursos_municao']:
                mensagens += self._coletar('recursos_municao', [('munição', 4)],
                                           'Atrás das caixas, você encontra 4 munições.')
            if not self.flags['recursos_bandagem']:
                mensagens += self._coletar('recursos_bandagem', [('bandagem', 1)],
                                           'Uma caixa de primeiros socorros guarda uma bandagem.')
            return mensagens or ['O subsolo já foi vasculhado. Não há novos recursos.']
        if acao == 'gerador':
            if self.flags['gerador']:
                return ['O gerador já está funcionando.']
            if self.flags['davi']:
                texto = 'Seguindo as instruções de Davi, você reconecta os cabos e preserva o fusível.'
            elif self.jogador.usar_item('fusível'):
                texto = 'Você instala o fusível. Ele é consumido no reparo do gerador.'
            else:
                return ['Falta um fusível. Procure na despensa ou converse com Davi na entrada.']
            self.flags['gerador'] = True
            return [texto, '*VRRRRRRRR* As luzes acendem. A porta da criatura recebe energia.']
        if acao == 'criatura':
            if not self.flags['gerador']:
                return ['A porta está sem energia. Ligue o gerador primeiro.']
            if not self.vidas_inimigos['criatura']:
                return ['A sala está silenciosa. A criatura já foi derrotada.']
            return ['A porta range. Uma respiração pesada vem da escuridão.'] + self._encontro('criatura')
        if acao in {'saida_principal', 'saida_alternativa'}:
            if not self.flags['gerador']:
                return ['A garagem está sem energia. Ligue o gerador.']
            if acao == 'saida_principal':
                if self.vidas_inimigos['criatura']:
                    return ['O bloqueio principal continua ativo. Derrote a criatura ou tente a manutenção.']
                self.final = 'confronto'
            else:
                if not self.flags['davi']:
                    return ['Você não sabe abrir a manutenção. Davi pode conhecer essa instalação.']
                if not self.jogador.usar_item('fusível'):
                    return ['A manutenção precisa de um fusível. Procure na despensa. A passagem principal continua possível.']
                self.final = 'manutencao'
            self.status = 'vitoria'
            return ['A passagem se abre. Helena e Davi correm até o carro com você.',
                    'O motor pega enquanto o céu clareia. A mansão fica para trás.',
                    'VOCÊS SOBREVIVERAM À NOITE.']
        raise ValueError('Ação sem implementação.')

    def turno(self, acao):
        if self.terminou or not self.inimigo_ativo:
            return ['Não há combate ativo.']
        chave = self.inimigo_ativo
        nome, _, minimo, maximo, chance = INIMIGOS[chave]
        inimigo = Inimigo(nome, self.vidas_inimigos[chave], minimo, maximo, chance)
        resultado = resolver_turno(self.jogador, inimigo, acao, self.rng)
        self.vidas_inimigos[chave] = inimigo.vida
        mensagens = list(resultado.mensagens)
        if resultado.recuou:
            self.local = RECUOS[chave]
            self.inimigo_ativo = None
        elif not inimigo.esta_vivo():
            self.inimigo_ativo = None
            if chave == 'rastejante':
                self.jogador.adicionar_item('munição', quantidade=2)
                mensagens.append('Você encontra 2 munições sob a prateleira quebrada.')
        self._atualizar()
        return mensagens
