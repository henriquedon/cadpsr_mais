# CadPSR+

## Sobre

Prova de conceito desenvolvida com a finalidade de simular a integração do Cadastro de Pessoas em situação de rua no Brasil, conforme o tema norteador do Projeto Integrador 2 (1ºSEM/2022). Este software se baseia em: framework web; banco de dados; uso de APIS; script web; nuvem; acessibilidade; testes; e sistema de controle de versão. E implementa novas funcionalidades e melhorias, a partir da refatoração de código de aplicação web construída em Projeto Integrador anterior.


## Tecnologias Utilizadas

### Back-end

- Python 3.10
- Flask
- Flask Login
- Flask Migrate
- Flask SQLAlchemy
- Git
- Gunicorn
- Jinja2
- Pendulum
- PostgreSQL
- Psycopg2


### Front-end

- Bootstrap 5
- JQuery
- Jquery Mask
- Javascript


## Funcionalidades

- Criação e edição de Cadastro de Pessoas em situação de rua;
- Criação e edição de Cadastro de Colaboradores;
- Impressão e geração de PDF, via Browser, do Cadastro de Pessoas em situação de rua;
- Geração de Relatório referente aos atendimentos realizados no dia;
- Geração de Relatório a partir de data específica;
- Redefinição de senha;
- Log de acesso;
- Testes automatizados;
- Script para geração de dados (fictícios) para fins de simulação da prova de conceito.


## Instruções para executar o projeto

```bash
### o exemplo abaixo se baseia em Linux:
### crie um diretório com nome que preferir e em seguida entre nele
### clone o repositório
git clone https...

### com o ambiente virtual, de sua preferência, ativado, instale as depedências (nesse exemplo estou utilizano pip + venv):
pip install -r requirements.txt

### crie um arquivo oculto chamado '.flaskenv':
touch .flaskv

### com um editor de sua preferência digite e salve o arquivo contendo os seguintes comandos:
export FLASK_APP=main.py
export FLASK_ENV=development


### execute os comandos abaixo para criar o banco de dados e fazer a 1ª migração:
flask db init
flask db migrate -m 'digite aqui uma mensagem se desejar'
flask db upgrade

### utilize o script 'testes_e_geracao_de_dados.py':
python3 testes_e_geracao_de_dados.py

### escolha a opção:
1 - inicia os testes em modo Desenvolvedor(a);
```

O script criará as entidades, os colaboradores do sistema e as pessoas (todos com dados fictícios) para simular o ambiente do ecossistema proposto.

### Login e Senha do desenvolvedor:

login: dev@dev
senha: teste

Para executar a aplicação execute o comando:

```bash
flask run
```

No navegador de sua preferência acesse o endereço: http://127.0.0.1:5000/login


## Desenvolvido por Henrique D.
