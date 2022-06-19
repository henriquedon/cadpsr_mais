def testes_basicos(tipo_de_teste):
    from random import shuffle, randint

    from secrets import token_hex

    print('###TESTES DE IMPORTAÇÕES\n')

    try:
        from cadpsr import db
        print(f'Teste - import db:{"sucesso".upper():.>62}!')
    except Exception as erro:
        print(f'Teste - import db:{"falhou".upper():.>62}!')
        print(f'Erro: {erro}')

    try:
        from cadpsr.models import Colaborador, Entidade, Atendimento, Pessoa, Acesso
        print(f'Teste - import models:{"sucesso".upper():.>58}!')
    except Exception as erro:
        print(f'Teste - import models:{"falhou".upper():.>58}!')
        print(f'Erro: {erro}')

    try:
        from pendulum import now
        print(f'Teste - import pendulum NOW: {"sucesso".upper():.>51}!')
    except Exception as erro:
        print(f'Teste - import pendulum NOW: {"falhou".upper():.>51}!')
        print(f'Erro: {erro}')

    try:
        from werkzeug.security import generate_password_hash, check_password_hash
        print(f'Teste - import werkzeug.security:{"sucesso".upper():.>47}!')
    except Exception as erro:
        print(f'Teste - import werkzeug.security:{"falhou".upper():.>47}!')
        print(f'Erro: {erro}')


    def gera_cpf():
        cpf = '100000090'
        lista_cpf =[]
        for v in range(100):
    	       lista_cpf.append(f'{cpf}{v:02}')

        for v in range(42):
            shuffle(lista_cpf)

        return lista_cpf


    def gera_nomes():
        def importa_arquivo(nome_arquivo):
            #ABRINDO ARQUIVO E DECLARANDO OBJETOS
            arquivo = open(nome_arquivo, 'r')
            linha = []
            lista = []
            #IMPORTANDO CONTEÚDO E FECHANDO O DOCUMENTO!
            for linha_percorrida in arquivo.readlines():
                if linha_percorrida[0] == '!' or linha_percorrida[0] == '\n':
                    continue
                else:
                    linha = []
                    linha_percorrida = linha_percorrida.split()
                    for palavra in linha_percorrida:
                        linha.append(palavra)
                    lista.append(linha)
            arquivo.close()
            return lista

        nomes = importa_arquivo('testes/nomes.txt')
        sobrenomes_brasileiros = importa_arquivo('testes/sobrenomes_brasileiros.txt')
        sobrenomes_italianos = importa_arquivo('testes/sobrenomes_italianos.txt')
        sobrenomes_japoneses = importa_arquivo('testes/sobrenomes_japoneses.txt')

        for i in range(41):
            shuffle(nomes)
            shuffle(sobrenomes_japoneses)
            shuffle(sobrenomes_italianos)
            shuffle(sobrenomes_brasileiros)

        lista_nomes_completos = []

        for v in range(100):
            nome_completo = []
            nome_completo.append(f'{nomes[v][0]} {sobrenomes_japoneses[v][0]} {sobrenomes_italianos[v][0]} {sobrenomes_brasileiros[v][0]}')
            lista_nomes_completos.append(nome_completo)

        return lista_nomes_completos


    def formata_data(data_hora):
        data_hora = data_hora.split('-')
        data_hora = f'{data_hora[2]}/{data_hora[1]}/{data_hora[0]} {data_hora[3]}:{data_hora[4]}:{data_hora[5]}'

        return data_hora


    print()
    print()
    print('###TESTE: GERAÇÃO DE ENTIDADES\n')
    print('Esse teste cobre: classes, objetos, configurações e persistência de dados.')
    print()
    try:
        #Geração de ENTIDADES - Banco de Dados
        entidades = {0: {'status': 'ATIVO', 'nome': 'Desenvolvedora CadPSR+', 'iniciativa': '2', 'tipo': '0', 'natureza': '0', 'email': 'cadpsr@cadpsr', 'telefone': '00000010', 'endereco': 'Av. Fabrica de Codigo, nº 1', 'cep': '00000010', 'cidade': '2'},
                     1: {'status': 'ATIVO', 'nome': 'Centro POP Santo André', 'iniciativa': '1', 'tipo': '2', 'natureza': '4', 'email': 'centropop.santoandre@cadpsr', 'telefone': '00000020', 'endereco': 'Av. Centro Santo André, nº 21', 'cep': '00000020', 'cidade': '1'},
                     2: {'status': 'ATIVO', 'nome': 'Centro POP São Bernardo do Campo', 'iniciativa': '1', 'tipo': '2', 'natureza': '4', 'email': 'centropop.saobernardocampo@cadpsr', 'telefone': '000000030', 'endereco': 'Av. Paço Municipal, nº 31', 'cep': '00000030', 'cidade': '2'},
                     3: {'status': 'ATIVO', 'nome': 'CRAS Santo André - Centro', 'iniciativa': '1', 'tipo': '3', 'natureza': '4', 'email': 'cras.santoandre@cadpsr', 'telefone': '000000021', 'endereco': 'Av. Centro Santo André, nº 22', 'cep': '00000020', 'cidade': '1'},
                     4: {'status': 'ATIVO', 'nome': 'CRAS São Bernardo do Campo - Centro', 'iniciativa': '1', 'tipo': '3', 'natureza': '4', 'email': 'cras.saobernardocampo@cadpsr', 'telefone': '000000031', 'endereco': 'Av. Paço Municipal, nº 32', 'cep': '00000030', 'cidade': '2'},
                     5: {'status': 'ATIVO', 'nome': 'CREAS Santo André', 'iniciativa': '1', 'tipo': '4', 'natureza': '4', 'email': 'creas.santoandre@cadpsr', 'telefone': '000000022', 'endereco': 'Av. Centro Santo André, nº 23', 'cep': '00000020', 'cidade': '1'},
                     6: {'status': 'ATIVO', 'nome': 'CREAS São Bernardo do Campo', 'iniciativa': '1', 'tipo': '4', 'natureza': '4', 'email': 'creas.saobernardocampo@cadpsr', 'telefone': '000000032', 'endereco': 'Av. Paço Municipal, nº 33', 'cep': '00000030', 'cidade': '2'},
                     9: {'status': 'ATIVO', 'nome': 'Associação Cidadania para com todos', 'iniciativa': '2', 'tipo': '1', 'natureza': '4', 'email': 'associacao.cidadania@cadpsr', 'telefone': '00000040', 'endereco': 'Rua Fraternidade e Esperança, nº 40', 'cep': '00000040', 'cidade': '1'},
                     7: {'status': 'ATIVO', 'nome': 'Associação Fraternidade Luz Solidária', 'iniciativa': '2', 'tipo': '1', 'natureza': '4', 'email': 'associacao.fraternidade@cadpsr', 'telefone': '00000050', 'endereco': 'Av Moonwalker, nº 50', 'cep': '00000050', 'cidade': '2'},
                     8: {'status': 'ATIVO', 'nome': 'Fundação Lutas & Diversidades', 'iniciativa': '2', 'tipo': '5', 'natureza': '4', 'email': 'fundacao.lutas@cadpsr', 'telefone': '00000060', 'endereco': 'Rua Das Funções, nº 60', 'cep': '00000060', 'cidade': '1'},
                     10: {'status': 'ATIVO', 'nome': 'Fundação Sociedade Inclusiva', 'iniciativa': '2', 'tipo': '5', 'natureza': '4', 'email': 'fundacao.sociedade@cadpsr', 'telefone': '00000070', 'endereco': 'Estrada Robervaldo Falcão, nº 70', 'cep': '00000070', 'cidade': '2'},
                     }

        for i in range(len(entidades)):
            data_hora = now('America/Sao_Paulo').format('YYYY-MM-DD-HH-mm-ss-SSSSSS')
            entidade = Entidade(status=entidades[i]['status'],
                                nome=entidades[i]['nome'],
                                iniciativa=entidades[i]['iniciativa'],
                                tipo=entidades[i]['tipo'],
                                natureza=entidades[i]['natureza'],
                                email=entidades[i]['email'],
                                telefone=entidades[i]['telefone'],
                                endereco=entidades[i]['endereco'],
                                cep=entidades[i]['cep'],
                                cidade=entidades[i]['cidade'],
                                uf='sp',
                                data_criacao= data_hora,
                                criado_por='Desenvolvedora CadPSR+',
                                )
            db.session.add(entidade)
            db.session.commit()
            print(f'Entidade de nº {i:02} adicionada com sucesso')
        print()
        print(f'Teste - Geração de Entidades:{"sucesso".upper():.>51}!')
    except Exception as erro:
        print(f'Teste - Geração de Entidades:{"falhou".upper():.>51}!')
        print(f'Erro: {erro}')

    print()
    print()
    print('###TESTE: GERAÇÃO DE COLABORADORES\n')
    print('Esse teste cobre: classes, objetos, configurações e persistência de dados.')
    print()
    try:
        data_nasc = '1990-01-01'

        colaboradores = [['ATIVO', 'Desenvolvedor CadPSR+', '88888888801', data_nasc , 'dev@dev', '2', '0', '0', data_hora, 'Desenvolvedor CadPSR+'],
                         ['ATIVO', 'Gerente Teste CadPSR+', '88888888803', data_nasc ,'dev.gerente@dev', '2', '4', '0', data_hora, 'Desenvolvedor CadPSR+'],
                         ['ATIVO', 'Colaborador Teste CadPSR+', '88888888805', data_nasc ,'dev.colaborador@dev', '2', '5', '0', data_hora, 'Desenvolvedor CadPSR+'],
                         ['ATIVO', 'Dona Ivone Lara', '22222222201', data_nasc, 'dona@cadpsr', '1', '4', '1', data_hora, 'Desenvolvedor CadPSR+'],
                         ['ATIVO', 'Hipatia de Alexandria', '22222222203', data_nasc, 'hipatia@cadpsr', '1', '4', '2', data_hora, 'Desenvolvedor CadPSR+'],
                         ['ATIVO', 'Mauro Matheus dos Santos', '22222222205', data_nasc, 'mauro@cadpsr', '1', '4', '3', data_hora, 'Desenvolvedor CadPSR+'],
                         ['ATIVO', 'Grace Hopper', '22222222207', data_nasc, 'grace@cadpsr', '1', '4', '4', data_hora, 'Desenvolvedor CadPSR+'],
                         ['ATIVO', 'Paulo Freire', '22222222209', data_nasc, 'paulo@cadpsr', '1', '4', '5', data_hora, 'Desenvolvedor CadPSR+'],
                         ['ATIVO', 'Luiz Gonzaga', '22222222211', data_nasc, 'luiz@cadpsr', '1', '4', '6', data_hora, 'Desenvolvedor CadPSR+'],
                         ['ATIVO', 'Chico Mendes', '33333333301', data_nasc, 'chico@cadpsr', '1', '5', '1', data_hora, 'Desenvolvedor CadPSR+'],
                         ['ATIVO', 'Nina Simone', '33333333303', data_nasc, 'nina@cadpsr', '1', '5', '2', data_hora, 'Desenvolvedor CadPSR+'],
                         ['ATIVO', 'Ada Lovelace', '33333333305', data_nasc, 'ada@cadpsr', '1', '5', '3', data_hora, 'Desenvolvedor CadPSR+'],
                         ['ATIVO', 'Tupac Shakur', '33333333307', data_nasc, 'tupac@cadpsr', '1', '5', '4', data_hora, 'Desenvolvedor CadPSR+'],
                         ['ATIVO', 'Chadwick Boseman', '33333333309', data_nasc, 'chadwick@cadpsr', '1', '5', '5', data_hora, 'Desenvolvedor CadPSR+'],
                         ['ATIVO', 'Sebastião Maia', '33333333311', data_nasc, 'sebastiao@cadpsr', '1', '5', '6', data_hora, 'Desenvolvedor CadPSR+'],
                         ['ATIVO', 'Nelson Mandela', '44444444401', data_nasc, 'nelson@cadpsr', '2', '4', '7', data_hora, 'Desenvolvedor CadPSR+'],
                         ['ATIVO', 'Martin Luther King Jr.', '44444444403', data_nasc, 'martin@cadpsr', '2', '5', '7', data_hora, 'Desenvolvedor CadPSR+'],
                         ['ATIVO', 'Fred Hampton', '55555555501', data_nasc, 'fred@cadpsr', '2', '4', '8', data_hora, 'Desenvolvedor CadPSR+'],
                         ['ATIVO', 'Alexander Supertramp', '55555555503', data_nasc, 'alexander@cadpsr', '2', '5', '8', data_hora, 'Desenvolvedor CadPSR+'],
                         ['ATIVO', 'Mahatma Ghandi', '66666666601', data_nasc, 'mahatma@cadpsr', '2', '4', '9', data_hora, 'Desenvolvedor CadPSR+'],
                         ['ATIVO', 'Carolina de Jesus', '66666666603', data_nasc, 'carolina@cadpsr', '2', '5', '9', data_hora, 'Desenvolvedor CadPSR+'],
                         ['ATIVO', 'Milton Santos', '77777777701', data_nasc, 'milton@cadpsr', '2', '4', '10', data_hora, 'Desenvolvedor CadPSR+'],
                         ['ATIVO', 'Emma Goldman', '77777777703', data_nasc, 'emma@cadpsr', '2', '5', '10', data_hora, 'Desenvolvedor CadPSR+'],
                         ]
        senha_padrao = 'teste' # senha padrão correspondente ao MODO DESENVOLVEDOR
        senha = generate_password_hash(senha_padrao)
        for i in range(len(colaboradores)):
            if tipo_de_teste == '2':
                if i == 0:
                    print()
                    print('DEFINIÇÃO DE SENHA PARA CONTA DE DESENVOLVEDOR(A)')
                    print()
                    print('ATENÇÃO: Você escolheu fazer os testes em MODO DEPLOY!')
                    print('INFORME UMA SENHA FORTE.')
                    print()
                    senha = input('Informe a senha de Desenvolvedor(a) CadPSR+: ')
                    senha = generate_password_hash(senha) # hash de senha expressa entre parênteses!
                    print()
                else: # para os demais colaboradores a senha será gerada automaticamente!
                    senha = token_hex(64) # senha marota -- oremos!
                    senha = generate_password_hash(senha) # geração de hash de senha expressa entre parênteses!

            data_hora = now('America/Sao_Paulo').format('YYYY-MM-DD-HH-mm-ss-SSSSSS')
            colaborador = Colaborador(status=colaboradores[i][0],
                                      nome_civil=colaboradores[i][1],
                                      nome_social=colaboradores[i][1],
                                      cpf=colaboradores[i][2],
                                      data_nascimento=data_nasc,
                                      email=colaboradores[i][4],
                                      senha=senha,
                                      iniciativa=colaboradores[i][5],
                                      tipo_clb=colaboradores[i][6],
                                      lotacao=colaboradores[i][7],
                                      data_criacao=data_hora,
                                      criado_por='Desenvolvedor CadPSR+',
                                      )
            db.session.add(colaborador)
            db.session.commit()
            print(f'Colaborador de nº {i:02} adicionado com sucesso')
        print()
        print(f'Teste - Geração de Colaboradores:{"sucesso".upper():.>47}!')
    except Exception as erro:
        print(f'Teste - Geração de Colaboradores:{"falhou".upper():.>47}!')
        print(f'Erro: {erro}')

    print()
    print()
    print('###TESTE: GERAÇÃO DE PESSOAS\n')
    print('Esse teste cobre: classes, objetos, configurações e persistência de dados.')
    print()
    try:
        data_nasci = '1990-07-07'
        nomes = gera_nomes()
        lista_cpf = gera_cpf()
        lista_id = [9,10,11,12,13,14,16,18,20,22]
        contador = 0
        for id in lista_id:
            colaborador = Colaborador.query.get(id)
            if colaborador.lotacao == '1':
                cidade_atual = '1'
            else:
                cidade_atual = '2'
            for i in range(len(lista_id)):
                data_hora = now('America/Sao_Paulo').format('YYYY-MM-DD-HH-mm-ss-SSSSSS')
                pessoa = Pessoa(status='ATIVO',
                                nome_civil=nomes[contador][0],
                                nome_social=nomes[contador][0],
                                cpf=lista_cpf[contador],
                                data_nascimento=data_nasci,
                                cidade_atual= cidade_atual,
                                entidade_geradora= colaborador.lotacao,
                                entidade_referencia= colaborador.lotacao,
                                data_criacao=data_hora,
                                criado_por=colaborador.nome_civil,
                                apelido='',
                                email='',
                                telefone='',
                                celular='',
                                etnia='6',
                                sexo='3',
                                orientacao_sexual='6',
                                identidade_genero='5',
                                rg='',
                                rg_dv='',
                                rg_uf='sp',
                                rg_orgao_emissor='',
                                titulo_eleitor='',
                                titulo_zona='',
                                titulo_secao='',
                                cns='',
                                nis='',
                                certidao_nascimento='',
                                naturalidade='',
                                nacionalidade='',
                                crnm_rnm='',
                                crnm_filiacao_a='',
                                crnm_filiacao_b='',
                                crnm_validade='',
                                crnm_classificacao='',
                                crnm_domicilio='',
                                crnm_emissao='',
                                questao_11 = '',
                                obs_psr=''
                                )
                db.session.add(pessoa)
                db.session.commit()
                pessoa = Pessoa.query.get(contador + 1)
                atendimento = Atendimento(data_atendimento=data_hora,
                                          id_pessoa=pessoa.id,
                                          nome_pessoa=pessoa.nome_civil,
                                          tipo_atendimento='2',
                                          id_colaborador=colaborador.id,
                                          nome_colaborador=colaborador.nome_civil,
                                          entidade_geradora=colaborador.lotacao,
                                          obs_atendimento=pessoa.obs_psr or '',
                                         )
                db.session.add(atendimento)
                db.session.commit()
                print(f'Pessoa de nº {contador + 1:02} adicionada com sucesso')
                contador += 1
        print()
        print(f'Teste - Geração de Pessoas:{"sucesso".upper():.>53}!')
    except Exception as erro:
        print(f'Erro: {erro}')
        print(f'Teste - Geração de Pessoas:{"falhou".upper():.>53}!')

    print()
    print()
    print('###TESTE: CREDENCIAIS DESENVOLVEDOR\n')
    print('Esse teste cobre: classes, objetos, configurações e consulta de dados.')
    print()
    #Teste de Exibição de credenciais de desenvolvedor
    try:
        if tipo_de_teste == '1':
            colaborador = Colaborador.query.get(1)
            email = colaborador.email
            print(f'Teste - Credenciais Desenvolvedor:{"sucesso".upper():.>46}!\n')
            print(f'Login: {email}')
            print(f'Senha Padrão: {senha_padrao}\n')
            print('OBS.: a SENHA DE TODOS colaboradores é IGUAL a senha do desenvolvedor.')
            print('ALERTA: em casos reais de deploy, NÃO UTILIZAR SENHA PADRÃO!')
        else:
            colaborador = Colaborador.query.get(1)
            email = colaborador.email
            print(f'Teste - Credenciais Desenvolvedor:{"sucesso".upper():.>46}!\n')
            print(f'Login: {colaborador.email}\n')
            print('ATENÇÃO: cada Colaborador(a) possui uma senha (forte) gerada automaticamente.')
    except Exception as erro:
        print(f'Teste - Credenciais Desenvolvedor:{"falhou".upper():.>46}!')
        print(f'Erro: {erro}')

    print()
    print('FIM DOS TESTES!')
