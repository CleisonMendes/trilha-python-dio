from sqlite3 import Cursor
from dominio import Cliente, PessoaFisica, PessoaJuridica


class BancoServico:
    def __init__(self, cursor: Cursor) -> None:
        self.cursor = cursor

    # ================= FILTROS E BUSCAS =================
    def filtrar_cliente(self, documento: str) -> dict | None:
        # Busca se o documento existe em Pessoa Física ou Pessoa Jurídica
        self.cursor.execute("""
            SELECT c.id, c.email, c.telefone, c.status 
            FROM cliente c
            LEFT JOIN pessoa_fisica pf ON c.id = pf.cliente_id
            LEFT JOIN pessoa_juridica pj ON c.id = pj.cliente_id
            WHERE pf.cpf = ? OR pj.cnpj = ?
        """, (documento, documento))
        
        row = self.cursor.fetchone()
        if not row:
            return None
            
        return {"id": row[0], "email": row[1], "telefone": row[2], "status": row[3]}

    def buscar_conta_por_numero(self, numero: int) -> dict | None:
        self.cursor.execute("SELECT id, numero, saldo, limite, limite_saques FROM conta WHERE numero = ?", (numero,))
        row = self.cursor.fetchone()
        if not row:
            return None
        return {"id": row[0], "numero": row[1], "saldo": row[2], "limite": row[3], "limite_saques": row[4]}

    # ================= CLIENTES =================
    def criar_cliente(self) -> None:
        documento = input("Informe o documento (CPF/CNPJ): ")
        if self.filtrar_cliente(documento):
            print("\n@@@ Já existe cliente com esse documento! @@@")
            return

        email = input("Informe o email: ")
        telefone = input("Informe o telefone: ")
        status = "ativo"

        # 1. Insere na tabela genérica 'cliente'
        self.cursor.execute(
            "INSERT INTO cliente (email, telefone, status) VALUES (?, ?, ?)", 
            (email, telefone, status)
        )
        cliente_id = self.cursor.lastrowid  # Pega o ID gerado automaticamente

        # 2. Insere na tabela específica correspondente
        if len(documento) == 11:
            nome = input("Informe o nome completo: ")
            renda_mensal = float(input("Informe a renda mensal: "))
            self.cursor.execute(
                "INSERT INTO pessoa_fisica (cliente_id, nome, cpf, renda_mensal) VALUES (?, ?, ?, ?)",
                (cliente_id, nome, documento, renda_mensal)
            )
        else:
            nome_fantasia = input("Informe o nome fantasia: ")
            faturamento_anual = float(input("Informe o faturamento anual: "))
            self.cursor.execute(
                "INSERT INTO pessoa_juridica (cliente_id, nome_fantasia, cnpj, faturamento_anual) VALUES (?, ?, ?, ?)",
                (cliente_id, nome_fantasia, documento, faturamento_anual)
            )

        print("\n=== Cliente criado com sucesso! ===")

    def listar_clientes(self) -> None:
        self.cursor.execute("""
            SELECT c.id, pf.nome, pf.cpf, pj.nome_fantasia, pj.cnpj, c.email 
            FROM cliente c
            LEFT JOIN pessoa_fisica pf ON c.id = pf.cliente_id
            LEFT JOIN pessoa_juridica pj ON c.id = pj.cliente_id
        """)
        clientes = self.cursor.fetchall()

        if not clientes:
            print("\n@@@ Não existem clientes cadastrados! @@@")
            return

        print("\n================ LISTA DE CLIENTES ================")
        for row in clientes:
            cid, nome, cpf, nome_fantasia, cnpj, email = row
            if cpf:
                print(f"[ID: {cid}] PF - Nome: {nome} | CPF: {cpf} | Email: {email}")
            else:
                print(f"[ID: {cid}] PJ - Empresa: {nome_fantasia} | CNPJ: {cnpj} | Email: {email}")

    # ================= CONTAS =================
    def criar_conta(self) -> None:
        documento = input("Informe o documento do titular (CPF/CNPJ): ")
        cliente = self.filtrar_cliente(documento)

        if not cliente:
            print("\n@@@ Cliente não encontrado! Cadastre o cliente primeiro. @@@")
            return

        # Gera o próximo número de conta sequencial de forma simples
        self.cursor.execute("SELECT MAX(numero) FROM conta")
        max_num = self.cursor.fetchone()[0]
        numero_conta = (max_num or 0) + 1
        agencia = "0001"
        limite = 500.0
        limite_saques = 3

        self.cursor.execute(
            "INSERT INTO conta (numero, agencia, limite, limite_saques, cliente_id) VALUES (?, ?, ?, ?, ?)",
            (numero_conta, agencia, limite, limite_saques, cliente["id"])
        )
        print(f"\n=== Conta criada com sucesso! Agência: {agencia} | Número: {numero_conta} ===")

    def listar_contas(self) -> None:
        self.cursor.execute("""
            SELECT co.numero, co.agencia, co.saldo, pf.nome, pj.nome_fantasia 
            FROM conta co
            JOIN cliente cl ON co.cliente_id = cl.id
            LEFT JOIN pessoa_fisica pf ON cl.id = pf.cliente_id
            LEFT JOIN pessoa_juridica pj ON cl.id = pj.cliente_id
        """)
        contas = self.cursor.fetchall()

        if not contas:
            print("\n@@@ Não existem contas cadastradas! @@@")
            return

        print("\n================ LISTA DE CONTAS ================")
        for row in contas:
            numero, agencia, saldo, pf_nome, pj_nome = row
            titular = pf_nome if pf_nome else pj_nome
            print(f"Agência: {agencia} | Conta: {numero} | Saldo: R${saldo:.2f} | Titular: {titular}")

    # ================= OPERAÇÕES BANCÁRIAS =================
    def depositar(self) -> None:
        num_conta = int(input("Informe o número da conta para depósito: "))
        conta = self.buscar_conta_por_numero(num_conta)

        if not conta:
            print("\n@@@ Conta não encontrada! @@@")
            return

        valor = float(input("Informe o valor do depósito: "))
        if valor <= 0:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
            return

        # Atualiza saldo e adiciona histórico de transação usando o id obtido da conta
        novo_saldo = conta["saldo"] + valor
        self.cursor.execute("UPDATE conta SET saldo = ? WHERE id = ?", (novo_saldo, conta["id"]))
        self.cursor.execute("INSERT INTO transacao (tipo, valor, conta_id) VALUES (?, ?, ?)", ("deposito", valor, conta["id"]))
        print(f"\n=== Depósito de R${valor:.2f} realizado com sucesso! ===")

    def sacar(self) -> None:
        num_conta = int(input("Informe o número da conta para saque: "))
        conta = self.buscar_conta_por_numero(num_conta)

        if not conta:
            print("\n@@@ Conta não encontrada! @@@")
            return

        valor = float(input("Informe o valor do saque: "))

        # Validações de limites e saldo
        excedeu_saldo = valor > conta["saldo"]
        excedeu_limite = valor > conta["limite"]

        # Conta quantos saques já foram feitos hoje na tabela de transações
        self.cursor.execute(
            "SELECT COUNT(*) FROM transacao WHERE conta_id = ? AND tipo = 'saque' AND date(data) = date('now')", 
            (conta["id"],)
        )
        total_saques_hoje = self.cursor.fetchone()[0]
        excedeu_saques = total_saques_hoje >= conta["limite_saques"]

        if excedeu_saldo:
            print("\n@@@ Operação falhou! Você não tem saldo suficiente. @@@")
        elif excedeu_limite:
            print(f"\n@@@ Operação falhou! O valor do saque excede o limite por operação de R${conta['limite']:.2f}. @@@")
        elif excedeu_saques:
            print("\n@@@ Operação falhou! Número máximo de saques diários atingido. @@@")
        elif valor > 0:
            novo_saldo = conta["saldo"] - valor
            self.cursor.execute("UPDATE conta SET saldo = ? WHERE id = ?", (novo_saldo, conta["id"]))
            self.cursor.execute("INSERT INTO transacao (tipo, valor, conta_id) VALUES (?, ?, ?)", ("saque", valor, conta["id"]))
            print(f"\n=== Saque de R${valor:.2f} realizado com sucesso! ===")
        else:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")

    def emitir_extrato(self) -> None:
        num_conta = int(input("Informe o número da conta: "))
        conta = self.buscar_conta_por_numero(num_conta)

        if not conta:
            print("\n@@@ Conta não encontrada! @@@")
            return

        self.cursor.execute("SELECT tipo, valor, data FROM transacao WHERE conta_id = ? ORDER BY data ASC", (conta["id"],))
        transacoes = self.cursor.fetchall()

        print("\n================ EXTRATO ================")
        if not transacoes:
            print("Não foram realizadas movimentações.")
        else:
            for tipo, valor, data in transacoes:
                sinal = "+" if tipo == "deposito" else "-"
                print(f"[{data}] {tipo.upper()}: {sinal}R${valor:.2f}")
        
        print(f"\nSaldo atual: R${conta['saldo']:.2f}")
        print("==========================================")
