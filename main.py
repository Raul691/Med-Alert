import json
import os

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen


ARQUIVO_JSON = "remedios.json"


class HomeScreen(Screen):

    def on_enter(self):
        Clock.schedule_once(lambda dt: self.atualizar())

    def atualizar(self):
        if "total_med" not in self.ids or "estoque_baixo" not in self.ids:
            return

        app = App.get_running_app()

        if not hasattr(app, "remedios"):
            self.ids.total_med.text = "0"
            self.ids.estoque_baixo.text = "0"
            return

        total = len(app.remedios)
        estoque_baixo = sum(
            1 for r in app.remedios
            if int(r["quantidade"]) <= 5
        )

        self.ids.total_med.text = str(total)
        self.ids.estoque_baixo.text = str(estoque_baixo)


class MedicamentosScreen(Screen):

    def on_enter(self):
        self.atualizar_lista()

    def atualizar_lista(self):
        app = App.get_running_app()

        texto = ""

        for r in app.remedios:
            texto += (
                f" {r['nome']}\n"
                f"Quantidade: {r['quantidade']}\n"
                f"Horário: {r['horario']}\n\n"
            )

        self.ids.lista.text = texto


class AdicionarScreen(Screen):

    def salvar_medicamento(self):

        nome = self.ids.nome.text
        quantidade = self.ids.quantidade.text
        horario = self.ids.horario.text

        if not nome or not quantidade or not horario:
            self.ids.msg.text = "Preencha todos os campos"
            return

        app = App.get_running_app()

        app.remedios.append({
            "nome": nome,
            "quantidade": quantidade,
            "horario": horario
        })

        app.salvar_dados()

        self.ids.msg.text = "Medicamento salvo!"

        self.ids.nome.text = ""
        self.ids.quantidade.text = ""
        self.ids.horario.text = ""


class EstoqueScreen(Screen):

    def on_enter(self):
        self.atualizar()

    def atualizar(self):

        app = App.get_running_app()

        texto = ""

        for r in app.remedios:

            alerta = ""

            if int(r["quantidade"]) <= 5:
                alerta = " ⚠ ESTOQUE BAIXO"

            texto += (
                f"{r['nome']} - "
                f"{r['quantidade']} comprimidos"
                f"{alerta}\n"
            )

        self.ids.estoque_lista.text = texto

    def consumir(self):

        nome = self.ids.nome_consumo.text

        app = App.get_running_app()

        for r in app.remedios:

            if r["nome"].lower() == nome.lower():

                qtd = int(r["quantidade"])

                if qtd > 0:
                    r["quantidade"] = str(qtd - 1)

                    app.salvar_dados()

                    self.ids.msg.text = (
                        f"Consumo registrado para {nome}"
                    )

                    self.atualizar()
                    return

        self.ids.msg.text = "Medicamento não encontrado"


class Gerenciador(ScreenManager):
    pass


class MedAlertApp(App):

    remedios = []

    def build(self):
        self.carregar_dados()
        return None

    def salvar_dados(self):

        with open(
            ARQUIVO_JSON,
            "w",
            encoding="utf-8"
        ) as arquivo:

            json.dump(
                self.remedios,
                arquivo,
                ensure_ascii=False,
                indent=4
            )

    def carregar_dados(self):

        if os.path.exists(ARQUIVO_JSON):

            with open(
                ARQUIVO_JSON,
                "r",
                encoding="utf-8"
            ) as arquivo:

                self.remedios = json.load(arquivo)


if __name__ == "__main__":
    MedAlertApp().run()