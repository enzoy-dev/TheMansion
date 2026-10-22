# Demonstração do jogo

[Assistir / baixar o vídeo MP4](themansion.mp4) · [Ler o percurso completo](playthrough.txt)

O vídeo mostra uma partida real da interface de terminal com entradas automatizadas,
semente 7, inventário, salvar/carregar, combate e a fuga pela manutenção.
**Contém spoilers e não tem áudio.** Não é um teste com jogador nem uma gravação
de velocidade humana: o ritmo foi ajustado para apresentar as telas.

O texto exibido vem de `interface.rodar`; as regras não são simuladas pelo renderizador.
O save demonstrativo é criado em um diretório temporário, removido ao terminar.
Nenhum `save.json` pessoal é lido ou alterado.

O arquivo [playthrough.cast](playthrough.cast) usa o formato asciicast v2 para
reprodução em ferramentas compatíveis. Para gerar novamente somente texto e cast:

```bash
python scripts/record_demo.py
```

Para recriar o MP4, são necessários FFmpeg no PATH e as dependências opcionais:

```bash
python -m pip install -r requirements-demo.txt
python -m playwright install chromium
python scripts/render_demo.py
```

Essas ferramentas não são necessárias para jogar. A gravação revela uma rota
vencedora; confira o [guia de primeira partida](../primeira-partida.md) se preferir
descobrir a mansão sem essa ajuda.
