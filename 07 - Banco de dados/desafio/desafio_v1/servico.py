from sqlite3 import Cursor
from dominio import Cliente, PessoaFisica, PessoaJuridica


class ClienteServico:
    def __init__(self, cursor: Cursor) -> None:
        self.cursor = cursor

    def filtrar_cliente(self, documento: str) -> Cliente | None:
        # Busca no banco se o documento digitado já existe como CPF ou CNPJ
        self.cursor.execute(
            "SELECT email, telefone, status, tipo_cliente, nome, cpf, renda_mensal, nome_fantasia, cnpj, faturamento_anual FROM clientes WHERE cpf = ? OR cnpj = ?", 
            (documento, documento)
        )
        row = self.cursor.fetchone()

        if not row:
            return None

        # Desempacota os dados da linha retornada do banco
        email, telefone, status, tipo_cliente, nome, cpf, renda_mensal, nome_fantasia, cnpj, faturamento_anual = row

        # Instancia e retorna a classe de domínio correta com base no tipo salvo
        if tipo_cliente == "PF":
            return PessoaFisica(email=email, telefone=telefone, status=status, nome=nome, cpf=cpf, renda_mensal=renda_mensal)
        else:
            return PessoaJuridica(email=email, telefone=telefone, status=status, nome_fantasia=nome_fantasia, cnpj=cnpj, faturamento_anual=faturamento_anual)

    def _criar_cliente_pessoa_fisica(self, documento: str) -> PessoaFisica:
        nome = input("Informe o nome completo: ")
        renda_mensal = float(input("Informe sua renda mensal: "))
        email = input("Informe seu email: ")
        telefone = input("Informe seu telefone: ")

        cliente = PessoaFisica(
            nome=nome, cpf=documento, renda_mensal=renda_mensal, email=email, telefone=telefone, status="ativo"
        )

        # Insere fisicamente o registro de Pessoa Física na tabela do banco de dados
        self.cursor.execute("""
            INSERT INTO clientes (email, telefone, status, tipo_cliente, nome, cpf, renda_mensal)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (cliente.email, cliente.telefone, cliente.status, "PF", cliente.nome, cliente.cpf, cliente.renda_mensal))

        return cliente

    def _criar_cliente_pessoa_juridica(self, documento: str) -> PessoaJuridica:
        nome = input("Informe o nome fantasia: ")
        faturamento_anual = float(input("Informe seu faturamento anual: "))
        email = input("Informe seu email: ")
        telefone = input("Informe seu telefone: ")

        cliente = PessoaJuridica(
            nome_fantasia=nome,
            cnpj=documento,
            faturamento_anual=faturamento_anual,
            email=email,
            telefone=telefone,
            status="active",
        )

        # Insere fisicamente o registro de Pessoa Jurídica na tabela do banco de dados
        self.cursor.execute("""
            INSERT INTO clientes (email, telefone, status, tipo_cliente, nome_fantasia, cnpj, faturamento_anual)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (cliente.email, cliente.telefone, cliente.status, "PJ", cliente.nome_fantasia, cliente.cnpj, cliente.faturamento_anual))

        return cliente

    def criar_cliente(self) -> None:
        documento = input("Informe o documento (CPF/CNPJ): ")
        cliente = self.filtrar_cliente(documento)

        if cliente:
            print("\n@@@ Já existe cliente com esse documento (CPF/CNPJ)! @@@")
            return

        if len(documento) == 11:
            cliente = self._criar_cliente_pessoa_fisica(documento=documento)
        else:
            cliente = self._criar_cliente_pessoa_juridica(documento=documento)

        print("\n", cliente)
        print("\n=== Cliente criado com sucesso! ===")

    def listar_clientes(self) -> None:
        # Recupera as informações básicas de todos os clientes cadastrados no banco de dados
        self.cursor.execute("SELECT tipo_cliente, nome, cpf, nome_fantasia, cnpj, email FROM clientes")
        clientes = self.cursor.fetchall()

        if not clientes:
            print("\n@@@ Não existem clientes cadastrados! @@@")
            return

        print("\n================ LISTA DE CLIENTES ================")
        for row in clientes:
            tipo, nome, cpf, nome_fantasia, cnpj, email = row
            if tipo == "PF":
                print(f"Pessoa Física - Nome: {nome} | CPF: {cpf} | Email: {email}")
            else:
                print(f"Pessoa Jurídica - Nome Fantasia: {nome_fantasia} | CNPJ: {cnpj} | Email: {email}")
        print("===================================================")
