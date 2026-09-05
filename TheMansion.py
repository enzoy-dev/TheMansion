

import random   

from Personagem import Personagem
from inimigo import Inimigo
from armas import faca
from combate import combate
from utilidades import pedir_escolha
from Json import salvar_jogo, carregar_jogo
from armas import faca, pistola



# =========================
# CONVERSAR COM O GRUPO
# =========================


def conversar_grupo(estado: dict[str, dict[str, bool]]) -> None:
    conversando = True


    while conversando:
        print("\nVocê se reúne com o grupo na entrada da mansão.")


        if not estado["conversas"].get("conversa_helena", False):
            print("\n1 - Conversar com Helena")


        if not estado["conversas"].get("conversa_davi", False):
            print("2 - Conversar com Davi")


        print("3 - Voltar")


        conversa = pedir_escolha("Escolha com quem falar: ")


        if conversa == 1 and not estado["conversas"].get("conversa_helena", False):
            print("\nHelena: Essa mansão é maior do que parece.")
            print("Helena: Acho que deveríamos explorar separadamente. Se ficarmos todos juntos, vamos perder muito tempo.")
            estado["conversas"]["conversa_helena"] = True


        elif conversa == 2 and not estado["conversas"].get("conversa_davi", False):
            print("\nDavi: Eu não gosto dessa ideia, mas não temos muitas opções.")
            print("Davi: Vamos dividir os caminhos e procurar qualquer coisa que possa nos ajudar.")
            print("Davi: Se encontrarmos algo estranho, voltamos imediatamente.")
            estado["conversas"]["conversa_davi"] = True


        elif conversa == 3:
            print("\nVocê volta a investigar a mansão.")
            conversando = False

# =========================
# EXPLORAR SALA DE JANTAR
# =========================

def explorar_sala_jantar(jogador: Personagem, estado: dict) -> None:
    if not estado["itens"]["faca_pega"]:
        print("\nVocê vira à esquerda e se depara com uma sala de jantar chique.")
        print("Há uma porta no fundo da sala.")
        print("Você encontra uma faca sobre a mesa e a guarda com você.")

        jogador.adicionar_item("faca", "arma")
        jogador.equipar_arma(faca)

        estado["itens"]["faca_pega"] = True

    else:
        print("\nA mesa está vazia. Você já pegou a faca.")

    if not estado["itens"]["chave_pega"]:
        print("\nVocê explora a sala de jantar.")
        print("Você encontra uma chave em formato de caveira em cima da mesa principal.")

        jogador.adicionar_item("chave de caveira", "chave")

        item = random.randint(1, 3)

        if item == 1:
            jogador.adicionar_item("munição", "munição", 3)
            print("Você também encontrou 3 munições.")

        elif item == 2:
            jogador.adicionar_item("bandagem", "cura")
            print("Você também encontrou uma bandagem.")

        else:
            print("Você não encontrou mais nada.")

        estado["itens"]["chave_pega"] = True
        estado["itens"]["mesa_explorada"] = True

    else:
        print("\nVocê já explorou a sala de jantar.")

# EXPLORAR COZINHA

def explorar_cozinha(jogador: Personagem) -> None:
    while True:
        print("\nNo fundo da cozinha, você percebe três coisas:")
        print("1 - Uma porta de madeira")
        print("2 - Um armário antigo")
        print("3 - Uma geladeira aparentemente desligada")
        print("4 - Voltar")

        escolha = pedir_escolha("\nO que você deseja investigar? ")

        if escolha == 1:
         
         if not estado["locais"]["despensa_explorada"]:

            print("\nVocê se aproxima da porta.")
            print("A maçaneta está coberta por uma substância escura.")
            print("Você segura a respiração e abre a porta.")

            print("\nAtrás dela existe uma pequena despensa.")
            print("Há várias caixas empilhadas e uma prateleira caída.")

            print("\nVocê encontra uma pequena caixa de munição.")
            jogador.adicionar_item("munição", "munição", 3)

            print("\nVocê fecha a porta da despensa.")

        elif escolha == 2:
          
          if not estado["locais"]["armario_explorado"]:

            print("\nVocê abre o armário.")
            print("Alguns pratos caem no chão e fazem um barulho enorme.")

            print("\nVocê espera alguns segundos.")
            print("Nada acontece.")

            print("Dentro do armário, você encontra uma bandagem.")
            jogador.adicionar_item("bandagem", "cura")

        elif escolha == 3:
         
         if not estado["locais"]["geladeira_explorada"]:

            print("\nVocê se aproxima da geladeira.")
            print("Ela está coberta de ferrugem.")

            print("Quando você abre a porta...")
            print("um líquido escuro escorre pelo chão.")

            print("\nVocê fecha a geladeira imediatamente.")
            print("Definitivamente não quer descobrir o que havia ali.")

        elif escolha == 4:
            print("\nVocê deixa a cozinha.")
            break

        else:
            print("\nVocê precisa escolher uma das opções.")

# EXPLORAR CORREDOR

def explorar_corredor(jogador: Personagem) -> None:
    print("\nVocê abre a porta e se depara com um corredor escuro.")
    print("Você sente um cheiro estranho vindo do final do corredor.")

    print("\nVocê decide seguir em frente, mas de repente uma criatura aparece e te ataca!")
    print("Você consegue se defender com a faca, mas acaba se machucando no processo.")

    jogador.receber_dano(20)

    zumbi = Inimigo("Zumbi", vida=30)
    venceu = combate(jogador, zumbi)

    if not venceu:
        return

    print("\nVocê derrotou a criatura.")
    print("O corpo cai no chão e o corredor fica em silêncio novamente.")

    print("\nÀ sua frente existem duas portas antigas à esquerda.")
    print("Também existe um corredor que continua à frente.")

    print("\nO que você deseja fazer?")
    print("1 - Continuar")
    print("2 - Usar bandagem")

    escolha = pedir_escolha("> ")

    if escolha == 2:
        if jogador.quantidade_item("bandagem") > 0:
            jogador.usar_item("bandagem")
            jogador.curar(20)
        else:
            print("\nVocê não possui nenhuma bandagem.")

    while True:
        print("\nO que você deseja fazer agora?")
        print("1 - Abrir a primeira porta")
        print("2 - Abrir a segunda porta")
        print("3 - Continuar pelo corredor")
        print("4 - Voltar")

        escolha_porta = pedir_escolha("Digite o número da sua escolha: ")

        if escolha_porta == 1:
            print("\nVocê empurra a porta lentamente...")
            print("As dobradiças rangem, ecoando pelo corredor.")
            print("O quarto parece abandonado há décadas.")

            print("\nEm cima da cama, algo chama sua atenção.")
            print("Uma bandagem antiga está escondida entre os lençóis.")

            jogador.adicionar_item("bandagem", "cura")

        elif escolha_porta == 2:
          if not estado["itens"].get("pistola_pega", False):
            print("\nVocê segura a maçaneta e força a porta.")
            print("A madeira começa a quebrar...")
            print("Você entra em um pequeno escritório cheio de livros.")

            print("\nNas gavetas da escrivaninha, você encontra algo útil.")
            print("\nDentro da gaveta existe uma pistola antiga.")

            jogador.adicionar_item("pistola", "arma", pistola)
            jogador.equipar_arma(pistola)

            estado["itens"]["pistola_pega"] = True
          else:
            print("\nVocê já explorou este quarto.")

        elif escolha_porta == 3:
            explorar_final_corredor(jogador)

        elif escolha_porta == 4:
            print("\nVocê decide voltar.")
            break

        else:
            print("\nEscolha inválida.")

#FINAL DO CORREDOR

def explorar_final_corredor(jogador: Personagem) -> None:
    print("\nO corpo da criatura permanece imóvel no chão.")
    print("Você segue em frente por alguns metros.")

    print("O corredor termina em uma parede de concreto desgastada.")
    print("À esquerda, o corredor continua por um pequeno trecho.")
    print("Há uma porta à direita e, no final, uma escada.")

    while True:
        print("\nO que você deseja fazer agora?")
        print("1 - Tentar abrir a porta à direita")
        print("2 - Descer a escada")
        print("3 - Voltar")

        escolha = pedir_escolha("Digite o número da sua escolha: ")

        if escolha == 1:
            print("\nVocê se aproxima da porta e tenta girar a maçaneta.")
            print("A porta range, mas não abre.")
            print("Parece estar trancada.")

            if jogador.quantidade_item("chave de caveira") > 0:
                print("\nVocê lembra da chave de caveira que encontrou na sala de jantar.")
                print("Você a utiliza para destrancar a porta.")

                print("A porta se abre lentamente.")
                print("Uma cozinha suja e abandonada aparece diante de você.")

                print("\nVocê entra na cozinha lentamente.")
                print("O cheiro de podridão é ainda mais forte aqui.")
                print("Há pratos quebrados espalhados pelo chão.")
                print("Manchas escuras cobrem as paredes.")

                explorar_cozinha(jogador)

                break

            else:
                print("\nVocê não possui a chave necessária para abrir esta porta.")

        elif escolha == 2:
            print("\nVocê decide descer a escada.")
            print("A escuridão toma conta do caminho.")

            break

        elif escolha == 3:
            break

        else:
            print("\nVocê hesita... mas precisa escolher uma opção.")

# EXPLORAR MANSÃO

def explorar_mansao(jogador: Personagem, estado: dict) -> None:
    dentro_da_sala = True

    while dentro_da_sala:
        jogador.mostrar_status()
        print("\nO que você deseja fazer agora?")

        if not estado["itens"].get("chave_pega", False):
            print("1 - Explorar a sala de jantar")
            print("2 - Abrir a porta no fundo")
            print("3 - Voltar")
        else:
            print("1- continuar pelo corredor")
            print("2 - voltar")

        escolha = pedir_escolha("Digite o número da sua escolha: ")

        if not estado["itens"].get("chave_pega", False):

          if escolha == 1:
           explorar_sala_jantar(jogador, estado)

          elif escolha == 2:
           explorar_corredor(jogador)

          elif escolha == 3:
           dentro_da_sala = False

          else:
           print("\nEscolha inválida.")

        else:

         if escolha == 1:
          explorar_corredor(jogador)

         elif escolha == 2:
          dentro_da_sala = False

         else:
          print("\nEscolha inválida.")


# =========================
# INTRODUÇÃO
# =========================

print('=== JOGO DE SOBREVIVENCIA ===')
nome = input("\nQual é o seu nome? ")
print(f'\n{nome}, você estava fugindo de criaturas na floresta, e se refugiou em uma mansão abandonada com seu grupo')
jogador = Personagem(nome, vida=100)

estado = {
    "itens": {
        "faca_pega": False,
        "chave_pega": False,
        "mesa_explorada": False
    },

    "conversas": {
        "conversa_helena": False,
        "conversa_davi": False
    },
    "locais": {
      "despensa_explorada": False,
      "armario_explorado": False,
      "geladeira_explorada": False
}
}


jogando = True

# =========================
# MENU PRINCIPAL
# =========================

while jogando:
    jogador.mostrar_status()

    print("\nO que você deseja fazer?")
    print("1 - Explorar a mansão")
    print("2 - Conversar com o grupo")
    print("3 - Salvar o jogo")
    print("4 - Carregar o jogo")
    print("5 - Sair do jogo")

    escolha = pedir_escolha("Digite o número da sua escolha: ")

    if escolha == 1:
        explorar_mansao(jogador, estado)

    elif escolha == 2:
        conversar_grupo(estado)

    elif escolha == 3:
     salvar_jogo(jogador, estado)

    elif escolha == 4:
     carregar_jogo(jogador, estado)

    elif escolha == 5:
     print("\nVocê decide parar por aqui. Até a próxima!")
     jogando = False

    else:
        print(
            "\nVocê ficou parado. "
            "Seu grupo foi explorar e agora você está sozinho."
        )
        print("O silêncio te incomoda.")

    if not jogador.esta_vivo():
        print("\nVocê não resistiu... FIM DE JOGO")
        jogando = False