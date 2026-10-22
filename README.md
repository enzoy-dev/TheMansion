# TheMansion

Uma aventura curta de terror e sobrevivência no terminal, escrita em Python. Você se refugia em uma mansão com Helena e Davi e precisa encontrar uma saída, administrando vida, munição e curativos.

**Candidata a lançamento: 1.0.0-rc.1.**
[Guia de primeira partida](docs/primeira-partida.md) ·
[Vídeo de demonstração — contém spoilers](docs/demo/README.md) ·
[Histórico da versão](CHANGELOG.md)

A história continua sendo um jogo em texto: explorar, conversar e escolher como gastar recursos faz parte da sobrevivência. Há duas rotas de fuga, e suas escolhas determinam qual delas estará disponível.

## Executar

Requer Python 3.12, versão usada na validação. O jogo usa apenas a biblioteca padrão; não é necessário instalar pacotes para jogar.

```bash
git clone https://github.com/enzoy-dev/TheMansion.git
cd TheMansion
python TheMansion.py
```

O menu inicial permite criar uma partida, carregar um save ou sair. Escolha um nome ao começar uma aventura nova.

Para conferir a versão: `python TheMansion.py --version`. No Windows, também
é possível usar `py -3.12 TheMansion.py` se o comando `python` não estiver no PATH.

## Preparar a distribuição

```bash
python scripts/build_release.py
```

O ZIP e `SHA256SUMS.txt` são gerados em `dist/`, usando apenas os arquivos públicos
listados pelo empacotador. Não incluem saves pessoais, ambiente virtual ou chaves.
Extraia o ZIP em uma pasta nova e execute `python TheMansion.py` dentro dela.
O workflow **Release candidate** gera o mesmo pacote como artefato do CI em pushes,
Pull Requests e execução manual;
não cria tags nem publica GitHub Releases automaticamente.

## Controles

Os números executam as ações exibidas para o local atual. A tela mostra localização, objetivo, vida, arma, munição e bandagens.

| Comando | Ação |
| --- | --- |
| `i` | Ver inventário e equipar faca, pistola ou punhos |
| `b` | Usar uma bandagem; durante combate, permite o contra-ataque |
| `s` | Salvar a partida, inclusive durante um combate |
| `c` | Carregar o último save; uma leitura inválida mantém a partida atual |
| `m` | Consultar o mapa |
| `o` | Consultar o objetivo atual |
| `q` | Sair sem salvar automaticamente |

Durante o combate:

1. Atacar.
2. Usar bandagem.
3. Trocar de arma, sem gastar turno.
4. Recuar, perdendo 6 de vida.

Entradas inválidas, tentativas de disparar sem munição e tentativas de cura sem efeito **não gastam turno**. Uma ação válida de ataque ou cura permite o ataque do inimigo, caso ele ainda esteja vivo. Um recuo tem apenas o custo indicado de 6 de vida, sem um segundo contra-ataque.

## Regras

- A pistola consome uma munição a cada disparo, inclusive quando erra. Sem balas, troque para a faca ou para os punhos, ou recue.
- A faca e os punhos não usam munição. A faca precisa estar no inventário para ser equipada.
- Cada bandagem recupera até **40 de vida**, tanto na exploração quanto no combate. Não ultrapassa a vida máxima e não é consumida com vida cheia.
- Explorar novamente um local não duplica os recursos nem refaz um sorteio já resolvido.
- Recuar conserva a vida restante do inimigo. Voltar ao encontro não reinicia o combate.
- O dano de emboscada do corredor ocorre no máximo uma vez.
- Vitória e derrota encerram o controle da partida; não é possível continuar explorando depois do fim.
- A aventura não tem cronômetro real. A chegada do amanhecer faz parte da narrativa.

## Escolhas e personagens

Helena pode fornecer um curativo e avisar sobre uma emboscada. Davi conhece a instalação elétrica e uma alternativa para chegar à garagem. Conversar novamente não gera recursos infinitos.

Algumas escolhas têm custos explícitos: proteger a mão com uma bandagem ou perder vida ao forçar uma porta; investigar um ruído com risco de combate ou deixá-lo para trás; preservar um fusível ou consumi-lo no reparo do gerador. É possível jogar sem conversar com os aliados, mas os benefícios e as rotas disponíveis mudam.

<details>
<summary>Rotas de fuga — contém spoilers</summary>

- **Confronto:** atravesse o corredor, ligue o gerador, derrote a criatura e abra a passagem principal da garagem. Sem a orientação de Davi, um fusível da despensa permite reparar o gerador.
- **Manutenção:** converse com Davi, obtenha o fusível da despensa, repare o gerador com suas instruções e use o fusível preservado na passagem de manutenção. Essa rota dispensa o combate com a criatura.

Os dois finais levam à fuga do grupo ao amanhecer, mas registram rotas diferentes. Não são duas campanhas separadas.

</details>

## Salvamento

Por padrão, o arquivo é `save.json` no diretório de execução. Você pode escolher outro caminho:

```bash
python TheMansion.py --save saves/partida.json
python TheMansion.py --save saves/partida.json --load
```

O save atual guarda versão, nome, vida, inventário, arma, localização, progresso, inimigo ativo, vida restante dos inimigos e estado do gerador aleatório. Assim, carregar um combate não sorteia novamente a sequência seguinte de ataques.

Os dados são validados em uma nova partida antes de substituir a partida em memória. A gravação usa um arquivo temporário, `flush`, `fsync` e substituição atômica. Uma falha anterior à substituição preserva o save anterior. Não há salvamento automático ao sair, vencer, perder ou interromper o terminal: use `s` nos pontos desejados.

### Saves antigos

O formato JSON original, sem campo de versão, é convertido **somente em memória** durante a leitura. O arquivo original permanece intacto até você escolher salvar novamente. Faça uma cópia antes de atualizar um save que queira guardar:

```bash
cp save.json save-backup.json
```

O formato antigo não guardava nome, localização exata nem estado aleatório. Por isso, a conversão usa o nome `Sobrevivente`, retorna à entrada e inicia um novo gerador aleatório, preservando vida, itens, arma e os marcos de progresso registrados. Recursos parcialmente coletados no subsolo são tratados separadamente para não duplicar nem descartar a parte restante. Informações que nunca foram gravadas não podem ser recuperadas.

Arquivos incompletos, valores inválidos, itens desconhecidos ou versões não suportadas são recusados com uma mensagem, sem apagar o arquivo nem alterar a partida atual.

## Reproduzir uma partida

```bash
python TheMansion.py --seed 7
```

A mesma semente e a mesma sequência de ações reproduzem os sorteios na mesma versão de Python e do jogo. Ao carregar um save, vale o estado aleatório salvo, e não o argumento `--seed`.

## Testes

```bash
python -m venv .venv
source .venv/bin/activate
# Windows: .venv\Scripts\activate
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Os testes cobrem munição, cura, turnos inválidos, recuo, coleta única, aliados, duas rotas completas, morte, gravação interrompida, JSON inválido, conversão de saves antigos e partidas reais pela linha de comando. Todos usam arquivos temporários; não precisam ler nem modificar o seu `save.json`.

O workflow **Game tests** roda em pushes e Pull Requests e também pode ser iniciado manualmente na aba Actions. Para bloquear merges quando houver falha, configure a proteção da branch no GitHub e exija a verificação `tests`.

## Estrutura

```text
TheMansion.py       # entrada, argumentos e main(); importar não inicia o jogo
interface.py        # menus e mensagens do terminal
jogo.py             # estado, escolhas, transições e progressão
locais.py           # mapa, descrições e ações de cada local
Personagem.py       # vida, inventário, arma e uso de recursos
armas.py            # armas imutáveis e cálculo de ataques
inimigo.py          # inimigos e seus ataques
combate.py          # resolução de um turno, sem input/print
Json.py             # validação, gravação e leitura de saves
tests/              # regras, persistência e percursos pelo terminal
```

A quantidade de salas e os encontros são deliberadamente pequenos. O balanceamento é validado por cenários automatizados e sorteios reproduzíveis; uma avaliação com jogadores ainda é necessária para ajustar dificuldade, ritmo e clareza da narrativa.

## Autor

Enzo Sousa dos Santos — [enzoy-dev](https://github.com/enzoy-dev)
