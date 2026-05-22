import textwrap
from bd import criar_conexao, criar_bd
from servico import BancoServico


def menu():
    menu = """\n
    ================ MENU ================
    [1]\tDepositar
    [2]\tSacar
    [3]\tExtrato
    [4]\tNovo cliente
    [5]\tListar clientes
    [6]\tNova conta
    [7]\tListar contas
    [0]\tSair
    => """
    return input(textwrap.dedent(menu))


def main():
    conexao = criar_conexao()
    cursor = conexao.cursor()
    criar_bd(cursor)
    conexao.commit()

    servico = BancoServico(cursor=cursor)

    while True:
        opcao = menu()

        if opcao == "1":
            servico.depositar()
            conexao.commit()
        elif opcao == "2":
            servico.sacar()
            conexao.commit()
        elif opcao == "3":
            servico.emitir_extrato()
        elif opcao == "4":
            servico.criar_cliente()
            conexao.commit()
        elif opcao == "5":
            servico.listar_clientes()
        elif opcao == "6":
            servico.criar_conta()
            conexao.commit()
        elif opcao == "7":
            servico.listar_contas()
        elif opcao == "0":
            break
        else:
            print("\n@@@ Operação inválida, por favor selecione novamente a operação desejada. @@@")

    cursor.close()
    conexao.close()


if __name__ == "__main__":
    main()
