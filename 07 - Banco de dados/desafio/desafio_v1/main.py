import textwrap
from bd import criar_conexao, criar_bd
from servico import ClienteServico


def menu():
    menu = """\n
    ================ MENU ================
    [1]\tNovo cliente
    [2]\tListar clientes
    [0]\tSair
    => """
    return input(textwrap.dedent(menu))


def main():
    # 1. Abre a conexão e cria as tabelas se necessário antes de iniciar o menu
    conexao = criar_conexao()
    cursor = conexao.cursor()
    criar_bd(cursor)
    conexao.commit()

    # 2. Passa o cursor ativo para a classe de serviços
    servico = ClienteServico(cursor=cursor)

    while True:
        match menu():
            case "1":
                servico.criar_cliente()
                conexao.commit() # Efetiva e grava permanentemente o novo cliente no arquivo SQLite
            case "2":
                servico.listar_clientes()
            case "0":
                break
            case _:
                print("\n@@@ Operação inválida, por favor selecione novamente a operação desejada. @@@")

    # 3. Fecha os recursos de maneira limpa ao encerrar a aplicação
    cursor.close()
    conexao.close()


if __name__ == "__main__":
    main()
