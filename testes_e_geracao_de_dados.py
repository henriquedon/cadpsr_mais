from testes.testes_cadpsr_mais import testes_basicos

while True:
    print()
    print('CADPSR+ | Versão Final')
    print('TESTE AUTOMATIZADO\n')
    print('Escolha uma das opções abaixo:\n')
    print(' 0 - sai desse script de testes;')
    print(' 1 - inicia os testes em modo Desenvolvedor(a);')
    print(' 2 - inicia os testes em modo Deploy.\n')
    print('Obs.: informe apenas um número.\n')

    opcao = input('Informe o Tipo de Teste ou 0 para sair: ')
    print()

    if opcao not in '120':
        print()
        print('Digite apenas 0, 1, ou 2')
    else:

        if opcao == '0':
            print('Você optou por não iniciar os testes.')
            break

        elif opcao == '1':
            print('Você optou por iniciar os testes em MODO DESENVOLVEDOR(A).')
            print()
            testes_basicos(opcao)
            break

        elif opcao == '2':
            print('Você optou por iniciar os testes em MODO DEPLOY.')
            print()
            testes_basicos(opcao)
            break
