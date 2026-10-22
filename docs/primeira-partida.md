# Primeira partida

## Começar

Instale Python 3.12, extraia o ZIP em uma pasta nova ou clone o repositório.
No VS Code, abra **a pasta que contém `TheMansion.py`** e um terminal nessa pasta:

```powershell
python --version
python TheMansion.py --version
python TheMansion.py
```

No Windows, se `python` não estiver disponível, tente `py -3.12` no lugar dele.
O jogo não requer `pip install`, Docker, conta ou chave de API.

Escolha **1 — Novo jogo**, informe seu nome e leia o objetivo no topo da tela.
Os números mudam conforme o local: use as opções que o menu mostra naquele momento.

## Primeiros minutos, sem revelar as saídas

- Converse com os aliados: eles têm informações e benefícios para a jornada.
- Examine os ambientes para encontrar ferramentas e recursos.
- Use `m` para o mapa e `o` para rever o objetivo.
- Use `i` para conferir o inventário e equipar uma arma que você possui.
- Durante um combate, trocar de arma não consome turno. Atacar ou se curar
  pode dar ao inimigo uma oportunidade de atacar.
- Leia o custo de cada escolha antes de selecionar: munição, curativos e vida
  são limitados. Bandagens restauram até 40 de vida.

## Guardar o progresso

Digite `s` para salvar. Para sair, digite `q`. **Sair não salva automaticamente**.
Para voltar, use o menu **2 — Carregar jogo** ou:

```powershell
python TheMansion.py --save save.json --load
```

Para separar suas partidas:

```powershell
python TheMansion.py --save saves/minha-partida.json
```

Se uma leitura falhar, o jogo informa o problema e preserva a partida atual e
o arquivo. Copie seu save antes de atualizar uma versão que queira guardar.

## Revisão de primeira experiência

A revisão automatizada verifica começo, entradas inválidas, controles e finais.
Ela não mede diversão ou clareza para alguém que nunca jogou. Para um teste humano,
peça à pessoa que jogue sem instruções além deste guia e registre:

| Observação | Resultado a preencher pelo observador |
| --- | --- |
| Encontrou como iniciar e entendeu o objetivo? | Não avaliado com jogador nesta entrega |
| Conseguiu explorar, equipar e usar o mapa? | Não avaliado com jogador nesta entrega |
| Entendeu o custo de atacar, curar e recuar? | Não avaliado com jogador nesta entrega |
| Salvou, saiu e carregou sem ajuda? | Não avaliado com jogador nesta entrega |
| Houve algum bloqueio, repetição confusa ou dificuldade excessiva? | Não avaliado com jogador nesta entrega |

Registre ações e mensagens observadas, sem transformar a demonstração automática
em um depoimento de jogador. A [demonstração](demo/README.md) contém spoilers.
