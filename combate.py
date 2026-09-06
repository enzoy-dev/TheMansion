from utilidades import pedir_escolha


def combate(jogador, inimigo):
    while jogador.esta_vivo() and inimigo.esta_vivo():
        print("\nO que você deseja fazer agora?")

        if jogador.arma_equipada:
            print(f"1 - Atacar com {jogador.arma_equipada.nome}")
        else:
            print("1 - Atacar (sem arma equipada)")

        print("2 - Usar bandagem")

        escolha = pedir_escolha("Digite o número da sua escolha: ")

        if escolha == 1:
            jogador.atacar(inimigo)
        elif escolha == 2:
            if jogador.usar_item("bandagem"):
                jogador.curar(40)
            else:
                print("\nVocê não tem bandagens suficientes.")
        else:
            print("\nOpção inválida.")

        if inimigo.esta_vivo():
            inimigo.atacar(jogador)

    return not inimigo.esta_vivo()