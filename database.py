import sqlite3

class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect("seal_db.db")
        self.cursor = self.conn.cursor()
        self.criar_tabelas()

    def criar_tabelas(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            nome TEXT PRIMARY KEY,
            quantidade INTEGER,
            custo REAL,
            venda REAL
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS fiscal (
            nome TEXT PRIMARY KEY,
            fornecedor TEXT,
            icms REAL,
            cofins REAL,
            pis REAL,
            ipi REAL
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            produto TEXT,
            qtd INTEGER,
            valor REAL,
            lucro REAL,
            impostos REAL
        )
        """)

        self.conn.commit()

    def salvar_produto(self, nome, quantidade, custo, venda):
        self.cursor.execute("""
        INSERT OR REPLACE INTO produtos (nome, quantidade, custo, venda)
        VALUES (?, ?, ?, ?)
        """, (nome, quantidade, custo, venda))
        self.conn.commit()

    def salvar_fiscal(self, nome, fornecedor, icms, cofins, pis, ipi):
        self.cursor.execute("""
        INSERT OR REPLACE INTO fiscal (nome, fornecedor, icms, cofins, pis, ipi)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (nome, fornecedor, icms, cofins, pis, ipi))
        self.conn.commit()

    def salvar_venda(self, data, produto, qtd, valor, lucro, impostos):
        self.cursor.execute("""
        INSERT INTO vendas (data, produto, qtd, valor, lucro, impostos)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (data, produto, qtd, valor, lucro, impostos))
        self.conn.commit()

    def excluir_produto(self, nome):
        self.cursor.execute("DELETE FROM produtos WHERE nome=?", (nome,))
        self.cursor.execute("DELETE FROM fiscal WHERE nome=?", (nome,))
        self.conn.commit()

    def carregar_produtos(self):
        self.cursor.execute("SELECT * FROM produtos")
        return self.cursor.fetchall()

    def carregar_fiscal(self):
        self.cursor.execute("SELECT * FROM fiscal")
        return self.cursor.fetchall()

    def carregar_vendas(self):
        self.cursor.execute("SELECT data, produto, qtd, valor, lucro, impostos FROM vendas")
        return self.cursor.fetchall()

    def buscar_produtos_por_nome(self, termo):
        self.cursor.execute("SELECT * FROM produtos")
        resultados = []
        for nome, q, c, v in self.cursor.fetchall():
            if termo in nome.lower():
                lucro = v - c
                resultados.append((nome, q, c, v, lucro))
        return resultados

    def fechar(self):
        self.conn.close()