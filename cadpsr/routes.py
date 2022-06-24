import os, webbrowser

from datetime import timedelta
from secrets import token_hex

from flask import (Flask, flash, redirect, request, render_template, session,
    url_for)

from flask_login import login_user, logout_user, current_user, login_required

from pendulum import now

from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename

from cadpsr import app, db
from cadpsr.dicionarios import (atendimento_cad_dic,
    colaborador_cad_dic, pessoa_cad_dic, entidade_cad_dic, questionario,
    questionario_pessoa_estrangeira)
from cadpsr.funcoes import (formata_data, formata_data_br, lista_para_str,
    limpa_doc, mascara_cpf, mascara_doc, mascara_tel, remove_aspas, ativa_nav_link)
from cadpsr.models import Acesso, Atendimento, Colaborador, Pessoa, Entidade


cadpsr_versao = 'Versão 1.1.1'


@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=20)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':

        pode_naum = [None, '', ' ']
        email = request.form.get('email')
        senha = request.form.get('senha')

        if email == pode_naum or len(email) == 0 or senha == pode_naum or len(senha) == 0:
            flash('É necessário preencher os campos E-mail e Senha.', category='error')
            return redirect('login')

        colaborador = Colaborador.query.filter_by(email=email).first()

        if colaborador is None or not colaborador.verifica_senha_hash(senha):
            flash('E-mail/Senha inválido(a)!', category='error')
            return redirect(url_for('login'))

        acesso = Acesso(data_hora=now(
                            'America/Sao_Paulo').format('YYYY-MM-DD-HH-mm-ss-SSSSSS'),
                        id_clb=colaborador.id,
                        nome_clb=colaborador.nome_civil,
                        status_clb=colaborador.status,
                        lotacao_clb=colaborador.lotacao
                        )
        db.session.add(acesso)
        db.session.commit()

        login_user(colaborador)
        if current_user.status == 'INICIO' or current_user.status == 'REDEF':
            flash(
                'Para acessar outras áreas do sistema, você precisa alterar sua senha.', category='error')
            return redirect(url_for('perfil'))
        proxima_pagina = request.args.get('next')
        if not proxima_pagina or url_parse(proxima_pagina).netloc != '':
            proxima_pagina = url_for('index')
        return redirect(url_for('index'))

    return render_template('login.html', cadpsr_versao=cadpsr_versao,
                                         titulo='Login - CadPSR',
                                         )


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/relatorio', methods=['GET', 'POST'])
@login_required
def relatorio():
    if current_user.status == 'INICIO' or current_user.status == 'REDEF':
        flash('Para acessar outras áreas do sistema, você precisa alterar sua senha!', category='error')
        return redirect('perfil')
    if request.method == 'GET':
        flash('Acesso negado.', category='error')
        return redirect('atendimentos')

    if request.method == 'POST':
        if request.form.get('gerar_relatorio_dia') == 'relatorio_dia':
            data_relatorio = now('America/Sao_Paulo').format('YYYY-MM-DD')
            titulo = 'Relatório Dia - CadPSR+'
        else:
            data_relatorio = request.form.get('data_relatorio')
            titulo = 'Relatório Data Específica - CadPSR+'

    atendimentos = Atendimento.query.filter_by(
        entidade_geradora=current_user.lotacao).filter(
            Atendimento.data_atendimento.like(
                '%' + data_relatorio + '%')).all()

    if not atendimentos:
        flash('Não há atendimento(s) correspondente(s) ao Dia Atual ou à Data Informada.')
        return redirect('atendimentos')

    qtd_pessoas = []
    for atendimento in atendimentos:
        qtd_pessoas.append(atendimento.id_pessoa)

    if len(atendimentos) % 11 == 0:
        paginas = len(atendimentos) // 11
    else:
        paginas = (len(atendimentos) // 11) + 1

    data_relatorio = formata_data_br(data_relatorio)
    entidade_nome = current_user.lotacao
    qtd_atendimentos = len(atendimentos)
    qtd_pessoas = len(set(qtd_pessoas))

    return render_template('impressao_relatorio.html', atendimentos=atendimentos,
                                                       atendimento_cad_dic=atendimento_cad_dic,
                                                       data_relatorio=data_relatorio,
                                                       entidade_cad_dic=entidade_cad_dic,
                                                       entidade_nome=entidade_nome,
                                                       formata_data=formata_data,
                                                       qtd_atendimentos=qtd_atendimentos,
                                                       qtd_pessoas=qtd_pessoas,paginas=paginas,
                                                       titulo=titulo,
                                                       )


@app.route('/cadastro', methods=['GET', 'POST'])
@login_required
def cadastro():
    if current_user.status == 'INICIO' or current_user.status == 'REDEF':
        flash('Para acessar outras áreas do sistema, você precisa alterar sua senha!', category='error')
        return redirect('perfil')

    if request.method == 'GET':
        flash('Acesso negado.', category='error')
        return redirect('pessoas')

    if request.method == 'POST':
        pessoa_id = request.form.get('imprimir_cadastro')
        pessoa = Pessoa.query.get(pessoa_id)

    if not pessoa:
        flash('Cadastro não localizado para impressão!')
        return redirect('pessoas')

    data_impressao = formata_data(now('America/Sao_Paulo').format('YYYY-MM-DD-HH-mm-ss-SSSSSS'))
    entidade_nome = current_user.lotacao
    titulo = 'Impressão de Cadastro - CadPSR+'

    return render_template('impressao_cadastro.html',data_impressao=data_impressao,
                                                     entidade_cad_dic=entidade_cad_dic,
                                                     entidade_nome=entidade_nome,
                                                     formata_data=formata_data,
                                                     formata_data_br=formata_data_br,
                                                     mascara_cpf=mascara_cpf,
                                                     mascara_doc=mascara_doc,
                                                     mascara_tel=mascara_tel,
                                                     pessoa=pessoa,
                                                     pessoa_cad_dic=pessoa_cad_dic,
                                                     titulo=titulo,
                                                     )


@app.route('/')
@app.route('/index')
@login_required
def index():
    if current_user.status == 'INICIO' or current_user.status == 'REDEF':
        flash('Para acessar outras áreas do sistema, você precisa alterar sua senha!', category='error')
        return redirect('perfil')

    busca = None
    dict_ativa = ativa_nav_link('home')
    tipo_de_consulta = None
    titulo = 'Home - CadPSR+'

    return render_template("index.html", titulo='Home :: CadPSR+', cadpsr_versao=cadpsr_versao,
                                                                   colaborador_cad_dic=colaborador_cad_dic,
                                                                   dict_ativa=dict_ativa,
                                                                   entidade_cad_dic=entidade_cad_dic,
                                                                   )


@app.route('/atendimentos', methods=['GET', 'POST'])
@login_required
def atendimentos():
    if current_user.status == 'INICIO' or current_user.status == 'REDEF':
        flash('Para acessar outras áreas do sistema, você precisa alterar sua senha!', category='error')
        return redirect('perfil')

    busca = None
    data_relatorio = formata_data_br(now('America/Sao_Paulo').format('YYYY-MM-DD'))
    dict_ativa = ativa_nav_link('atendimentos')
    tipo_consulta = None
    titulo = 'Consulta de Atendimentos - CadPSR+'

    if request.method == 'POST':
        dado_consultado = remove_aspas(request.form.get("""dado_consultado"""))

        if dado_consultado == '' or None:
            return redirect(url_for('atendimentos'))
        else:
            busca = True
            tipo_consulta = request.form.get("""tipo_consulta""")

        if tipo_consulta == 'id_pessoa':
            pessoa = Pessoa.query.get(dado_consultado)

            if pessoa:
                pessoa_cpf = mascara_cpf(pessoa.cpf)
                pessoa_entidade_geradora = pessoa.entidade_geradora
                pessoa_id = pessoa.id
                pessoa_nome = pessoa.nome_civil

                return render_template('atendimentos.html', atendimento_cad_dic=atendimento_cad_dic,
                                                            busca=busca,
                                                            colaborador_cad_dic=colaborador_cad_dic,
                                                            data_relatorio=data_relatorio,
                                                            dict_ativa=dict_ativa,
                                                            entidade_cad_dic=entidade_cad_dic,
                                                            pessoa_cpf=pessoa_cpf,
                                                            pessoa_entidade_geradora=pessoa_entidade_geradora,
                                                            pessoa_id=pessoa_id,
                                                            pessoa_nome=pessoa_nome,
                                                            tipo_consulta=tipo_consulta,
                                                            titulo=titulo,
                                                            )
            else:
                flash('Não há Atendimento referente ao ID informado.', category='error')
                return redirect('atendimentos')
        else:
            atendimento = Atendimento.query.get(dado_consultado)
            if atendimento:
                entidade = Entidade.query.filter_by(nome=entidade_cad_dic['entidade'][atendimento.entidade_geradora]).first()
                pessoa = Pessoa.query.get(atendimento.id_pessoa)

                data_atendimento = formata_data(atendimento.data_atendimento)
                entidade_iniciativa = entidade.iniciativa
                pessoa_cpf = mascara_cpf(pessoa.cpf)
                pessoa_entidade_geradora = pessoa.entidade_geradora
                pessoa_id = pessoa.id
                pessoa_nome = pessoa.nome_civil

                return render_template('atendimentos.html', atendimento=atendimento,
                                                            atendimento_cad_dic=atendimento_cad_dic,
                                                            busca=busca,
                                                            colaborador_cad_dic=colaborador_cad_dic,
                                                            data_atendimento=data_atendimento,
                                                            data_relatorio=data_relatorio,
                                                            dict_ativa=dict_ativa,
                                                            entidade_iniciativa=entidade_iniciativa,
                                                            entidade_cad_dic=entidade_cad_dic,
                                                            pessoa_cpf=pessoa_cpf,
                                                            pessoa_entidade_geradora=pessoa_entidade_geradora,
                                                            pessoa_id=pessoa_id,
                                                            pessoa_nome=pessoa_nome,
                                                            tipo_consulta=tipo_consulta,
                                                            titulo=titulo,
                                                            )
            else:
                flash('Não há Atendimento referente ao ID informado.', category='error')
                return redirect('atendimentos')

    return render_template('atendimentos.html', atendimento_cad_dic=atendimento_cad_dic,
                                                busca=busca,
                                                colaborador_cad_dic=colaborador_cad_dic,
                                                criado_por=current_user.nome_civil,
                                                data_relatorio=data_relatorio,
                                                dict_ativa=dict_ativa,
                                                entidade_cad_dic=entidade_cad_dic,
                                                tipo_consulta=tipo_consulta,
                                                titulo=titulo,
                                                )


@app.route('/atendimentos_cadpsr/<psr_id>', methods=['GET', 'POST'])
@login_required
def atendimentos_cadpsr(psr_id):
    if current_user.status == 'INICIO' or current_user.status == 'REDEF':
        flash('Para acessar outras áreas do sistema, você precisa alterar sua senha!', category='error')
        return redirect('perfil')

    atendimentos = Atendimento.query.filter_by(id_pessoa=psr_id).all()
    atendimentos.reverse()

    dict_ativa = ativa_nav_link('atendimentos')
    pessoa = Pessoa.query.get(psr_id)
    heading = 'Histórico de Atendimentos'
    pessoa_cpf = mascara_cpf(pessoa.cpf)
    pessoa_entidade_geradora = pessoa.entidade_geradora
    pessoa_entidade_referencia = pessoa.entidade_referencia
    pessoa_id = pessoa.id
    pessoa_nome = pessoa.nome_civil
    titulo = 'Histórico Todos Atendimentos - CadPSR+'

    return render_template('atendimentos_cadpsr.html', atendimentos=atendimentos,
                                                       atendimento_cad_dic=atendimento_cad_dic,
                                                       colaborador_cad_dic=colaborador_cad_dic,
                                                       dict_ativa=dict_ativa,
                                                       entidade_cad_dic=entidade_cad_dic,
                                                       formata_data=formata_data,
                                                       heading=heading,
                                                       pessoa_cpf=pessoa_cpf,
                                                       pessoa_entidade_geradora=pessoa_entidade_geradora,
                                                       pessoa_entidade_referencia=pessoa_entidade_referencia,
                                                       pessoa_id=pessoa_id,
                                                       pessoa_nome=pessoa_nome,
                                                       titulo=titulo,
                                                       )


@app.route('/atendimentos_entidade/<psr_id>', methods=['GET', 'POST'])
@login_required
def atendimentos_entidade(psr_id):
    if current_user.status == 'INICIO' or current_user.status == 'REDEF':
        flash('Para acessar outras áreas do sistema, você precisa alterar sua senha!', category='error')
        return redirect('perfil')

    atendimentos = Atendimento.query.filter_by(entidade_geradora=current_user.lotacao).filter_by(id_pessoa=psr_id).all()
    atendimentos.reverse()

    dict_ativa = ativa_nav_link('atendimentos')
    pessoa = Pessoa.query.get(psr_id)
    heading = 'Histórico de Atendimento(s) efetuado(s) nessa Entidade'
    pessoa_cpf = mascara_cpf(pessoa.cpf)
    pessoa_entidade_geradora = pessoa.entidade_geradora
    pessoa_entidade_referencia = pessoa.entidade_referencia
    pessoa_id = pessoa.id
    pessoa_nome = pessoa.nome_civil
    titulo = 'Histórico Atendimentos Entidade - CadPSR+'

    return render_template('atendimentos_cadpsr.html', atendimentos=atendimentos,
                                                       atendimento_cad_dic=atendimento_cad_dic,
                                                       colaborador_cad_dic=colaborador_cad_dic,
                                                       dict_ativa=dict_ativa,
                                                       formata_data=formata_data,
                                                       entidade_cad_dic=entidade_cad_dic,
                                                       heading=heading,
                                                       pessoa_cpf=pessoa_cpf,
                                                       pessoa_entidade_geradora=pessoa_entidade_geradora,
                                                       pessoa_entidade_referencia=pessoa_entidade_referencia,
                                                       pessoa_id=pessoa_id,
                                                       pessoa_nome=pessoa_nome,
                                                       titulo=titulo,
                                                       )


@app.route('/colaboradores', methods=['GET', 'POST'])
@login_required
def colaboradores():
    if current_user.status == 'INICIO' or current_user.status == 'REDEF':
        flash('Para acessar outras áreas do sistema, você precisa alterar sua senha!', category='error')
        return redirect('perfil')
    if current_user.tipo_clb == '5':
        flash('Acesso não autorizado!')
        return redirect('/index.html')

    acessos = None
    busca = None
    colaborador = None
    dict_ativa = ativa_nav_link('colaboradores')
    colaboradores = None
    titulo = 'Consulta de Colaboradores - CadPSR+'
    total_colaboradores_entidade = len(Colaborador.query.filter_by(lotacao=current_user.lotacao).all())
    total_colaboradores_cadpsr = len(Colaborador.query.all())

    if request.method == 'POST':
        if request.form.get('dado_consultado') == '' or None:
            return redirect(url_for('colaboradores'))
        busca = True
        dado_consultado = remove_aspas(request.form.get('dado_consultado')).lower()
        tipo_de_consulta = request.form.get('tipo_de_consulta')
        dado_consultado = remove_aspas(request.form.get('dado_consultado')).strip()

        if dado_consultado == '.acesso' and current_user.tipo_clb == '0':
            if dado_consultado == '.acesso':
                acessos = Acesso.query.order_by(Acesso.id_acesso.desc()).all()

            if not acessos:
                acessos = None
                flash("A consulta não obteve resultados.", category="error")
                return redirect('/colaboradores')
            return render_template('/colaboradores.html', acessos=acessos,
                                                          busca=busca,
                                                          colaborador=colaborador,
                                                          colaboradores=colaboradores,
                                                          colaborador_cad_dic=colaborador_cad_dic,
                                                          dado_consultado=dado_consultado,
                                                          dict_ativa=dict_ativa,
                                                          entidade_cad_dic=entidade_cad_dic,
                                                          formata_data=formata_data,
                                                          titulo=titulo,
                                                          total_colaboradores_entidade=total_colaboradores_entidade,
                                                          total_colaboradores_cadpsr=total_colaboradores_cadpsr,
                                                          )

        elif dado_consultado == '.t':
            colaborador = None
            if current_user.tipo_clb == '0':
                colaboradores = Colaborador.query.all()

            else:
                colaboradores = Colaborador.query.filter_by(lotacao=current_user.lotacao).all()

            if not colaboradores:
                colaboradores = None
                flash("A consulta não obteve resultados.", category="error")
                return redirect('/colaboradores')
            return render_template('/colaboradores.html', acessos=acessos,
                                                          busca=busca,
                                                          colaborador=colaborador,
                                                          colaboradores=colaboradores,
                                                          colaborador_cad_dic=colaborador_cad_dic,
                                                          dado_consultado=dado_consultado,
                                                          dict_ativa=dict_ativa,
                                                          entidade_cad_dic=entidade_cad_dic,
                                                          titulo=titulo,
                                                          total_colaboradores_entidade=total_colaboradores_entidade,
                                                          total_colaboradores_cadpsr=total_colaboradores_cadpsr,
                                                          )
        elif tipo_de_consulta == 'NOME':
            colaborador = Colaborador.query.filter(Colaborador.nome_civil.like('%' + dado_consultado + '%')).first()

        elif tipo_de_consulta == 'IDC':
            if dado_consultado.isdigit():
                colaborador = Colaborador.query.get(dado_consultado)
            else:
                flash('Utilize apenas número para consulta por  IDC.', category='error')
                return redirect('/colaboradores')
        else:
            if dado_consultado.isdigit():
                colaborador = Colaborador.query.filter_by(cpf=dado_consultado).first()
            else:
                flash('Utilize apenas número para consulta por  CPF.', category='error')
                return redirect('/colaboradores')

        if colaborador and busca == True:

            if colaborador.tipo_clb == '0':
                flash('Cadastro não localizado.', category='error')
                return redirect(url_for('colaboradores'))

            if colaborador.cpf == current_user.cpf:
                flash('Cadastro não localizado.', category='error')
                return redirect(url_for('colaboradores'))

            if colaborador.id == current_user.id:
                flash('Cadastro não localizado.', category='error')
                return redirect(url_for('colaboradores'))

            if current_user.tipo_clb == '4':
                if current_user.lotacao != colaborador.lotacao:
                    flash('Cadastro não localizado.', category='error')
                    return redirect(url_for('colaboradores'))

            return render_template('colaboradores.html', acessos=acessos,
                                                         busca=busca,
                                                         colaborador=colaborador,
                                                         colaboradores=None,
                                                         colaborador_cad_dic=colaborador_cad_dic,
                                                         dado_consultado=dado_consultado,
                                                         dict_ativa=dict_ativa,
                                                         entidade_cad_dic=entidade_cad_dic,
                                                         total_colaboradores_entidade=total_colaboradores_entidade,
                                                         total_colaboradores_cadpsr=total_colaboradores_cadpsr,
                                                         titulo=titulo,
                                                         )
        else:
            busca = None
            flash("Cadastro não localizado.", category="error")
            return redirect('/colaboradores')

    return render_template('colaboradores.html', busca=busca,
                                                 colaborador_cad_dic=colaborador_cad_dic,
                                                 dict_ativa=dict_ativa,
                                                 entidade_cad_dic=entidade_cad_dic,
                                                 total_colaboradores_entidade=total_colaboradores_entidade,
                                                 total_colaboradores_cadpsr=total_colaboradores_cadpsr,
                                                 titulo=titulo,
                                                 )


@app.route('/pessoas', methods=['GET', 'POST'])
@login_required
def pessoas():
    if current_user.status == 'INICIO' or current_user.status == 'REDEF':
        flash('Para acessar outras áreas do sistema, você precisa alterar sua senha!', category='error')
        return redirect('perfil')

    busca = None
    dict_ativa = ativa_nav_link('pessoas')
    titulo = 'Consulta de Pessoas - CadPSR+'
    total_pessoas_cadpsr = len(Pessoa.query.all())
    total_pessoas_entidade = len(Pessoa.query.filter_by(entidade_referencia=current_user.lotacao).all())

    if request.method == 'POST':

        if request.form.get('dado_consultado') == '' or None:
            return redirect(url_for('pessoas'))

        busca = True
        tipo_de_consulta = request.form.get('tipo_de_consulta')
        dado_consultado = remove_aspas(request.form.get('dado_consultado'))

        if dado_consultado == '.t' or dado_consultado == '.e1' or dado_consultado == '.e2' or dado_consultado == '.e3' or dado_consultado == '.e4':
            pessoa = None
            pessoas = None
            if current_user.tipo_clb == '0':
                if dado_consultado == '.t':
                    pessoas = Pessoa.query.all()
                else:
                    pessoas = Pessoa.query.filter_by(entidade_referencia=dado_consultado[2]).all() #fatiamento, expressa apenas o nº
                    if len(pessoas ) == 0:
                        pessoas = None

            elif dado_consultado == '.t':
                pessoas = Pessoa.query.filter_by(entidade_referencia=current_user.lotacao).all()

            if not pessoas:
                flash("A consulta não obteve resultados.", category="error")
                return redirect('/pessoas')

            return render_template('/pessoas.html', busca=busca,
                                                    colaborador_cad_dic=colaborador_cad_dic,
                                                    dado_consultado=dado_consultado,
                                                    dict_ativa=dict_ativa,
                                                    entidade_cad_dic=entidade_cad_dic,
                                                    pessoa=pessoa,
                                                    pessoas=pessoas,
                                                    titulo=titulo,
                                                    total_pessoas_entidade=total_pessoas_entidade,
                                                    total_pessoas_cadpsr=total_pessoas_cadpsr,
                                                    )

        if tipo_de_consulta == 'NOME':
            pessoa = Pessoa.query.filter(Pessoa.nome_civil.like('%' + dado_consultado + '%')).first()
        elif tipo_de_consulta == 'ID':
            if dado_consultado.isdigit():
                pessoa = Pessoa.query.filter_by(id=int(dado_consultado)).first()
            else:
                flash(
                    'Utilize apenas número para consulta por IDP.', category='error')
                return redirect('/pessoas')
        else:
            if dado_consultado.isdigit():
                pessoa = Pessoa.query.filter_by(cpf=dado_consultado).first()
            else:
                flash(
                    'Utilize apenas número para consulta por CPF.', category='error')
                return redirect('/pessoas')

        if pessoa:
            dn = pessoa.data_nascimento.split('-')
            nascimento = f'{dn[2]}/{dn[1]}/{dn[0]}'
            return render_template('/pessoas.html', busca=busca,
                                                    colaborador_cad_dic=colaborador_cad_dic,
                                                    dict_ativa=dict_ativa,
                                                    entidade_cad_dic=entidade_cad_dic,
                                                    pessoa=pessoa,
                                                    pessoas=None,
                                                    total_pessoas_entidade=total_pessoas_entidade,
                                                    total_pessoas_cadpsr=total_pessoas_cadpsr,
                                                    titulo=titulo,
                                                    )
        else:
            busca = None
            flash("Cadastro não localizado.", category="error")
            return redirect('/pessoas')

    return render_template('/pessoas.html', busca=busca,
                                            colaborador_cad_dic=colaborador_cad_dic,
                                            dict_ativa=dict_ativa,
                                            entidade_cad_dic=entidade_cad_dic,
                                            total_pessoas_entidade=total_pessoas_entidade,
                                            total_pessoas_cadpsr=total_pessoas_cadpsr,
                                            titulo=titulo,
                                            )


@app.route('/cadastro_clb/<clb_id>', methods=['GET', 'POST'])
@login_required
def cadastro_clb(clb_id):
    if current_user.status == 'INICIO' or current_user.status == 'REDEF':
        flash('Para acessar outras áreas do sistema, você precisa alterar sua senha!', category='error')
        return redirect('perfil')
    if current_user.tipo_clb == '5':
        return redirect('/index.html')

    colaborador = Colaborador.query.get(clb_id)
    dict_ativa = ativa_nav_link('colaboradores')
    titulo = 'Cadastro Colaborador(a) - CadPSR+'

    if current_user.id == colaborador.id:
        flash('Acesso negado.', category='error')
        return redirect('/colaboradores')

    if current_user.tipo_clb == '4' and current_user.lotacao != colaborador.lotacao:
        flash('Acesso não autorizado.', category='error')
        return redirect(url_for('colaboradores'))

    if not colaborador:
        flash('Cadastro não localizado.', category='error')
        return redirect(url_for('colaboradores'))

    data_atualizacao = formata_data(colaborador.data_atualizacao)
    data_criacao = formata_data(colaborador.data_criacao)

    return render_template('cadastro_clb.html', colaborador=colaborador,
                                                colaborador_cad_dic=colaborador_cad_dic,
                                                data_criacao=data_criacao,
                                                data_atualizacao=data_atualizacao,
                                                dict_ativa=dict_ativa,
                                                entidade_cad_dic=entidade_cad_dic,
                                                mascara_cpf=mascara_cpf,
                                                mascara_doc=mascara_doc,
                                                titulo=titulo,
                                                )


@app.route('/cadastro_psr/<int:psr_id>', methods=['GET', 'POST'])
@login_required
def cadastro_psr(psr_id):
    if current_user.status == 'INICIO' or current_user.status == 'REDEF':
        flash('Para acessar outras áreas do sistema, você precisa alterar sua senha!', category='error')
        return redirect('perfil')
    pessoa = Pessoa.query.get(psr_id)

    if not pessoa:
        flash('Cadastro não encontrado.', category="error")
        return redirect('/pessoas')

    data_atualizacao = formata_data(pessoa.data_atualizacao)
    data_criacao = formata_data(pessoa.data_criacao)
    data_impressao = formata_data_br(now('America/Sao_Paulo').format('YYYY-MM-DD-HH-mm-ss-SSSSSS'))
    dict_ativa = ativa_nav_link('pessoas')
    estado = 'disabled'
    titulo = 'Cadastro Pessoa - CadPSR+'
    titulo_body_2 = pessoa.nome_civil

    return render_template('/cadastro_psr.html', colaborador=current_user,
                                                 colaborador_cad_dic=colaborador_cad_dic,
                                                 data_atualizacao=data_atualizacao,
                                                 data_criacao=data_criacao,
                                                 data_impressao=data_impressao,
                                                 dict_ativa=dict_ativa,
                                                 estado=estado,
                                                 entidade_cad_dic=entidade_cad_dic,
                                                 mascara_cpf=mascara_cpf,
                                                 mascara_doc=mascara_doc,
                                                 mascara_tel=mascara_tel,
                                                 pessoa=pessoa,
                                                 pessoa_cad_dic=pessoa_cad_dic,
                                                 questionario=questionario,
                                                 questionario_pessoa_estrangeira=questionario_pessoa_estrangeira,
                                                 titulo=titulo,
                                                 titulo_body_2=titulo_body_2
                                                 )


@app.route('/edicao_clb/<clb_id>', methods=['GET', 'POST'])
@login_required
def edicao_clb(clb_id):
    if current_user.status == 'INICIO' or current_user.status == 'REDEF':
        flash('Para acessar outras áreas do sistema, você precisa alterar sua senha!', category='error')
        return redirect('perfil')
    if current_user.tipo_clb == '5':
        flash('Acesso não autorizado!')
        return redirect('/index.html')

    colaborador = Colaborador.query.get(clb_id)
    dict_ativa = ativa_nav_link('colaboradores')

    if not colaborador:
        flash('Colaborador(a) não encontrado!', category='error')
        return redirect(url_for('colaboradores'))

    titulo = 'Edição Cadastro Colaborador(a) - CadPSR+'

    if current_user.tipo_clb == '4' and current_user.lotacao != colaborador.lotacao:
        flash('Acesso negado.', category='error')
        return redirect(url_for('colaboradores'))

    data_atualizacao = formata_data(colaborador.data_atualizacao)
    data_criacao = formata_data(colaborador.data_criacao)

    if request.method == 'POST':

        cpf = limpa_doc(request.form.get('cpf'))
        nome_civil = request.form.get('nome_civil')
        nome_social = request.form.get('nome_social')
        if nome_social is None or nome_social == '':
            nome_social = nome_civil
        data_nascimento = request.form.get('data_nascimento')
        email = request.form.get('email')
        iniciativa = request.form.get('iniciativa')
        tipo_clb = request.form.get('tipo_clb')
        lotacao = request.form.get('lotacao')
        modificado_por = current_user.id

        # VERIFICAÇÃO DE ENTRADA DE DADOS

        if nome_civil != None:
            if len(nome_civil) > 60:
                flash('O campo Nome Civil não pode conter mais de 60 caracteres.', category='error')
                return redirect('/novo_clb')

        if nome_social != None:
            if len(nome_social) > 60:
                flash('O campo Nome Social não pode conter mais de 60 caracteres.', category='error')
                return redirect('/novo_clb')

        if data_nascimento != None:
            if len(data_nascimento) > 10:
                flash('O campo "Data de Nascimento" não pode conter mais de 10 caracteres.', category='error')
                return redirect('/novo_clb')

        if len(nome_civil) < 3:
            flash('Nome curto demais.', category='error')
            return redirect(f'/edicao_clb/{clb_id}')

        # VERIFICAÇÃO DE DUPLICAÇÃO NA BASE DADOS

        # Verifica se existe CPF cadastrado em outro cadastro!
        verifica_cpf = Colaborador.query.filter_by(cpf=cpf).first()
        if verifica_cpf and verifica_cpf.id != colaborador.id:
            flash(f'Falha ao atualizar o cadastro: CPF já cadastrado. IDC correspondente: {colaborador.id}', category='error')
            return redirect('/colaboradores')

        colaborador = Colaborador.query.get(clb_id)
        colaborador.nome_civil = nome_civil
        colaborador.nome_social = nome_social
        colaborador.data_nascimento = data_nascimento
        colaborador.iniciativa = iniciativa
        colaborador.tipo_clb = tipo_clb
        colaborador.lotacao = lotacao
        colaborador.data_atualizacao = now(
            'America/Sao_Paulo').format('YYYY-MM-DD-HH-mm-ss-SSSSSS')
        colaborador.modificado_por = modificado_por

        db.session.commit()

        flash('Cadastro de atualizado com sucesso.', category='success')
        return redirect(f'/cadastro_clb/{clb_id}')

    return render_template('edicao_clb.html', colaborador=colaborador,
                                              colaborador_cad_dic=colaborador_cad_dic,
                                              data_criacao=data_criacao,
                                              data_atualizacao=data_atualizacao,
                                              dict_ativa=dict_ativa,
                                              entidade_cad_dic=entidade_cad_dic,
                                              mascara_cpf=mascara_cpf,
                                              titulo=titulo,
                                              )


@app.route('/edicao_psr/<int:psr_id>', methods=['GET', 'POST'])
@login_required
def edicao_psr(psr_id):
    if current_user.status == 'INICIO' or current_user.status == 'REDEF':
        flash('Para acessar outras áreas do sistema, você precisa alterar sua senha!', category='error')
        return redirect('perfil')

    pessoa = Pessoa.query.get(psr_id)

    if not pessoa:
        flash('Cadastro inexistente!', category='error')
        return redirect(url_for('pessoas'))

    data_atualizacao = formata_data(pessoa.data_atualizacao)
    data_criacao = formata_data(pessoa.data_criacao)
    dict_ativa = ativa_nav_link('pessoas')
    estado = ''
    titulo = 'Edição Cadastro Pessoa - CadPSR+'
    titulo_body_1 = 'Atualização de Dados Cadastrais - PSR'
    titulo_body_2 = pessoa.nome_civil

    if request.method == 'POST':

        pessoa = Pessoa.query.get(psr_id)

        nome_civil = request.form.get('nome_civil')
        nome_social = request.form.get('nome_social')
        if nome_civil == '' or nome_civil == '':
            flash('É necessário informar o nome civil.', category='error')
            return redirect(url_for('novo_psr'))

        if nome_social is None or nome_social == '':
            nome_social = nome_civil

        celular = limpa_doc(request.form.get('celular'))
        certidao_nascimento = limpa_doc(request.form.get('certidao_nascimento'))
        cpf = limpa_doc(request.form.get('cpf'))
        cns = limpa_doc(request.form.get('cns'))
        crnm_rnm = limpa_doc(request.form.get('crnm_rnm'))
        nis = limpa_doc(request.form.get('nis'))
        rg = limpa_doc(request.form.get('rg'))
        telefone = limpa_doc(request.form.get('telefone'))
        titulo_eleitor = limpa_doc(request.form.get('titulo_eleitor'))

        # VALIDAÇÕES DE CAMPOS DE ENTRADA

        if nome_civil is not None:
            if len(nome_civil) > 60:
                flash('O campo Nome Civil não pode conter mais de 60 caracteres.', category='error')
                return redirect('/novo_psr')

        if nome_social is not None:
            if len(nome_social) > 60:
                flash('O campo Nome Social não pode conter mais de 60 caracteres.', category='error')
                return redirect('/novo_psr')

        if request.form.get('apelido') is not None:
            if len(request.form.get('apelido')) > 60:
                flash('O campo Apelido não pode conter mais de 60 caracteres.', category='error')
                return redirect('/novo_psr')

        if request.form.get('email') is not None:
            if len(request.form.get('email')) > 60:
                flash('O campo E-mail não pode conter mais de 60 caracteres.', category='error')
                return redirect('/novo_psr')

        if telefone is not None:
            if len(telefone) > 10:
                flash('O campo Telefone não pode conter mais de 10 caracteres.', category='error')
                return redirect('/novo_psr')

        if celular is not None:
            if len(celular) > 11:
                flash('O campo Celular não pode conter datamais de 11 caracteres.', category='error')
                return redirect('/novo_psr')

        if rg is not None:
            if len(rg) > 9:
                flash('O campo RG não pode conter mais de 9 caracteres.', category='error')
                return redirect('/novo_psr')

        if rg != None and request.form.get('rg_dv') == None:
                flash('É necessário informar o dígito confirmador referente ao RG.', category='error')
                return redirect('/novo_psr')

        if request.form.get('rg_emissao') is not None:
            if len(request.form.get('rg_emissao')) > 10:
                flash('O campo RG Emissão não pode conter mais de 10 caracteres.', category='error')
                return redirect('/novo_psr')

        if request.form.get('rg_orgao_emissor') is not None:
            if len(request.form.get('rg_orgao_emissor')) > 60:
                flash('O campo RG Órgão Emissor não pode conter mais de 60 caracteres.', category='error')
                return redirect('/novo_psr')

        if titulo_eleitor is not None:
            if len(titulo_eleitor) > 12:
                flash('O campo Título de Eleitor não pode conter mais de 12 caracteres.', category='error')
                return redirect('/novo_psr')

        if request.form.get('titulo_zona') is not None:
            if len(request.form.get('titulo_zona')) > 6:
                flash('O campo Zona (Título de Eleitor) não pode conter mais de 6 caracteres.', category='error')
                return redirect('/novo_psr')

        if request.form.get('titulo_secao') is not None:
            if len(request.form.get('titulo_secao')) > 6:
                flash('O campo Seção (Título de Eleitor) não pode conter mais de 6 caracteres.', category='error')
                return redirect('/novo_psr')

        if request.form.get('titulo_emissao') is not None:
            if len(request.form.get('titulo_emissao')) > 10:
                flash('O campo Emissão (Título de Eleitor) não pode conter mais de 10 caracteres.', category='error')
                return redirect('/novo_psr')

        if cns is not None:
            if len(cns) > 15:
                flash('O campo CNS não pode conter mais de 15 caracteres.', category='error')
                return redirect('/novo_psr')

        if nis is not None:
            if len(nis) > 12:
                flash('O campo NIS não pode conter mais de 12 caracteres.', category='error')
                return redirect('/novo_psr')

        if certidao_nascimento is not None:
            if len(certidao_nascimento) > 32:
                flash('O campo Certidão Nascimento não pode conter mais de 32 caracteres.', category='error')
                return redirect('/novo_psr')

        if request.form.get('naturalidade') is not None:
            if len(request.form.get('naturalidade')) > 60:
                flash('O campo Naturalidade não pode conter mais de 30 caracteres.', category='error')
                return redirect('/novo_psr')

        if request.form.get('nacionalidade') is not None:
            if len(request.form.get('nacionalidade')) > 30:
                flash('O campo Nascionalidade não pode conter mais de 30 caracteres.', category='error')
                return redirect('/novo_psr')

        if crnm_rnm is not None:
            if len(crnm_rnm) >  20:
                flash('O campo CRNM não pode conter mais de 20 caracteres.', category='error')
                return redirect('/novo_psr')

        if request.form.get('crnm_filiacao_a') is not None:
            if len(request.form.get('crnm_filiacao_a')) > 60:
                flash('O campo Filiação (a) não pode conter mais de 60 caracteres.', category='error')
                return redirect('/novo_psr')

        if request.form.get('crnm_filiacao_b') is not None:
            if len(request.form.get('crnm_filiacao_b')) > 60:
                flash('O campo Filiação (b) não pode conter mais de 60 caracteres.', category='error')
                return redirect('/novo_psr')

        if request.form.get('crnm_validade') is not None:
            if len(request.form.get('crnm_validade')) > 10:
                flash('O Validade (CRNM) não pode conter mais de 10 caracteres.', category='error')
                return redirect('/novo_psr')

        if request.form.get('crnm_classificacao') is not None:
            if len(request.form.get('crnm_classificacao')) > 30:
                flash('O Classificação (CRNM) não pode conter mais de 30 caracteres.', category='error')
                return redirect('/novo_psr')

        if request.form.get('crnm_domicilio') is not None:
            if len(request.form.get('crnm_domicilio')) > 100:
                flash('O campo Domicílio (CRNM) não pode conter mais de 100 caracteres.', category='error')
                return redirect('/novo_psr')

        if request.form.get('crnm_emissao') is not None:
            if len(request.form.get('crnm_emissao')) > 10:
                flash('O Emissão (CRNM) não pode conter mais de 10 caracteres.', category='error')
                return redirect('/novo_psr')

        if request.form.get('questao_11') is not None:
            if len(request.form.get('questao_11')) > 12:
                flash('O campo referente à renda da Questão 11 não pode conter mais de 12 caracteres.', category='error')
                return redirect('/novo_psr')

        if request.form.get('obs_psr') is not None:
            if len(request.form.get('obs_psr')) > 300:
                flash('O campo Observação não pode conter mais de 300 caracteres.', category='error')
                return redirect('/novo_psr')

        # VERIFICAÇÃO DE DUPLICAÇÃO DE DOCUMENTOS NA BASE DE DADOS

        doc = Pessoa.query.filter_by(rg=rg).first()  # Verifica RG
        if pessoa.rg is not None and pessoa.rg != '' and doc.rg is not None and doc.rg != '':
            if pessoa.rg != doc.rg:
                flash(
                    f'RG já cadastrado. IDP correspondente: {pessoa.id}.', category='error')
                return redirect(url_for('novo_psr'))

        # Verifica Título de Eleitor
        doc = Pessoa.query.filter_by(titulo_eleitor=titulo_eleitor).first()
        if pessoa.titulo_eleitor is not None and pessoa.titulo_eleitor != '' and doc.titulo_eleitor is not None and doc.titulo_eleitor != '':
            if pessoa.titulo_eleitor != doc.titulo_eleitor:
                flash(
                    f'Título de Eleitor já cadastrado. IDP correspondente: {pessoa.id}.', category='error')
                return redirect(url_for('novo_psr'))

        doc = Pessoa.query.filter_by(cns=cns).first()  # Verifica CNS

        if pessoa.cns:
            if pessoa.cns != doc.cns:
                flash(
                    f'CNS já cadastrado. IDP correspondente: {pessoa.id}.', category='error')
                return redirect(url_for('novo_psr'))

        doc = Pessoa.query.filter_by(nis=nis).first()  # Verifica NIS
        if pessoa.nis is not None and pessoa.nis != '' and doc.nis is not None and doc.nis != '':
            if pessoa.nis != doc.nis:
                flash(
                    f'NIS já cadastrado. IDP correspondente: {pessoa.id}.', category='error')
                return redirect(url_for('novo_psr'))

        # Verifica Certidão de Nascimento
        doc = Pessoa.query.filter_by(
            certidao_nascimento=certidao_nascimento).first()
        if pessoa.certidao_nascimento is not None and pessoa.certidao_nascimento != '' and doc.certidao_nascimento is not None and doc.certidao_nascimento != '':
            if pessoa.certidao_nascimento != doc.certidao_nascimento:
                flash(
                    f'Certidão de Nascimento já cadastrada. IDP correspondente: {pessoa.id}.', category='error')
                return redirect(url_for('novo_psr'))

        doc = Pessoa.query.filter_by(
            crnm_rnm=crnm_rnm).first()  # Verifica CRNM
        if pessoa.crnm_rnm is not None and pessoa.crnm_rnm != '' and doc.crnm_rnm is not None and doc.crnm_rnm != '':
            if pessoa.crnm_rnm != doc.crnm_rnm:
                flash(
                    f'CRNM já cadastrado. IDP correspondente: {pessoa.id}.', category='error')
                return redirect(url_for('novo_psr'))

        if nome_social is None or nome_social == '':
            nome_social = request.form.get('nome_civil')

        pessoa = Pessoa.query.get(int(psr_id))

        pessoa.data_atualizacao = now(
            'America/Sao_Paulo').format('YYYY-MM-DD-HH-mm-ss-SSSSSS')
        pessoa.modificado_por = current_user.id
        pessoa.nome_civil = nome_civil
        pessoa.nome_social = nome_social
        pessoa.apelido = request.form.get('apelido')
        pessoa.data_nascimento = request.form.get('data_nascimento')
        pessoa.cidade_atual = request.form.get('cidade_atual')
        pessoa.entidade_referencia = request.form.get('entidade_referencia')
        pessoa.email = request.form.get('email')
        pessoa.telefone = telefone
        pessoa.celular = celular
        pessoa.etnia = request.form.get('etnia')
        pessoa.sexo = request.form.get('sexo')
        pessoa.orientacao_sexual = request.form.get('orientacao_sexual')
        pessoa.identidade_genero = request.form.get('identidade_genero')
        pessoa.rg = rg
        pessoa.rg_dv = request.form.get('rg_dv')
        pessoa.rg_uf = request.form.get('rg_uf')
        pessoa.rg_emissao = request.form.get('rg_emissao')
        pessoa.rg_orgao_emissor = request.form.get('rg_orgao_emissor')
        pessoa.titulo_eleitor = titulo_eleitor
        pessoa.titulo_zona = request.form.get('titulo_zona')
        pessoa.titulo_secao = request.form.get('titulo_secao')
        pessoa.titulo_emissao = request.form.get('titulo_emissao')
        pessoa.cns = cns
        pessoa.nis = nis
        pessoa.certidao_nascimento = certidao_nascimento
        pessoa.naturalidade = request.form.get('naturalidade')
        pessoa.nacionalidade = request.form.get('nacionalidade')
        pessoa.crnm_rnm = crnm_rnm
        pessoa.crnm_filiacao_a = request.form.get('crnm_filiacao_a')
        pessoa.crnm_filiacao_b = request.form.get('crnm_filiacao_b')
        pessoa.crnm_validade = request.form.get('crnm_validade')
        pessoa.crnm_classificacao = request.form.get('crnm_classificacao')
        pessoa.crnm_domicilio = request.form.get('crnm_domicilio')
        pessoa.crnm_emissao = request.form.get('crnm_emissao')
        pessoa.questao_migracao = request.form.get('questao_migracao')
        pessoa.questao_1 = lista_para_str(request.form.getlist("questao_1"))
        pessoa.questao_2 = request.form.get('questao_2')
        pessoa.questao_3 = lista_para_str(request.form.getlist("questao_3"))
        pessoa.questao_4 = request.form.get('questao_4')
        pessoa.questao_5 = request.form.get('questao_5')
        pessoa.questao_6 = request.form.get('questao_6')
        pessoa.questao_7 = lista_para_str(request.form.getlist("questao_7"))
        pessoa.questao_8 = lista_para_str(request.form.getlist("questao_8"))
        pessoa.questao_9 = request.form.get('questao_9')
        pessoa.questao_10 = lista_para_str(request.form.getlist("questao_10"))
        pessoa.questao_11 = request.form.get('questao_11')
        pessoa.questao_12 = request.form.get('questao_12')
        pessoa.questao_13 = lista_para_str(request.form.getlist("questao_13"))
        pessoa.questao_14 = request.form.get('questao_14')
        pessoa.obs_psr = request.form.get('obs_psr')
        db.session.commit()

        atendimento = Atendimento(data_atendimento=pessoa.data_criacao,
                                  entidade_geradora=current_user.lotacao,
                                  id_pessoa=pessoa.id,
                                  id_colaborador=current_user.id,
                                  obs_atendimento=pessoa.obs_psr or '',
                                  nome_colaborador=current_user.nome_civil,
                                  nome_pessoa=pessoa.nome_civil,
                                  tipo_atendimento='1',
                                 )
        db.session.add(atendimento)
        db.session.commit()

        flash(
            f'O cadastro de {pessoa.nome_civil} foi atualizado com sucesso!', category='success')
        return redirect(f'/cadastro_psr/{psr_id}')

    return render_template('/edicao_psr.html', colaborador=current_user,
                                               colaborador_cad_dic=colaborador_cad_dic,
                                               data_atualizacao=data_atualizacao,
                                               data_criacao=data_criacao,
                                               dict_ativa=dict_ativa,
                                               entidade_cad_dic=entidade_cad_dic,
                                               estado=estado,
                                               mascara_cpf=mascara_cpf,
                                               mascara_doc=mascara_doc,
                                               mascara_tel=mascara_tel,
                                               pessoa=pessoa,
                                               pessoa_cad_dic=pessoa_cad_dic,
                                               questionario=questionario,
                                               questionario_pessoa_estrangeira=questionario_pessoa_estrangeira,
                                               titulo=titulo,
                                               titulo_body_1=titulo_body_1,
                                               titulo_body_2=titulo_body_2
                                               )


@app.route('/exclusao_clb/<clb_id>', methods=['POST'])
@login_required
def exclusao_clb(clb_id):
    if current_user.status == 'INICIO' or current_user.status == 'REDEF':
        flash('Para acessar outras áreas do sistema, você precisa alterar sua senha!', category='error')
        return redirect('perfil')
    if current_user.tipo_clb == '5':
        flash('Acesso não autorizado!')
        return redirect('/index.html')

    colaborador = Colaborador.query.get(clb_id)

    if not colaborador:
        flash('Erro ao excluir cadastro: Colaborador não localizado.',
              category='error')
        return redirect(url_for('colaboradores'))

    if current_user.tipo_clb == colaborador.tipo_clb:
        flash('Acesso negado.', category='error')
        return redirect(url_for('index'))

    if current_user.lotacao == 'GERENTE' and current_user.lotacao != colaborador.lotacao:
        flash('Você não tem permissão para alterar/desativar cadastros de Colaboradores de outras Entidades.', category='error')
        colaboradores = Colaborador.query.all()
        return render_template('colaboradores.html', colaboradores=colaboradores)

    db.session.delete(colaborador)
    db.session.commit()
    flash(
        f'O cadastro de {colaborador.nome_civil} foi excluído com sucesso.', category='success')
    return redirect('/colaboradores')


@app.route('/exclusao_psr/<psr_id>', methods=['POST'])
@login_required
def exclusao_psr(psr_id):
    if current_user.status == 'INICIO' or current_user.status == 'REDEF':
        flash('Para acessar outras áreas do sistema, você precisa alterar sua senha!', category='error')
        return redirect('perfil')
    if current_user.tipo_clb == '5':
        flash('Acesso não autorizado!')
        return redirect('/index.html')

    pessoa = Pessoa.query.get(psr_id)

    if not pessoa:
        flash('Erro ao excluir cadastro: cadastro não localizado.', category='error')
        return redirect(url_for('pessoas'))

    db.session.delete(pessoa)
    db.session.commit()
    flash(
        f'O cadastro de {pessoa.nome_civil} foi excluído com sucesso.', category='success')

    return redirect('/pessoas')


@app.route('/novo_clb', methods=['GET', 'POST'])
@login_required
def novo_clb():
    if current_user.status == 'INICIO' or current_user.status == 'REDEF':
        flash('Para acessar outras áreas do sistema, você precisa alterar sua senha!', category='error')
        return redirect('perfil')
    if current_user.tipo_clb == '5':
        flash('Acesso não autorizado!')
        return redirect('/index.html')

    dict_ativa = ativa_nav_link('colaboradores')
    titulo = 'Novo Cadastro de Colaborador(a) - CadPSR+'
    titulo_body_2 = 'Novo Cadastro de Colaborador(a)'

    return render_template("novo_clb.html", colaborador=current_user,
                                            colaborador_cad_dic=colaborador_cad_dic,
                                            dict_ativa=dict_ativa,
                                            entidade_cad_dic=entidade_cad_dic,
                                            questionario=questionario,
                                            titulo=titulo,
                                            titulo_body_2=titulo_body_2
                                            )


@app.route('/novo_psr', methods=['GET', 'POST'])
@login_required
def novo_psr():
    if current_user.status == 'INICIO' or current_user.status == 'REDEF':
        flash('Para acessar outras áreas do sistema, você precisa alterar sua senha!', category='error')
        return redirect('perfil')

    dict_ativa = ativa_nav_link('pessoas')
    titulo = 'Novo Cadastro de Pessoa - CadPSR+'
    titulo_body_2 = 'Novo Cadastro de Pessoa'

    return render_template('novo_psr.html', colaborador_cad_dic=colaborador_cad_dic,
                                            dict_ativa=dict_ativa,
                                            entidade_cad_dic=entidade_cad_dic,
                                            pessoa_cad_dic=pessoa_cad_dic,
                                            questionario=questionario,
                                            questionario_pessoa_estrangeira=questionario_pessoa_estrangeira,
                                            titulo=titulo,
                                            titulo_body_2=titulo_body_2,
                                            )


@app.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():

    dict_ativa = ativa_nav_link('perfil')

    if current_user.status == 'ATIVO':
        titulo = 'Perfil Colaborador(a) - CadPSR+'
        subtitulo = 'Alteração de Senha'


    if current_user.status == 'REDEF':
        titulo = 'Redefinição de Senha efetuada por Chefia - CadPSR+'
        subtitulo = 'Por favor, altere sua senha (é obrigatório).'

    if current_user.status == 'INICIO':
        titulo = 'Primeiro Acesso - CadPSR+'
        subtitulo = 'Boas-vindas. Este é seu primeiro acesso. É necessário alterar sua senha.'


    if request.method == 'POST':
        senha_atual = request.form.get('senha_atual')
        senha_nova = request.form.get('senha_nova')
        senha_confirmacao = request.form.get('senha_confirmacao')

        senha = current_user.senha

        if not check_password_hash(senha, senha_atual):
            flash('A senha atual não corresponde à senha armazenada.', category='error')
            return redirect('/perfil')


        elif senha_atual == senha_nova:
            flash('A nova senha precisa ser diferente da senha atual.', category='error')
            return redirect('/perfil')

        if senha_nova != senha_confirmacao:
            flash('Os campos de *Nova Senha e *Confirmação de Senha não se correspondem.', category='error')
            return redirect('/perfil')

        if len(senha_nova) < 10:
            flash('A senha precisa conter no mínimo 10 dígitos.', category='error')
            return redirect('/perfil')

        if len(senha_nova) > 64:
            flash('A senha não pode conter mais de 64 caracteres.', category='error')
            return redirect('/perfil')

        senha_hash = generate_password_hash(senha_nova)
        current_user.senha = senha_hash

        if current_user.status == 'REDEF' or current_user.status == 'INICIO':
            current_user.status = 'ATIVO'
            mensagem = 'Senha alterada com sucesso. Agora você pode acessar o sistema.'
        else:
            mensagem = 'Senha alterada com sucesso.'
        db.session.commit()
        del senha_atual
        del senha_nova
        del senha_hash

        flash(mensagem, category='success')
        return redirect('/index')

    return render_template('perfil.html', colaborador=current_user,
                                          colaborador_cad_dic=colaborador_cad_dic,
                                          dict_ativa=dict_ativa,
                                          entidade_cad_dic=entidade_cad_dic,
                                          subtitulo=subtitulo,
                                          titulo=titulo,
                                          )


@app.route('/persistencia_atendimento', methods=['POST'])
@login_required
def persistencia_atendimento():
    if current_user.status == 'INICIO' or current_user.status == 'REDEF':
        flash('Para acessar outras áreas do sistema, você precisa alterar sua senha!', category='error')
        return redirect('perfil')

    if request.method == 'POST':
        registrar = request.form.get('registrar')
        tipo_atendimento = request.form.get('tipo_atendimento')
        obs_atendimento = request.form.get('obs_atendimento')
        if obs_atendimento != None:
            if len(obs_atendimento) > 500:
                flash('O campo Observação de Atendimento não pode conter mais de 500 caracteres.', category='error')
                redirect('atendimentos')

        data_criacao = now(
            'America/Sao_Paulo').format('YYYY-MM-DD-HH-mm-ss-SSSSSS')
        pessoa = Pessoa.query.get(registrar)
        titulo = 'Consulta de Atendimentos'
        tipo_consulta = 'id_atendimento'

        atendimento = Atendimento(data_atendimento=data_criacao,
                                  entidade_geradora=current_user.lotacao,
                                  id_pessoa=pessoa.id,
                                  id_colaborador=current_user.id,
                                  nome_pessoa=pessoa.nome_civil,
                                  nome_colaborador=current_user.nome_civil,
                                  obs_atendimento=obs_atendimento or '',
                                  tipo_atendimento=tipo_atendimento,
                                 )
        db.session.add(atendimento)
        db.session.commit()

        return redirect(f'atendimentos_cadpsr/{registrar}')

    return redirect('atendimentos')


@app.route('/persistencia_psr', methods=['POST'])
@login_required
def persistencia_psr():
    if current_user.status == 'INICIO' or current_user.status == 'REDEF':
        flash('Para acessar outras áreas do sistema, você precisa alterar sua senha!', category='error')
        return redirect('perfil')

    if request.method == 'POST':
        if not request.form.get('nome_civil'):
            flash('É necessário informar o nome civil.', category='error')
            return redirect(url_for('novo_psr'))

        nome_civil = request.form.get('nome_civil')
        nome_social = request.form.get('nome_social')
        if nome_social == None or nome_social == '':
            nome_social = nome_civil

        celular = limpa_doc(request.form.get('celular'))
        certidao_nascimento = limpa_doc(request.form.get('certidao_nascimento'))
        cpf = limpa_doc(request.form.get('cpf'))
        cns = limpa_doc(request.form.get('cns'))
        crnm_rnm = limpa_doc(request.form.get('crnm_rnm'))
        nis = limpa_doc(request.form.get('nis'))
        rg = limpa_doc(request.form.get('rg'))
        telefone = limpa_doc(request.form.get('telefone'))
        titulo_eleitor = limpa_doc(request.form.get('titulo_eleitor'))

        # VALIDAÇÕES DOS CAMPOS DE ENTRADA

        if nome_civil is not None:
            if len(nome_civil) > 60:
                flash('O campo Nome Civil não pode conter mais de 60 caracteres.', category='error')
                return redirect('/novo_psr')

        if nome_social is not None:
            if len(nome_social) > 60:
                flash('O campo Nome Social não pode conter mais de 60 caracteres.', category='error')
                return redirect('/novo_psr')

        if request.form.get('apelido') is not None:
            if len(request.form.get('apelido')) > 60:
                flash('O campo Apelido não pode conter mais de 60 caracteres.', category='error')
                return redirect('/novo_psr')

        if request.form.get('email') is not None:
            if len(request.form.get('email')) > 60:
                flash('O campo E-mail não pode conter mais de 60 caracteres.', category='error')
                return redirect('/novo_psr')

        if telefone is not None:
            if len(telefone) > 10:
                flash('O campo Telefone não pode conter mais de 10 caracteres.', category='error')
                return redirect('/novo_psr')

        if celular is not None:
            if len(celular) > 11:
                flash('O campo Celular não pode conter datamais de 11 caracteres.', category='error')
                return redirect('/novo_psr')

        if rg is not None:
            if len(rg) > 9:
                flash('O campo RG não pode conter mais de 9 caracteres.', category='error')
                return redirect('/novo_psr')

        if request.form.get('rg') != '' and request.form.get('rg_dv') == '':
                flash('É necessário informar o dígito confirmador referente ao RG.', category='error')
                return redirect('/novo_psr')

        if request.form.get('rg_emissao') is not None:
            if len(request.form.get('rg_emissao')) > 10:
                flash('O campo RG Emissão não pode conter mais de 10 caracteres.', category='error')
                return redirect('/novo_psr')

        if request.form.get('rg_orgao_emissor') is not None:
            if len(request.form.get('rg_orgao_emissor')) > 60:
                flash('O campo RG Órgão Emissor não pode conter mais de 60 caracteres.', category='error')
                return redirect('/novo_psr')

        if titulo_eleitor is not None:
            if len(titulo_eleitor) > 12:
                flash('O campo Título de Eleitor não pode conter mais de 12 caracteres.', category='error')
                return redirect('/novo_psr')

        if request.form.get('titulo_zona') is not None:
            if len(request.form.get('titulo_zona')) > 6:
                flash('O campo Zona (Título de Eleitor) não pode conter mais de 6 caracteres.', category='error')
                return redirect('/novo_psr')

        if request.form.get('titulo_secao') is not None:
            if len(request.form.get('titulo_secao')) > 6:
                flash('O campo Seção (Título de Eleitor) não pode conter mais de 6 caracteres.', category='error')
                return redirect('/novo_psr')

        if request.form.get('titulo_emissao') is not None:
            if len(request.form.get('titulo_emissao')) > 10:
                flash('O campo Emissão (Título de Eleitor) não pode conter mais de 10 caracteres.', category='error')
                return redirect('/novo_psr')

        if cns is not None:
            if len(cns) > 15:
                flash('O campo CNS não pode conter mais de 15 caracteres.', category='error')
                return redirect('/novo_psr')

        if nis is not None:
            if len(nis) > 12:
                flash('O campo NIS não pode conter mais de 12 caracteres.', category='error')
                return redirect('/novo_psr')

        if certidao_nascimento is not None:
            if len(certidao_nascimento) > 32:
                flash('O campo Certidão Nascimento não pode conter mais de 32 caracteres.', category='error')
                return redirect('/novo_psr')

        if request.form.get('naturalidade') is not None:
            if len(request.form.get('naturalidade')) > 60:
                flash('O campo Naturalidade não pode conter mais de 30 caracteres.', category='error')
                return redirect('/novo_psr')

        if request.form.get('nacionalidade') is not None:
            if len(request.form.get('nacionalidade')) > 30:
                flash('O campo Nascionalidade não pode conter mais de 30 caracteres.', category='error')
                return redirect('/novo_psr')

        if crnm_rnm is not None:
            if len(crnm_rnm) >  20:
                flash('O campo CRNM não pode conter mais de 20 caracteres.', category='error')
                return redirect('/novo_psr')

        if request.form.get('crnm_filiacao_a') is not None:
            if len(request.form.get('crnm_filiacao_a')) > 60:
                flash('O campo Filiação (a) não pode conter mais de 60 caracteres.', category='error')
                return redirect('/novo_psr')

        if request.form.get('crnm_filiacao_b') is not None:
            if len(request.form.get('crnm_filiacao_b')) > 60:
                flash('O campo Filiação (b) não pode conter mais de 60 caracteres.', category='error')
                return redirect('/novo_psr')

        if request.form.get('crnm_validade') is not None:
            if len(request.form.get('crnm_validade')) > 10:
                flash('O Validade (CRNM) não pode conter mais de 10 caracteres.', category='error')
                return redirect('/novo_psr')

        if request.form.get('crnm_classificacao') is not None:
            if len(request.form.get('crnm_classificacao')) > 30:
                flash('O Classificação (CRNM) não pode conter mais de 30 caracteres.', category='error')
                return redirect('/novo_psr')

        if request.form.get('crnm_domicilio') is not None:
            if len(request.form.get('crnm_domicilio')) > 100:
                flash('O campo Domicílio (CRNM) não pode conter mais de 100 caracteres.', category='error')
                return redirect('/novo_psr')

        if request.form.get('crnm_emissao') is not None:
            if len(request.form.get('crnm_emissao')) > 10:
                flash('O Emissão (CRNM) não pode conter mais de 10 caracteres.', category='error')
                return redirect('/novo_psr')

        if request.form.get('questao_11') is not None:
            if len(request.form.get('questao_11')) > 12:
                flash('O campo referente à renda da Questão 11 não pode conter mais de 12 caracteres.', category='error')
                return redirect('/novo_psr')

        if request.form.get('obs_psr') is not None:
            if len(request.form.get('obs_psr')) > 500:
                flash('O campo Observação não pode conter mais de 500 caracteres.', category='error')
                return redirect('/novo_psr')


        # VERIFICAÇÃO DE DUPLICAÇÃO DE DOCUMENTOS CADASTRADOS NA BASE DE DADOS

        pessoa = Pessoa.query.filter_by(cpf=cpf).first()  # Verifica CPF
        if pessoa:
            flash(f'CPF já cadastrado. IDP correspondente: {pessoa.id}.', category='error')
            return redirect(url_for('novo_psr'))

        pessoa = Pessoa.query.filter_by(rg=rg).first()  # Verifica RG
        if pessoa and pessoa.rg != '':
            flash(f'RG já cadastrado. IDP correspondente: {pessoa.id}.', category='error')
            return redirect(url_for('novo_psr'))

        pessoa = Pessoa.query.filter_by(
            titulo_eleitor=titulo_eleitor).first()  # Verifica Título de Eleitor
        if pessoa and pessoa.titulo_eleitor != '':
            flash(f'Título de Eleitor já cadastrado. IDP correspondente: {pessoa.id}.', category='error')
            return redirect(url_for('novo_psr'))

        pessoa = Pessoa.query.filter_by(cns=cns).first()  # Verifica CNS
        if pessoa and pessoa.cns != '':
            flash(f'CNS já cadastrado. IDP correspondente: {pessoa.id}.', category='error')
            return redirect(url_for('novo_psr'))

        pessoa = Pessoa.query.filter_by(nis=nis).first()  # Verifica NIS
        if pessoa and pessoa.nis != '':
            flash(f'NIS já cadastrado. IDP correspondente: {pessoa.id}.', category='error')
            return redirect(url_for('novo_psr'))

        # Verifica Certidão de Nascimento
        pessoa = Pessoa.query.filter_by(
            certidao_nascimento=certidao_nascimento).first()
        if pessoa and pessoa.certidao_nascimento != '':
            flash(f'Certidão de Nascimento já cadastrada. IDP correspondente: {pessoa.id}.', category='error')
            return redirect(url_for('novo_psr'))

        pessoa = Pessoa.query.filter_by(
            crnm_rnm=crnm_rnm).first()  # Verifica CRNM
        if pessoa and pessoa.crnm_rnm:
            flash(f'CRNM de Nascimento já cadastrada. IDP correspondente: {pessoa.id}.', category='error')
            return redirect(url_for('novo_psr'))

        if not cpf.isdigit():
            flash('CPF inválido. Digite apenas números.', category='error')
            return redirect(url_for('novo_psr'))

        elif len(cpf) != 11:
            flash('O CPF deve conter exatos 11 dígitos.', category='error')
            return redirect(url_for('novo_psr'))

        pessoa = Pessoa(status='ATIVO',
                        data_criacao=now(
                            'America/Sao_Paulo').format('YYYY-MM-DD-HH-mm-ss-SSSSSS'),
                        criado_por=current_user.id,
                        nome_civil=nome_civil,
                        nome_social=nome_social,
                        apelido=request.form.get('apelido'),
                        cpf=cpf,
                        data_nascimento=request.form.get('data_nascimento'),
                        cidade_atual=request.form.get('cidade_atual'),
                        entidade_geradora = current_user.lotacao,
                        entidade_referencia=request.form.get('entidade_referencia'),
                        email=request.form.get('email'),
                        telefone=telefone,
                        celular=celular,
                        etnia=request.form.get('etnia'),
                        sexo=request.form.get('sexo'),
                        orientacao_sexual=request.form.get('orientacao_sexual'),
                        identidade_genero=request.form.get('identidade_genero'),
                        rg=rg,
                        rg_dv=request.form.get('rg_dv'),
                        rg_uf=request.form.get('rg_uf'),
                        rg_emissao=request.form.get('rg_emissao'),
                        rg_orgao_emissor=request.form.get('rg_orgao_emissor'),
                        titulo_eleitor=titulo_eleitor,
                        titulo_zona=request.form.get('titulo_zona'),
                        titulo_secao=request.form.get('titulo_secao'),
                        titulo_emissao=request.form.get('titulo_emissao'),
                        cns=cns,
                        nis=nis,
                        certidao_nascimento=certidao_nascimento,
                        naturalidade=request.form.get('naturalidade'),
                        nacionalidade=request.form.get('nacionalidade'),
                        crnm_rnm=crnm_rnm,
                        crnm_filiacao_a=request.form.get('crnm_filiacao_a'),
                        crnm_filiacao_b=request.form.get('crnm_filiacao_b'),
                        crnm_validade=request.form.get('crnm_validade'),
                        crnm_classificacao=request.form.get('crnm_classificacao'),
                        crnm_domicilio=request.form.get('crnm_domicilio'),
                        crnm_emissao=request.form.get('crnm_emissao'),
                        questao_migracao=request.form.get('questao_migracao'),
                        questao_1=lista_para_str(request.form.getlist("questao_1")),
                        questao_2=request.form.get('questao_2'),
                        questao_3=lista_para_str(request.form.getlist("questao_3")),
                        questao_4=request.form.get('questao_4'),
                        questao_5=request.form.get('questao_5'),
                        questao_6=request.form.get('questao_6'),
                        questao_7=lista_para_str(request.form.getlist("questao_7")),
                        questao_8=lista_para_str(request.form.getlist("questao_8")),
                        questao_9=request.form.get('questao_9'),
                        questao_10=lista_para_str(request.form.getlist("questao_10")),
                        questao_11=request.form.get('questao_11'),
                        questao_12=request.form.get('questao_12'),
                        questao_13=lista_para_str(request.form.getlist("questao_13")),
                        questao_14=request.form.get('questao_14'),
                        obs_psr=request.form.get('obs_psr')
                        )
        db.session.add(pessoa)
        db.session.commit()
        pessoa = Pessoa.query.filter_by(cpf=cpf).first()

        atendimento = Atendimento(data_atendimento=pessoa.data_criacao,
                                  entidade_geradora=current_user.lotacao,
                                  id_pessoa=pessoa.id,
                                  id_colaborador=current_user.id,
                                  nome_colaborador=current_user.nome_civil,
                                  nome_pessoa=pessoa.nome_civil,
                                  obs_atendimento=pessoa.obs_psr or '',
                                  tipo_atendimento='2',
                                 )
        db.session.add(atendimento)
        db.session.commit()
        flash(f'{pessoa.nome_civil} foi cadastrado(a) com sucesso!', category='success')
        return redirect(f'/cadastro_psr/{pessoa.id}')

    return redirect(f'cadastro_psr/{pessoa.id}', dict_ativa=dict_ativa,
                                                 colaborador_cad_dic=colaborador_cad_dic,)


@app.route('/persistencia_clb', methods=['POST'])
@login_required
def persistencia_clb():
    if current_user.status == 'INICIO' or current_user.status == 'REDEF':
        flash('Para acessar outras áreas do sistema, você precisa alterar sua senha!', category='error')
        return redirect('perfil')
    if current_user.tipo_clb == '5':
        flash('Acesso não autorizado!')
        return redirect('/index.html')

    if request.method == 'POST':

        nome_civil = request.form.get('nome_civil')
        nome_social = request.form.get('nome_social')
        if nome_social == None or nome_social == '':
            nome_social = nome_civil

        cpf = limpa_doc(request.form.get('cpf'))
        criado_por = current_user.id
        data_nascimento = request.form.get('data_nascimento')
        email = request.form.get('email')
        iniciativa = request.form.get('iniciativa')
        tipo_clb = request.form.get('tipo_clb')
        lotacao = request.form.get('lotacao')

        # VERIFICAÇÃO DE ENTRADA DE DADOS

        if nome_civil is not None:
            if len(nome_civil) > 60:
                flash('O campo Nome Civil não pode conter mais de  caracteres.', category='error')
                return redirect('/novo_clb')

        if nome_social is not None:
            if len(nome_social) > 60:
                flash('O campo Nome Social não pode conter mais de 60 caracteres.', category='error')
                return redirect('/novo_clb')

        if cpf is not None:
            if len(cpf) > 11:
                flash('O campo CPF não pode conter mais de  caracteres.', category='error')
                return redirect('/novo_clb')

        if data_nascimento is not None:
            if len(data_nascimento) > 10:
                flash('O campo "Data de Nascimento" não pode conter mais de 10 caracteres.', category='error')
                return redirect('/novo_clb')

        if email is not None:
            if len(email) > 60:
                flash('O campo E-mail não pode conter mais de 60 caracteres.', category='error')
                return redirect('/novo_clb')

        # VERIFICAÇÃO DE DUPLICAÇÃO NA BASE DE DADOS

        verifica_cpf = Colaborador.query.filter_by(cpf=cpf).first()  # Verifica e-mail

        if verifica_cpf:
            flash(f'CPF já cadastrado. IDC correspondente: {verifica_cpf.id}!', category='error')
            return redirect('/novo_clb')

        verifica_email = Colaborador.query.filter_by(email=email).first()  # Verifica e-mail
        if verifica_email:
            flash(f'E-mail já cadastrado. IDC correspondente: {verifica_email.id}!', category='error')
            return redirect('/novo_clb')
        if not cpf.isdigit():
            flash('CPF inválido. Digite apenas números.', category='error')
            return redirect('/novo_clb')
        if len(cpf) != 11:
            flash('O CPF deve conter exatos 11 dígitos.', category='error')
            return redirect('/novo_clb')
        if len(nome_civil) < 2:
            flash('Nome curto demais.', category='error')
            return redirect('/novo_clb')

        data_criacao = now('America/Sao_Paulo').format('YYYY-MM-DD-HH-mm-ss-SSSSSS')
        colaborador = Colaborador(status='INICIO',
                                  nome_civil=nome_civil,
                                  nome_social=nome_social,
                                  cpf=cpf,
                                  data_nascimento=data_nascimento,
                                  email=email,
                                  iniciativa=iniciativa,
                                  tipo_clb=tipo_clb,
                                  lotacao=lotacao,
                                  data_criacao=data_criacao,
                                  criado_por=criado_por)
        senha_gerada = token_hex(7)
        # Gera hash da senha e o atribui ao campo senha
        colaborador.seta_senha_hash(senha_gerada)
        db.session.add(colaborador)
        db.session.commit()
        flash(f'Cadastro de {colaborador.nome_civil} efetuado com sucesso. Senha temporária: {senha_gerada}', category='success')
        del senha_gerada
        return redirect(f'cadastro_clb/{colaborador.id}')

    return redirect(f'cadastro_psr/{colaborador.id}')


@app.route('/status_clb/<int:clb_id>', methods=['POST'])
@login_required
def status_clb(clb_id):
    if current_user.status == 'INICIO' or current_user.status == 'REDEF':
        flash('Para acessar outras áreas do sistema, você precisa alterar sua senha!', category='error')
        return redirect('perfil')
    if current_user.tipo_clb == '5':
        flash('Acesso não autorizado!')
        return redirect('/index.html')

    colaborador = Colaborador.query.get(clb_id)
    if Colaborador:
        if colaborador.status == 'ATIVO' or colaborador.status == 'REDEF' or colaborador.status == 'INICIO':
            senha_gerada = token_hex(64)
            colaborador.seta_senha_hash(senha_gerada)
            colaborador.status = 'INATIVO'
            colaborador.data_atualizacao = now(
                'America/Sao_Paulo').format('YYYY-MM-DD-HH-mm-ss-SSSSSS')

            flash('Cadastro INATIVADO com sucesso.', category='success')
        else:
            colaborador.status = 'REDEF'
            senha_gerada = token_hex(7)
            colaborador.seta_senha_hash(senha_gerada)
            colaborador.data_atualizacao = now(
                'America/Sao_Paulo').format('YYYY-MM-DD-HH-mm-ss-SSSSSS')
            flash(
                f'Cadastro ATIVADO com sucesso. Senha temporária: {senha_gerada}', category='success')

        db.session.commit()
    else:
        flash('Cadastro não localizado.', category='error')

    return redirect(f'/cadastro_clb/{colaborador.id}')


@app.route('/status_psr/<int:psr_id>', methods=['POST'])
@login_required
def status_psr(psr_id):
    if current_user.status == 'INICIO' or current_user.status == 'REDEF':
        flash('Para acessar outras áreas do sistema, você precisa alterar sua senha!', category='error')
        return redirect('perfil')

    pessoa = Pessoa.query.get(psr_id)
    if Pessoa:
        if pessoa.status == 'ATIVO':
            pessoa.status = 'INATIVO'
            pessoa.data_atualizacao = now(
                'America/Sao_Paulo').format('YYYY-MM-DD-HH-mm-ss-SSSSSS')
            flash('Cadastro INATIVADO com sucesso.', category='success')
        else:
            pessoa.status = 'ATIVO'
            pessoa.data_atualizacao = now(
                'America/Sao_Paulo').format('YYYY-MM-DD-HH-mm-ss-SSSSSS')
            flash('Cadastro ATIVADO com sucesso.', category='success')

        db.session.commit()
    else:
        flash('Cadastro não localizado.', category='error')
        return redirect('/pessoas')

    return redirect(f'/cadastro_psr/{psr_id}')


@app.route('/redefinicao_senha/<clb_id>', methods=['POST'])
@login_required
def redefinicao_senha(clb_id):
    if current_user.status == 'INICIO' or current_user.status == 'REDEF':
        flash('Para acessar outras áreas do sistema, você precisa alterar sua senha!', category='error')
        return redirect('perfil')

    if current_user.tipo_clb == '5':
        flash('Acesso não autorizado!')
        return redirect('/index.html')
    if current_user.status == 'INICIO' or current_user.status == 'REDEF':
        flash('Para acessar outras áreas do sistema, você precisa alterar sua senha!', category='error')
        return redirect('/index.html')

    colaborador = Colaborador.query.get(clb_id)
    if request.method == 'POST':
        if not colaborador:
            flash('Erro! Colaborador não encontrado(a). Contate o Admin.',
                  category='error')
            return redirect('/colaboradores')

        if current_user.tipo_clb != '0' and current_user.lotacao != colaborador.lotacao:
            flash('Você não tem permissão para alterar o cadastro de colaboradores de outras Entidades!', category='error')
            return redirect('/index.html')
        if current_user.id == colaborador.id:
            flash('Acesso não autorizado: para alterar sua senha utilize a página de Perfil!', category='error')
            return redirect('/index.html')
        if colaborador.status == 'INATIVO':
            flash(f'Não foi possível redefirnir a senha. STATUS INATIVO.', category='error')
            return redirect(f'/cadastro_clb/{clb_id}')
        if colaborador.status == 'REDEF' and current_user.tipo_clb != '0':
            flash(f'Senha já foi redefinida. Aguarde o(a) Colaborador(a) acessar o sistema ou contate o Admin.', category='error')
            return redirect(f'/cadastro_clb/{clb_id}')
        if colaborador.status == 'INICIO' and current_user.tipo_clb != '0':
            flash(f'Não foi possível redefinir a senha. Colaborador(a) ainda não efetuou o primeiro acesso.', category='error')
            return redirect(f'/cadastro_clb/{clb_id}')

        senha_gerada = token_hex(7)
        colaborador.seta_senha_hash(senha_gerada)
        if colaborador.status != 'INICIO':
            colaborador.status = 'REDEF'
            colaborador.data_atualizacao = now(
                'America/Sao_Paulo').format('YYYY-MM-DD-HH-mm-ss-SSSSSS')
        db.session.commit()
        flash(
            f'A senha de {colaborador.nome_social} foi redefinida com sucesso. Senha temporária: {senha_gerada}', category='success')
        del senha_gerada

    return redirect(f'/cadastro_clb/{clb_id}')
