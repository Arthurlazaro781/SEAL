import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime

class CadastroFrame:
    def __init__(self, parent, app):
        self.app = app
        self.frame = tk.LabelFrame(parent, text=" Cadastro de Produto ", font=("Arial", 10, "bold"), 
                                   padx=15, pady=15, bg="white", relief="flat")
        self.frame.pack(side="left", fill="y", padx=5)

        self.vars = {}
        campos = [("Produto:", "n"), ("Quantidade:", "q"), ("Custo Unitário (R$):", "c"), ("Venda Unitária (R$):", "v")]

        for label, key in campos:
            tk.Label(self.frame, text=label, bg="white", font=("Arial", 9)).pack(anchor="w", pady=(5, 0))
            self.vars[key] = tk.Entry(self.frame, font=("Arial", 11), bd=1, relief="solid")
            self.vars[key].pack(fill="x", pady=5)

        tk.Button(self.frame, text="💾 SALVAR PRODUTO", command=self.salvar, 
                  bg="#27ae60", fg="white", font=("Arial", 10, "bold"), height=2, cursor="hand2").pack(fill="x", pady=15)
        
        tk.Button(self.frame, text="🧹 LIMPAR CAMPOS", command=self.limpar, bg="#95a5a6", fg="white", bd=0).pack(fill="x")
        
        tk.Label(self.frame, text="\n* Dê 2 cliques no item\npara configurar impostos.", 
                 font=("Arial", 8, "italic"), bg="white", fg="#7f8c8d").pack()

    def salvar(self):
        from models import Produto
        try:
            n = self.vars['n'].get()
            q = int(self.vars['q'].get())
            c = float(self.vars['c'].get().replace(',', '.'))
            v = float(self.vars['v'].get().replace(',', '.'))

            produto = Produto(n, q, c, v)

            for item in self.app.tabela.tabela.get_children():
                if self.app.tabela.tabela.item(item, "values")[0] == n:
                    self.app.tabela.tabela.item(item, values=(n, q, f"{c:.2f}", f"{v:.2f}", f"{produto.lucro_bruto:.2f}"))
                    self.app.db.salvar_produto(n, q, c, v)
                    self.limpar()
                    return

            self.app.tabela.tabela.insert("", "end", values=(n, q, f"{c:.2f}", f"{v:.2f}", f"{produto.lucro_bruto:.2f}"))
            
            if n not in self.app.banco_fiscal:
                self.app.banco_fiscal[n] = {"fornecedor": "Não Informado", "icms": 0.0, "cofins": 0.0, "pis": 0.0, "ipi": 0.0}

            self.app.db.salvar_produto(n, q, c, v)
            self.limpar()
        except:
            messagebox.showerror("Erro", "Preencha os campos corretamente.")

    def limpar(self):
        for v in self.vars.values(): 
            v.delete(0, tk.END)


class TabelaFrame:
    def __init__(self, parent, app):
        self.app = app
        self.frame = tk.Frame(parent, bg="white")
        self.frame.pack(side="left", fill="both", expand=True, padx=10)

        busca_frame = tk.Frame(self.frame, bg="white")
        busca_frame.pack(fill="x")

        tk.Label(busca_frame, text="🔍 Buscar produto:", bg="white").pack(side="left", padx=5)

        self.busca_var = tk.StringVar()
        self.busca_entry = tk.Entry(busca_frame, textvariable=self.busca_var)
        self.busca_entry.pack(side="left", fill="x", expand=True, padx=5)

        self.busca_var.trace("w", self.filtrar_produtos)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", rowheight=32, font=("Segoe UI", 10))
        
        self.tabela = ttk.Treeview(self.frame, columns=("n", "q", "c", "v", "l"), show="headings")
        headings = [("n", "Produto"), ("q", "Estoque"), ("c", "Custo (R$)"), ("v", "Venda (R$)"), ("l", "Margem Bruta")]
        
        for id, texto in headings:
            self.tabela.heading(id, text=texto)
            self.tabela.column(id, anchor="center", width=120)

        self.tabela.pack(fill="both", expand=True)
        self.tabela.bind("<Double-1>", self.on_double_click)

    def on_double_click(self, event):
        sel = self.tabela.selection()
        if sel:
            self.carregar_campos(event)
            self.abrir_aba_fiscal_detalhada(event)

    def abrir_aba_fiscal_detalhada(self, event):
        sel = self.tabela.selection()
        if not sel: return
        nome_prod = self.tabela.item(sel, "values")[0]

        if nome_prod not in self.app.banco_fiscal:
            self.app.banco_fiscal[nome_prod] = {"fornecedor": "Não Informado", "icms": 0.0, "cofins": 0.0, "pis": 0.0, "ipi": 0.0}

        janela = tk.Toplevel(self.app.root)
        janela.title(f"Configuração de Impostos: {nome_prod}")
        janela.geometry("400x520")
        janela.configure(bg="#fdfdfd", padx=25, pady=20)
        janela.grab_set()

        tk.Label(janela, text=f"DETALHAMENTO FISCAL", font=("Arial", 12, "bold"), bg="#fdfdfd").pack(pady=10)

        tk.Label(janela, text="Fornecedor:", bg="#fdfdfd").pack(anchor="w")
        ent_forn = tk.Entry(janela, width=40); ent_forn.pack(pady=5)
        ent_forn.insert(0, self.app.banco_fiscal[nome_prod]['fornecedor'])

        impostos_frame = tk.LabelFrame(janela, text=" Alíquotas (%) ", padx=10, pady=10, bg="white")
        impostos_frame.pack(fill="x", pady=10)

        campos_imp = {}
        tributos = [("ICMS (R$):", "icms"), ("COFINS (R$):", "cofins"), ("PIS (R$):", "pis"), ("IPI (R$):", "ipi")]

        for label, key in tributos:
            f = tk.Frame(impostos_frame, bg="white")
            f.pack(fill="x", pady=2)
            tk.Label(f, text=label, bg="white", width=12, anchor="w").pack(side="left")
            ent = tk.Entry(f, width=10)
            ent.pack(side="right")
            ent.insert(0, str(self.app.banco_fiscal[nome_prod][key]))
            campos_imp[key] = ent

        def salvar_fiscal():
            try:
                self.app.banco_fiscal[nome_prod] = {
                    "fornecedor": ent_forn.get(),
                    "icms": float(campos_imp['icms'].get().replace(',', '.')),
                    "cofins": float(campos_imp['cofins'].get().replace(',', '.')),
                    "pis": float(campos_imp['pis'].get().replace(',', '.')),
                    "ipi": float(campos_imp['ipi'].get().replace(',', '.'))
                }

                self.app.db.salvar_fiscal(
                    nome_prod,
                    ent_forn.get(),
                    float(campos_imp['icms'].get().replace(',', '.')),
                    float(campos_imp['cofins'].get().replace(',', '.')),
                    float(campos_imp['pis'].get().replace(',', '.')),
                    float(campos_imp['ipi'].get().replace(',', '.'))
                )

                messagebox.showinfo("Sucesso", "Configuração fiscal salva!")
                janela.destroy()
            except:
                messagebox.showerror("Erro", "Valores de impostos devem ser numéricos.")

        tk.Button(janela, text="GRAVAR TRIBUTAÇÃO", command=salvar_fiscal, 
                  bg="#2980b9", fg="white", font=("Arial", 10, "bold"), height=2).pack(fill="x", pady=20)

    def carregar_campos(self, event):
        sel = self.tabela.selection()
        if sel:
            item = self.tabela.item(sel, "values")
            self.app.cadastro.limpar()
            self.app.cadastro.vars['n'].insert(0, item[0])
            self.app.cadastro.vars['q'].insert(0, item[1])
            self.app.cadastro.vars['c'].insert(0, item[2])
            self.app.cadastro.vars['v'].insert(0, item[3])

    def filtrar_produtos(self, *args):
        termo = self.busca_var.get().lower()

        for item in self.tabela.get_children():
            self.tabela.delete(item)

        resultados = self.app.db.buscar_produtos_por_nome(termo)
        for nome, q, c, v, lucro in resultados:
            self.tabela.insert("", "end", values=(nome, q, f"{c:.2f}", f"{v:.2f}", f"{lucro:.2f}"))


class ControlesFrame:
    def __init__(self, parent, app):
        self.app = app
        self.frame = tk.LabelFrame(parent, text=" Operações ", font=("Arial", 10, "bold"), padx=15, pady=15, bg="white")
        self.frame.pack(side="right", fill="y", padx=5)

        tk.Button(self.frame, text="🛒 REGISTRAR VENDA\n& EMITIR NOTA", command=self.vender, 
                  bg="#e67e22", fg="white", font=("Arial", 10, "bold"), width=22, height=4).pack(pady=10)
        
        tk.Button(self.frame, text="📊 BALANÇO MENSAL", command=self.gerar_balanco, 
                  bg="#8e44ad", fg="white", font=("Arial", 10, "bold"), width=22, height=2).pack(pady=10)
        
        tk.Button(self.frame, text="🗑️ EXCLUIR ITEM", command=self.excluir, 
                  bg="#c0392b", fg="white", width=22).pack(side="bottom", pady=10)

    def vender(self):
        sel = self.app.tabela.tabela.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um produto na tabela!")
            return
        
        item = list(self.app.tabela.tabela.item(sel, "values"))
        nome_p, estoque = item[0], int(item[1])
        qtd = simpledialog.askinteger("Venda", f"Quantidade de {nome_p}:", minvalue=1)
        
        if not qtd or qtd > estoque:
            messagebox.showerror("Erro", "Quantidade inválida ou insuficiente.")
            return

        janela_cli = tk.Toplevel(self.app.root)
        janela_cli.title("Checkout - Dados do Cliente")
        janela_cli.geometry("400x500")
        janela_cli.grab_set()

        tk.Label(janela_cli, text="DADOS PARA EMISSÃO DE NOTA", font=("Arial", 11, "bold")).pack(pady=10)
        
        campos_cli = {}
        labels = [("Nome/Razão Social:", "nome"), ("CPF/CNPJ:", "doc"), ("Telefone:", "tel"), ("Endereço:", "end")]
        for lb, key in labels:
            tk.Label(janela_cli, text=lb).pack(anchor="w", padx=25)
            e = tk.Entry(janela_cli, width=40); e.pack(pady=2, padx=25)
            campos_cli[key] = e

        def processar_venda():
            cli = {k: v.get() for k, v in campos_cli.items()}
            if not cli['nome'] or not cli['doc']:
                messagebox.showerror("Erro", "Nome e CPF/CNPJ são obrigatórios!")
                return

            custo_un, venda_un = float(item[2]), float(item[3])
            fisc = self.app.banco_fiscal[nome_p]
            val_imp_un = fisc['icms'] + fisc['cofins'] + fisc['pis'] + fisc['ipi']
            lucro_liq = (venda_un - custo_un - val_imp_un) * qtd

            self.app.vendas_historico.append({
                "data": datetime.now().strftime("%d/%m %H:%M"),
                "prod": nome_p, "qtd": qtd, "valor": venda_un * qtd, "lucro_liq": lucro_liq, "imp": val_imp_un * qtd
            })

            self.app.db.salvar_venda(
                datetime.now().strftime("%d/%m %H:%M"),
                nome_p,
                qtd,
                venda_un * qtd,
                lucro_liq,
                val_imp_un * qtd
            )

            item[1] = estoque - qtd
            self.app.tabela.tabela.item(sel, values=item)
            
            self.exibir_nota_fiscal(cli, nome_p, qtd, venda_un, val_imp_un, fisc)
            janela_cli.destroy()

        tk.Button(janela_cli, text="FINALIZAR E EMITIR NOTA", command=processar_venda, 
                  bg="#27ae60", fg="white", font=("Arial", 10, "bold"), height=2).pack(pady=20)

    def exibir_nota_fiscal(self, cli, prod, qtd, preco, imp_un, fisc):
        janela_nf = tk.Toplevel(self.app.root)
        janela_nf.title("Nota Fiscal Eletrônica (Simulação)")
        janela_nf.geometry("600x650")

        txt_nf = f"""
===========================================================
                NOTA FISCAL DE VENDA (SIMULADA)
===========================================================
DATA/HORA: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
-----------------------------------------------------------
CLIENTE: {cli['nome'].upper()}
CPF/CNPJ: {cli['doc']}
TELEFONE: {cli['tel']}
ENDEREÇO: {cli['end'].upper()}
-----------------------------------------------------------
PRODUTO: {prod.upper()}
QUANTIDADE: {qtd}
VALOR UNIT: R$ {preco:.2f}
VALOR TOTAL: R$ {preco * qtd:.2f}
-----------------------------------------------------------
DETALHAMENTO TRIBUTÁRIO (LEI 12.741/12):
ICMS: R$ {fisc['icms']:.2f} | PIS: R$ {fisc['pis']:.2f} | COFINS: R$ {fisc['cofins']:.2f} | IPI: R$ {fisc['ipi']:.2f}
TOTAL DE IMPOSTOS NESTA NOTA: R$ {imp_un * qtd:.2f}
-----------------------------------------------------------
VALOR LÍQUIDO DA OPERAÇÃO: R$ {(preco * qtd) - (imp_un * qtd):.2f}
===========================================================
        """
        
        area = tk.Text(janela_nf, font=("Courier New", 10), bg="#fdfdfd")
        area.insert("1.0", txt_nf)
        area.config(state="disabled")
        area.pack(padx=20, pady=20, fill="both", expand=True)

        def imprimir():
            nome_arq = f"Nota_{prod}_{datetime.now().strftime('%H%M%S')}.txt"
            with open(nome_arq, "w", encoding="utf-8") as f:
                f.write(txt_nf)
            messagebox.showinfo("Impressão", f"Nota Fiscal 'impressa' com sucesso em: {nome_arq}")

        tk.Button(janela_nf, text="🖨️ IMPRIMIR NOTA (.TXT)", command=imprimir, 
                  bg="#3498db", fg="white", font=("Arial", 10, "bold")).pack(pady=10)

    def gerar_balanco(self):
        if not self.app.vendas_historico:
            messagebox.showinfo("Aviso", "Sem vendas para o relatório.")
            return

        faturamento = sum(v['valor'] for v in self.app.vendas_historico)
        lucro_liquido = sum(v['lucro_liq'] for v in self.app.vendas_historico)
        total_impostos = sum(v['imp'] for v in self.app.vendas_historico)

        txt = f"RELATÓRIO FISCAL E FINANCEIRO MENSAL - {datetime.now().strftime('%m/%Y')}\n"
        txt += "="*70 + "\n"
        txt += f"{'DATA':<12} | {'PRODUTO':<18} | {'QTD':<5} | {'IMPOSTO':<10} | {'LUCRO LÍQ.':<10}\n"
        txt += "-"*70 + "\n"
        for v in self.app.vendas_historico:
            txt += f"{v['data']:<12} | {v['prod']:<18} | {v['qtd']:<5} | R$ {v['imp']:>8.2f} | R$ {v['lucro_liq']:>8.2f}\n"
        
        txt += "="*70 + "\n"
        txt += f"FATURAMENTO BRUTO:    R$ {faturamento:>12.2f}\n"
        txt += f"TOTAL IMPOSTOS PAGOS: R$ {total_impostos:>12.2f}\n"
        txt += f"LUCRO LÍQUIDO REAL:   R$ {lucro_liquido:>12.2f}\n"
        txt += "="*70 + "\n"

        janela_rel = tk.Toplevel(self.app.root)
        janela_rel.title("Relatório de Lucros e Impostos")
        janela_rel.geometry("700x550")
        frame_txt = tk.Frame(janela_rel); frame_txt.pack(padx=20, pady=20, fill="both", expand=True)
        scr = tk.Scrollbar(frame_txt); scr.pack(side="right", fill="y")
        area = tk.Text(frame_txt, font=("Courier New", 10), yscrollcommand=scr.set); area.insert("1.0", txt)
        area.config(state="disabled"); area.pack(side="left", fill="both", expand=True); scr.config(command=area.yview)

    def excluir(self):
        sel = self.app.tabela.tabela.selection()

        if not sel:
            messagebox.showwarning("Aviso", "Selecione um produto para excluir.")
            return

        item_id = sel[0]
        valores = self.app.tabela.tabela.item(item_id, "values")

        if not valores:
            messagebox.showerror("Erro", "Não foi possível obter o produto.")
            return

        nome = valores[0]

        confirmar = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Tem certeza que deseja excluir o produto '{nome}'?"
        )

        if not confirmar:
            return

        try:
            self.app.db.excluir_produto(nome)

            if nome in self.app.banco_fiscal:
                del self.app.banco_fiscal[nome]

            self.app.tabela.tabela.delete(item_id)

            messagebox.showinfo("Sucesso", "Produto excluído com sucesso!")

        except Exception as e:
            messagebox.showerror("Erro", str(e))