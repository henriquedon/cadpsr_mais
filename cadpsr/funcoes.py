

def ativa_nav_link(pagina):
    dicionario = {'home': {'active': '',
                         'aria-current': ''},
                'atendimentos': {'active': '',
                                 'aria-current': ''},
                'pessoas': {'active': '',
                            'aria-current': ''},
                'colaboradores': {'active': '',
                                  'aria-current': ''},
                'entidades': {'active': '',
                              'aria-current': ''},
                'perfil': {'active': '',
                           'aria-current': ''}
                }
    #dicionario = deepcopy(dicionario_links)
    if pagina == 'home':
        dicionario['home']['active'] = ' active'
        dicionario['home']['aria-current'] = ' aria-current="page"'

    elif pagina == 'atendimentos':
        dicionario['atendimentos']['active'] = ' active'
        dicionario['atendimentos']['aria-current'] = ' aria-current="page"'

    elif pagina == 'pessoas':
        dicionario['pessoas']['active'] = ' active'
        dicionario['pessoas']['aria-current'] = ' aria-current="page"'

    elif pagina == 'colaboradores':
        dicionario['colaboradores']['active'] = ' active'
        dicionario['colaboradores']['aria-current'] = ' aria-current="page"'

    elif pagina == 'entidades':
        dicionario['entidades']['active'] = ' active'
        dicionario['entidades']['aria-current'] = ' aria-current="page"'

    else:
        dicionario['perfil']['active'] = ' active'
        dicionario['perfil']['aria-current'] = ' aria-current="page"'
    return dicionario


def formata_data(data_hora):
    if data_hora:
        data_hora = data_hora.split('-')
        data_hora = f'{data_hora[2]}/{data_hora[1]}/{data_hora[0]} {data_hora[3]}:{data_hora[4]}:{data_hora[5]}'
    else:
        data_hora = ''
    return data_hora


def formata_data_br(data):
    if data:
        data = data.split('-')
        data = f'{data[2]}/{data[1]}/{data[0]}'
    else:
        data = ''
    return data


def limpa_doc(doc):
    if doc:
        doc = ''.join(digito for digito in doc if digito not in '.- ()')
    else:
        doc = ''
    return doc


def lista_para_str(lista):
    string = ''
    for i in lista:
        string += str(i)
    return string


def mascara_tel(numero):
    if numero:
        if len(numero) == 10:
            mascara = f'{numero[0]}{numero[1]} {numero[2]}{numero[3]}{numero[4]}{numero[5]} {numero[6]}{numero[7]}{numero[8]}{numero[9]}'
        else:
            mascara = f'{numero[0]}{numero[1]} {numero[2]}{numero[3]}{numero[4]}{numero[5]}{numero[6]} {numero[7]}{numero[8]}{numero[9]}{numero[10]}'
    else:
        mascara = ''
    return mascara


def mascara_cpf(cpf):
    cpf = f'{cpf[0:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:11]}'
    return cpf


def mascara_doc(doc, casas, agrupamento):
    if doc:
        lista = list(doc)
        mascara = ''
        contador = 1
        for i in range(agrupamento):

            for v in range(casas):
                mascara += lista.pop(0)
            if contador < agrupamento:
                mascara += ' '
                contador += 1
    else:
        mascara = ''
    return mascara


def remove_aspas(string):
    nova_string = ''
    for caractere in string:
        if caractere == "'" or caractere == '"':
            continue
        else:
            nova_string += caractere
    return nova_string
