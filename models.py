class Produto:
    def __init__(self, nome, quantidade, custo, venda):
        self.nome = nome
        self.quantidade = quantidade
        self.custo = custo
        self.venda = venda

    @property
    def lucro_bruto(self):
        return self.venda - self.custo

    def to_tuple(self):
        return (self.nome, self.quantidade, self.custo, self.venda)