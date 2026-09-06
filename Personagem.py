from typing import TypedDict

from inimigo import Inimigo
from armas import Arma


class Item(TypedDict):
    nome: str
    tipo: str
    quantidade: int


class Personagem:
    def __init__(
        self,
        nome: str,
        vida: int,
        inventario: list[Item] | None = None
    ) -> None:
        self.nome = nome
        self.vida_maxima = vida
        self._vida = vida
        self.inventario = inventario if inventario is not None else []
        self.arma_equipada: Arma | None = None

    @property
    def vida(self) -> int:
        return self._vida

    @vida.setter
    def vida(self, valor: int) -> None:
        if valor < 0:
            self._vida = 0
        elif valor > self.vida_maxima:
            self._vida = self.vida_maxima
        else:
            self._vida = valor

    def equipar_arma(self, arma: Arma) -> bool:
        if self.quantidade_item(arma.nome) > 0:
            self.arma_equipada = arma
            print(f"\nVocê equipou a {arma.nome}.")
            return True

        print(f"\nVocê não possui a {arma.nome} no inventário.")
        return False

    def atacar(self, inimigo: Inimigo) -> None:
        if self.arma_equipada:
            self.arma_equipada.atacar(inimigo)
        else:
            print("\nVocê não tem uma arma equipada!")

    def adicionar_item(self, nome_item: str, tipo: str, quantidade: int = 1) -> None:
        for item in self.inventario:
            if item["nome"] == nome_item:
                item["quantidade"] += quantidade
                print(f"\nVocê encontrou {quantidade} {nome_item}(s).")
                return
        self.inventario.append({"nome": nome_item, "tipo": tipo, "quantidade": quantidade})
        print(f"\nVocê encontrou {quantidade} {nome_item}(s).")

    def quantidade_item(self, nome_item: str) -> int:
        for item in self.inventario:
            if item["nome"] == nome_item:
                return item["quantidade"]
        return 0

    def usar_item(self, nome_item: str, quantidade: int = 1) -> bool:
        for item in self.inventario:
            if item["nome"] == nome_item and item["quantidade"] >= quantidade:
                item["quantidade"] -= quantidade
                if item["quantidade"] == 0:
                    self.inventario.remove(item)
                return True
        return False

    def receber_dano(self, dano: int) -> None:
        self.vida -= dano
        print(f"\nVocê recebeu {dano} de dano!")
        print(f"Vida atual: {self.vida}")

    def curar(self, quantidade: int) -> None:
        self.vida += quantidade
        print(f"\nVocê usa uma bandagem e recupera {quantidade} de vida!")

    def esta_vivo(self) -> bool:
        return self.vida > 0

    def mostrar_status(self) -> None:
        print("\n----------------------------")
        print(f"Vida: {self.vida}")

        if len(self.inventario) == 0:
            print("Inventário: vazio")
        else:
            print("Inventário:")
            for item in self.inventario:
                print(f"- {item['nome']} x{item['quantidade']}")

        if self.arma_equipada:
            print(f"Arma equipada: {self.arma_equipada.nome}")
        else:
            print("Arma equipada: nenhuma")

        print("----------------------------")