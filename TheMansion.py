

import random   

from Personagem import Personagem
from inimigo import Inimigo
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

def explorar_cozinha(jogador: Personagem, estado: dict) -> None:
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
            estado["locais"]["despensa_explorada"] = True

        elif escolha == 2:
          
          if not estado["locais"]["armario_explorado"]:

            print("\nVocê abre o armário.")
            print("Alguns pratos caem no chão e fazem um barulho enorme.")

            print("\nVocê espera alguns segundos.")
            print("Nada acontece.")

            print("Dentro do armário, você encontra uma bandagem.")
            jogador.adicionar_item("bandagem", "cura")
            estado["locais"]["armario_explorado"] = True

        elif escolha == 3:
         
         if not estado["locais"]["geladeira_explorada"]:

            print("\nVocê se aproxima da geladeira.")
            print("Ela está coberta de ferrugem.")

            print("Quando você abre a porta...")
            print("um líquido escuro escorre pelo chão.")

            print("\nVocê fecha a geladeira imediatamente.")
            print("Definitivamente não quer descobrir o que havia ali.")
            estado["locais"]["geladeira_explorada"] = True

        elif escolha == 4:
            print("\nVocê deixa a cozinha.")
            break

        else:
            print("\nVocê precisa escolher uma das opções.")

# EXPLORAR CORREDOR

def explorar_corredor(jogador: Personagem, estado: dict) -> None:
    print("\nVocê abre a porta e se depara com um corredor escuro.")
    print("Você sente um cheiro estranho vindo do final do corredor.")

    print("\nVocê decide seguir em frente, mas de repente uma criatura aparece e te ataca!")
    print("Você consegue se defender com a faca, mas acaba se machucando no processo.")

    jogador.receber_dano(20)

    zumbi = Inimigo("Zumbi", vida=30)
    venceu = combate(jogador, zumbi)

    if not venceu:
        return
    estado["progresso"]["zumbi_derrotado"] = True

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

            jogador.adicionar_item("pistola", "arma")
            jogador.equipar_arma(pistola)

            estado["itens"]["pistola_pega"] = True
          else:
            print("\nVocê já explorou este quarto.")

        elif escolha_porta == 3:
            explorar_final_corredor(jogador, estado)

        elif escolha_porta == 4:
            print("\nVocê decide voltar.")
            break

        else:
            print("\nEscolha inválida.")

#FINAL DO CORREDOR

def explorar_final_corredor(jogador: Personagem, estado: dict) -> None:
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

                explorar_cozinha(jogador, estado)

                break

            else:
                print("\nVocê não possui a chave necessária para abrir esta porta.")

        elif escolha == 2:
            print("\nVocê decide descer a escada.")
            print("A escuridão toma conta do caminho.")

            explorar_subsolo(jogador, estado)
            
            break

        elif escolha == 3:
            break

        else:
            print("\nVocê hesita... mas precisa escolher uma opção.")

def explorar_subsolo(jogador: Personagem, estado: dict) -> None:
    print("\nVocê desce a escada com cuidado.")
    print("O ambiente é úmido e frio.")
    print("O cheiro de mofo é intenso.")

    print("\nNo subsolo, você encontra uma área grande e mal iluminada.")
    print("Há um gerador antigo no centro do local.")

    explorando = True

    while explorando:

        print("\nO que você deseja fazer?")
        print("1 - Procurar por recursos")
        print("2 - Examinar o gerador")
        print("3 - Ver as portas metálicas")
        print("4 - Voltar")

        escolha = pedir_escolha("Digite sua escolha: ")

        if escolha == 1:
            explorar_recursos_subsolo(jogador, estado)

        elif escolha == 2:
            ativar_gerador(jogador, estado)

        elif escolha == 3:
            portas_subsolo(jogador, estado)

        elif escolha == 4:
            explorando = False

        else:
            print("\nEscolha inválida.")


def explorar_recursos_subsolo(
    jogador: Personagem,
    estado: dict
) -> None:

    print("\nVocê começa a procurar alguma coisa útil.")

    if not estado["subsolo"]["municao_pega"]:
        print("\nAtrás de algumas caixas, você encontra munição.")

        jogador.adicionar_item("munição", "munição", 4)

        estado["subsolo"]["municao_pega"] = True

    elif not estado["subsolo"]["bandagem_pega"]:
        print("\nVocê encontra uma pequena caixa de primeiros socorros.")

        jogador.adicionar_item("bandagem", "cura")

        estado["subsolo"]["bandagem_pega"] = True

    else:
        print("\nVocê já vasculhou praticamente tudo.")


def ativar_gerador(
    jogador: Personagem,
    estado: dict
) -> None:

    if estado["subsolo"]["gerador_ligado"]:
        print("\nO gerador continua funcionando.")
        return

    print("\nVocê se aproxima do gerador.")

    print("Ele parece antigo, mas ainda pode funcionar.")

    print("\nVocê verifica os cabos.")

    print("Alguns estão soltos.")

    print("\nDepois de alguns minutos, você consegue conectá-los.")

    print("\nVocê puxa a alavanca.")

    print("\n*VRRRRRRRRRRRRRR*")

    print("\nO gerador começa a funcionar.")

    print("\nAs luzes do subsolo se acendem.")

    print("\nVocê escuta dois barulhos metálicos.")

    print("*CLANG*")

    print("*CLANG*")

    print("\nAs duas portas metálicas foram destrancadas.")

    estado["subsolo"]["gerador_ligado"] = True

def portas_subsolo(
    jogador: Personagem,
    estado: dict
) -> None:

    if not estado["subsolo"]["gerador_ligado"]:

        print("\nVocê se aproxima das duas portas metálicas.")

        print("Nenhuma delas possui maçaneta.")

        print("Ambas parecem depender de energia.")

        return

    print("\nVocê está diante das duas portas metálicas.")

    print("1 - Porta da esquerda")
    print("2 - Porta da direita")
    print("3 - Voltar")

    escolha = pedir_escolha("Digite sua escolha: ")

    if escolha == 1:
        sala_boss(jogador, estado)

    elif escolha == 2:
        garagem(jogador, estado)

    elif escolha == 3:
        return

    else:
        print("\nEscolha inválida.")

def sala_boss(
    jogador: Personagem,
    estado: dict
) -> None:

    if estado["subsolo"]["boss_derrotado"]:

        print("\nA sala está silenciosa.")

        print("O corpo da criatura permanece no chão.")

        return

    print("\nVocê abre a porta metálica.")

    print("O som ecoa por todo o subsolo.")

    print("\nA sala está completamente escura.")

    print("Você entra lentamente.")

    print("\nA porta se fecha atrás de você.")

    print("*CLANG*")

    print("\nVocê escuta uma respiração.")

    print("Lenta.")

    print("Pesada.")

    print("\nVocê aponta sua arma para o fundo da sala.")

    print("\nAlgo se move.")

    print("\n==============================")
    print("          BOSS")
    print("==============================")

    boss = Inimigo(
        "A Criatura",
        vida=100,
        dano_min=15,
        dano_max=25,
        chance_acerto=65
    )

    venceu = combate(jogador, boss)

    if not venceu:
        return

    estado["subsolo"]["boss_derrotado"] = True

    print("\nA criatura finalmente cai.")

    print("\nO silêncio toma conta da sala.")

    print("\nDepois de alguns segundos...")

    print("*CLANG*")

    print("\nVocê escuta a outra porta sendo liberada.")

    estado["subsolo"]["boss_derrotado"] = True

    print("\nA criatura finalmente cai.")

    print("\nO silêncio toma conta da sala.")

    print("\nDepois de alguns segundos...")

    print("*CLANG*")

print("\nVocê escuta a outra porta sendo liberada.")

def garagem(
    jogador: Personagem,
    estado: dict
) -> None:

    if not estado["subsolo"]["boss_derrotado"]:

        print("\nA porta continua bloqueada.")

        print("Você sente que ainda precisa resolver alguma coisa.")

        return

    print("\nVocê abre a porta metálica.")

    print("\nDessa vez ela se abre completamente.")

    print("Do outro lado existe um estacionamento subterrâneo.")

    print("\nHá alguns carros antigos estacionados.")

    print("Um deles parece estar em condições de funcionar.")

    print("\nVocê encontrou uma saída.")

    final_jogo(jogador, estado)

def final_jogo(
    jogador: Personagem,
    estado: dict
) -> None:

    print("\nVocê corre até o carro.")

    print("Os outros começam a descer para o estacionamento.")

    print("\nTodos entram no veículo.")

    print("Você liga o motor.")

    print("\nO carro demora alguns segundos para funcionar.")

    print("Então o motor finalmente pega.")

    print("\nVocê olha para a mansão uma última vez.")

    print("O céu começa a clarear.")

    print("\nO amanhecer chegou.")

    print("\nO carro deixa o estacionamento.")

    print("A mansão fica para trás.")

    print("\nNinguém fala durante alguns minutos.")

    print("\nVocês simplesmente continuam dirigindo.")

    print("\n==============================")
    print("            FIM")
    print("==============================")

    print("\nVOCÊS SOBREVIVERAM À NOITE.")


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
           explorar_corredor(jogador, estado)

          elif escolha == 3:
           dentro_da_sala = False

          else:
           print("\nEscolha inválida.")

        else:

         if escolha == 1:
          explorar_corredor(jogador, estado)

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
    },
    "progresso": {
    "zumbi_derrotado": False,
    "pistola_pega": False,
    "porta_final_aberta": False
    },
    "subsolo": {
        "gerador_ligado": False,
        "boss_derrotado": False,
        "municao_pega": False,
        "bandagem_pega": False
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