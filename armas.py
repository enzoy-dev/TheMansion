import random


class Arma:
    def __init__(
        self,
        nome: str,
        dano_min: int,
        dano_max: int,
        chance_acerto: int,
        usa_municao: bool = False
    ) -> None:
        self.nome = nome
        self.dano_min = dano_min
        self.dano_max = dano_max
        self.chance_acerto = chance_acerto
        self.usa_municao = usa_municao

    def atacar(self, alvo) -> int:
        acerto = random.randint(1, 100)
        if acerto <= self.chance_acerto:
            dano = random.randint(self.dano_min, self.dano_max)
            print(f"\nVocê acertou o ataque e causou {dano} de dano!")
            alvo.receber_dano(dano)
            return dano
        print("\nVocê errou o ataque!")
        return 0


class Faca(Arma):
    def __init__(self) -> None:
        super().__init__(
            nome="faca",
            dano_min=10,
            dano_max=20,
            chance_acerto=80,
            usa_municao=False
        )


class Pistola(Arma):
    def __init__(self) -> None:
        super().__init__(
            nome="pistola",
            dano_min=25,
            dano_max=40,
            chance_acerto=70,
            usa_municao=True
        )


faca = Faca()
pistola = Pistola()

armas = {
    "faca": faca,
    "pistola": pistola
}