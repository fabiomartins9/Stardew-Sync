import os
import shutil
import re
import customtkinter as ctk
from tkinter import messagebox

class StardewCloner(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Stardew Save Manager - Fix Final")
        self.geometry("600x550")
        ctk.set_appearance_mode("dark")
        self.base_path = os.path.join(os.getenv('APPDATA'), 'StardewValley', 'Saves')
        self.setup_ui()

    def setup_ui(self):
        ctk.CTkLabel(self, text="Gerenciador de Saves - Stardew", font=("Arial", 22, "bold")).pack(pady=20)
        self.atualizar_lista()
        
        ctk.CTkLabel(self, text="Selecione o save original:").pack()
        self.save_selector = ctk.CTkOptionMenu(self, values=self.saves, width=400)
        self.save_selector.pack(pady=10)

        self.name_entry = ctk.CTkEntry(self, placeholder_text="Novo nome do PERSONAGEM", width=400)
        self.name_entry.pack(pady=10)

        self.farm_entry = ctk.CTkEntry(self, placeholder_text="Novo nome da FAZENDA", width=400)
        self.farm_entry.pack(pady=10)

        self.btn_clonar = ctk.CTkButton(self, text="CLONAR E FORÇAR RENOMEAÇÃO", command=self.executar_clonagem, 
                                        fg_color="#2ecc71", height=50, font=("Arial", 14, "bold"))
        self.btn_clonar.pack(pady=25)

        self.btn_limpar = ctk.CTkButton(self, text="LIMPAR CÓPIAS", command=self.limpar_duplicatas, fg_color="#e74c3c")
        self.btn_limpar.pack(pady=5)

    def atualizar_lista(self):
        if os.path.exists(self.base_path):
            self.saves = [f for f in os.listdir(self.base_path) if os.path.isdir(os.path.join(self.base_path, f))]
        else: self.saves = ["Erro: Pasta não encontrada"]

    def substituir_tags(self, conteudo, novo_nome, nova_fazenda):
        # Regex explica: Procure por <name> QUALQUER_COISA </name> e troque pelo novo nome
        # O 'count=1' garante que só mude o nome do jogador no início do arquivo
        conteudo = re.sub(r'<name>.*?</name>', f'<name>{novo_nome}</name>', conteudo, count=1)
        conteudo = re.sub(r'<farmName>.*?</farmName>', f'<farmName>{nova_fazenda}</farmName>', conteudo, count=1)
        return conteudo

    def executar_clonagem(self):
        pasta_origem = self.save_selector.get()
        novo_char = self.name_entry.get().strip()
        nova_faz = self.farm_entry.get().strip()

        if not novo_char or not nova_faz:
            messagebox.showwarning("Aviso", "Preencha todos os campos!")
            return

        try:
            nome_antigo_char = pasta_origem.split('_')[0]
            id_save = pasta_origem.split('_')[-1]
            novo_id_pasta = novo_char.replace(" ", "")
            nova_pasta_nome = f"{novo_id_pasta}_{id_save}"
            
            caminho_origem = os.path.join(self.base_path, pasta_origem)
            caminho_destino = os.path.join(self.base_path, nova_pasta_nome)

            if os.path.exists(caminho_destino):
                shutil.rmtree(caminho_destino)

            shutil.copytree(caminho_origem, caminho_destino)

            for arquivo in os.listdir(caminho_destino):
                caminho_atual = os.path.join(caminho_destino, arquivo)
                if arquivo.endswith("_old"):
                    os.remove(caminho_atual)
                    continue

                # Renomeia o arquivo físico
                novo_nome_arq = arquivo.replace(nome_antigo_char, novo_id_pasta)
                novo_caminho_arq = os.path.join(caminho_destino, novo_nome_arq)
                os.rename(caminho_atual, novo_caminho_arq)

                # Edição com Regex (independente de espaços ou caracteres ocultos)
                with open(novo_caminho_arq, 'r', encoding='utf-8', errors='ignore') as f:
                    conteudo = f.read()

                conteudo_editado = self.substituir_tags(conteudo, novo_char, nova_faz)

                with open(novo_caminho_arq, 'w', encoding='utf-8') as f:
                    f.write(conteudo_editado)

            messagebox.showinfo("Sucesso", "Save alterado com sucesso!")
            self.atualizar_lista()
            self.save_selector.configure(values=self.saves)

        except Exception as e:
            messagebox.showerror("Erro", f"Erro crítico: {e}")

    def limpar_duplicatas(self):
        if messagebox.askyesno("Confirmar", "Apagar saves que não começam com 'Fabio'?"):
            for pasta in os.listdir(self.base_path):
                if not pasta.startswith("Fabio") and "_" in pasta:
                    shutil.rmtree(os.path.join(self.base_path, pasta))
            self.atualizar_lista()
            self.save_selector.configure(values=self.saves)

if __name__ == "__main__":
    app = StardewCloner()
    app.mainloop()