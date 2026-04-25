import tkinter as tk
from database import DatabaseManager
from views import CadastroFrame, TabelaFrame, ControlesFrame

class AppBebidasContabil:
    def __init__(self, root):
        self.root = root
        self.root.title("SEAL Contábil - Gestão de Estoque e Financeiro")
        self.root.geometry("1250x780")
        self.root.configure(bg="#f4f6f9")

        # --- BANCO DE DADOS ---
        self.db = DatabaseManager()

        # Dados em Memória
        self.vendas_historico = [] 
        self.banco_fiscal = {} 

        # --- HEADER ---
        header = tk.Frame(root, bg="#2c3e50", height=70)
        header.pack(fill="x")
        tk.Label(header, text="SEAL - FINANCEIRO E ESTOQUES", 
                 font=("Segoe UI", 16, "bold"), fg="white", bg="#2c3e50").pack(pady=20)

        # --- CONTAINER PRINCIPAL ---
        container = tk.Frame(root, bg="#f4f6f9")
        container.pack(padx=20, pady=10, fill="both", expand=True)

        # --- FRAMES ---
        self.cadastro = CadastroFrame(container, self)
        self.tabela = TabelaFrame(container, self)
        self.controles = ControlesFrame(container, self)

        self.carregar_dados()

    def carregar_dados(self):
        produtos = self.db.carregar_produtos()
        for nome, q, c, v in produtos:
            lucro = v - c
            self.tabela.tabela.insert("", "end", values=(nome, q, f"{c:.2f}", f"{v:.2f}", f"{lucro:.2f}"))

        fiscais = self.db.carregar_fiscal()
        for row in fiscais:
            nome = row[0]
            self.banco_fiscal[nome] = {
                "fornecedor": row[1],
                "icms": row[2],
                "cofins": row[3],
                "pis": row[4],
                "ipi": row[5]
            }

        vendas = self.db.carregar_vendas()
        for v in vendas:
            self.vendas_historico.append({
                "data": v[0],
                "prod": v[1],
                "qtd": v[2],
                "valor": v[3],
                "lucro_liq": v[4],
                "imp": v[5]
            })

    def fechar(self):
        self.db.fechar()
        self.root.destroy()