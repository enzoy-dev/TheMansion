import json
from armas import armas


def criar_dados_save(jogador, estado):
    return {
        "vida": jogador.vida,
        "inventario": jogador.inventario,
        "arma_equipada": jogador.arma_equipada.nome if jogador.arma_equipada else None,
        "estado": estado
    }


def salvar_jogo(jogador, estado):
    dados = criar_dados_save(jogador, estado)

    with open("save.json", "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, indent=4)

    print("\nJogo salvo com sucesso!")


def carregar_jogo(jogador, estado):
    try:
        with open("save.json", "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)

        jogador.vida = dados["vida"]
        jogador.inventario = dados["inventario"]
        estado.update(dados["estado"])

        # Restaura a arma equipada
        nome_arma = dados.get("arma_equipada")
        if nome_arma and nome_arma in armas:
            jogador.arma_equipada = armas[nome_arma]
        else:
            jogador.arma_equipada = None

        print("\nJogo carregado com sucesso!")

    except FileNotFoundError:
        print("\nNenhum save encontrado.")

    except json.JSONDecodeError:
        print("\nO arquivo de save está corrompido.")