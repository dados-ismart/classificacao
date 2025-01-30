import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
from time import sleep
import pytz

st.set_page_config(layout="wide")
fuso_horario = pytz.timezone('America/Sao_Paulo')

def check_password():
    """Returns `True` if the user had a correct password."""
 
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if (st.session_state["username"] in st.secrets["passwords"] and st.session_state["password"] == st.secrets["passwords"][st.session_state["username"]]):
            st.session_state["password_correct"] = True
            st.session_state["authenticated_username"] = st.session_state["username"]  # Guarda o username
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False
 
    if "password_correct" not in st.session_state:
        # First run, show inputs for username + password.
        st.text_input("Usuário", on_change=password_entered, key="username")
        st.text_input(
            "Senha", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input("Usuário", on_change=password_entered, key="username")
        st.text_input(
            "Senha", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Usuário desconhecido ou senha incorreta.")
        return False
    else:
        # Password correct.
        return True


if check_password():
    #ler planilha
    conn = st.connection("gsheets", type=GSheetsConnection)

    def ler_sheets(pagina):
        df = conn.read(worksheet=pagina, ttl=1)
        return df

    def classificar():
        return 'batata'

    def retornar_indice(lista, variavel):
        if variavel == None:
            return None
        try:
            for indice, valor in enumerate(lista):
                if valor == variavel:
                    return indice
        except:
            return None

    ## LISTAS PARA MULTIPLA ESCOLHA
    caixa_periodo = ['-', '1°', '2°', '3°', '4°', '5°', '6°', '7°', '8°']
    caixa_nomenclatura = ['bimestre', 'trimestre', 'simestre', 'ciclo', 'período', 'etapa']
    # Acadêmico
    caixa_argumentacao = ['Superficial - apenas reproduz', 
                        'Argumenta e se posiciona, trazendo sua opinião de forma consistente', 
                        'Sempre traz elementos além dos solicitados']
    caixa_rotina_estudos = ['Não', 'Precisa melhorar', 'Sim']
    caixa_atividades_extracurriculares = ['Nenhuma', 'Uma', 'Mais de uma']
    caixa_sim_nao = ['Sim', 'Não']
    #Perfil
    caixa_nunca_eventualmente_sempre = ['Nunca', 'Eventualmente', 'Sempre']
    caixa_networking = ['Tem dificuldade', 'Sim (dentro da escola)', 'Sim, (além da escola)']
    # Psicológico
    caixa_fragilidade = ['Não', 
                        'Sim, com baixa probabilidade de impacto', 
                        'Sim, com média probabilidade de impacto',
                        'Sim, com alta probabilidade de impacto']
    caixa_ideacao_suicida = ['Não', 'Sim, estável', 'Sim, em risco']
    # Apenas para alunos do 3º Ano
    caixa_coerencia_enem = ['Sim', 'Não', 'Sim para ser recomendado pelo Ismart para cursinho Med']
    caixa_nota_condizente = ['Sim', 'Não', 'Sim para ser recomendado pelo Ismart para cursinho Med']


    #importar e tratar datasets
    df = ler_sheets('registro')
    bd = ler_sheets('bd')
    bd = bd.dropna(subset=['RA - NOME'])
    bd['RA'] = bd['RA'].astype(int)
    ra = None
    bd = bd[bd['Analista'] == st.session_state["authenticated_username"]]
    st.title('Formulário de Classificação')

    #Seleção do aluno
    if "authenticated_username" in st.session_state:
        st.subheader(st.session_state["authenticated_username"])
        
    ra_nome = st.selectbox(
    "Seleção do aluno",
    bd['RA - NOME'],
    index=None,
    placeholder="RA")

    if ra_nome is not None:
        try:
            ra = bd.loc[bd['RA - NOME'] == ra_nome, 'RA'].iloc[0]
        except IndexError:
            st.warning('Aluno não encontrado na base.')
            st.stop()
            
        #pessoal
        nome = bd.loc[bd['RA'] == ra, 'Nome'].iloc[0]
        escola = bd.loc[bd['RA'] == ra, 'Escola'].iloc[0]
        cidade = bd.loc[bd['RA'] == ra, 'Cidade'].iloc[0]
        media_pu = bd.loc[bd['RA'] == ra, 'Média PU'].iloc[0]
        enem_projetado = bd.loc[bd['RA'] == ra, 'ENEM Projetado'].iloc[0]
        #materias
        matematica = bd.loc[bd['RA'] == ra, 'Nota Matemática'].iloc[0]
        ingles = bd.loc[bd['RA'] == ra, 'Nota Inglês'].iloc[0]
        fisica = bd.loc[bd['RA'] == ra, 'Nota Física'].iloc[0]
        portugues = bd.loc[bd['RA'] == ra, 'Nota Português'].iloc[0]
        frances = bd.loc[bd['RA'] == ra, 'Nota Francês/Alemão e Outros'].iloc[0]
        biologia = bd.loc[bd['RA'] == ra, 'Nota Biologia'].iloc[0]
        historia = bd.loc[bd['RA'] == ra, 'Nota História'].iloc[0]
        espanhol = bd.loc[bd['RA'] == ra, 'Nota Espanhol'].iloc[0]
        ciencias = bd.loc[bd['RA'] == ra, 'Nota Ciências'].iloc[0]
        geografia = bd.loc[bd['RA'] == ra, 'Nota Geografia'].iloc[0]
        quimica = bd.loc[bd['RA'] == ra, 'Nota Química'].iloc[0]

        qtd_somas_idiomas = 0
        idiomas = 0
        if ingles != '-':
            idiomas += ingles
            qtd_somas_idiomas += 1
        if frances != '-':
            idiomas += frances
            qtd_somas_idiomas += 1
        if espanhol != '-':
            idiomas += espanhol
            qtd_somas_idiomas += 1

        qtd_somas_humanas = 0
        humanas = 0
        if geografia != '-':
            humanas += geografia
            qtd_somas_humanas += 1
        if historia != '-':
            humanas += historia
            qtd_somas_humanas += 1


        #extras
        analista = bd.loc[bd['RA'] == ra, 'Analista'].iloc[0]
        segmento = bd.loc[bd['RA'] == ra, 'Segmento'].iloc[0]
        ano = bd.loc[bd['RA'] == ra, 'Ano'].iloc[0]

        #Variaveis Registro
        if df.query(f'RA == {ra}').empty:
            registro_data_submit = None
            registro_classificacao = None
            registro_periodo = None
            registro_nomenclatura = None
            registro_resposta_argumentacao = None
            registro_resposta_rotina_estudos = None
            registro_resposta_faltas = None
            registro_resposta_atividades_extracurriculares = None
            registro_resposta_medalha = None
            registro_resposta_respeita_escola = None
            registro_resposta_atividades_obrigatorias_ismart = None
            registro_resposta_colaboracao = None
            registro_resposta_atividades_nao_obrigatorias_ismart = None
            registro_resposta_networking = None
            registro_resposta_proatividade = None
            registro_resposta_questoes_psiquicas = None
            registro_resposta_questoes_familiares = None
            registro_resposta_questoes_saude = None
            registro_resposta_ideacao_suicida = None
            registro_resposta_adaptacao_projeto = None
            registro_resposta_seguranca_profissional = None
            registro_resposta_curso_apoiado = None
            registro_resposta_nota_condizente = None
            
        if not df.query(f'RA == {ra}').empty:
            registro_data_submit = df.loc[df['RA'] == ra, 'data_submit'].iloc[0]
            registro_classificacao = df.loc[df['RA'] == ra, 'classificacao'].iloc[0]
            registro_periodo = df.loc[df['RA'] == ra, 'periodo'].iloc[0]
            registro_nomenclatura = df.loc[df['RA'] == ra, 'nomenclatura'].iloc[0]
            registro_resposta_argumentacao = df.loc[df['RA'] == ra, 'resposta_argumentacao'].iloc[0]
            registro_resposta_rotina_estudos = df.loc[df['RA'] == ra, 'resposta_rotina_estudos'].iloc[0]
            registro_resposta_faltas = df.loc[df['RA'] == ra, 'resposta_faltas'].iloc[0]
            registro_resposta_atividades_extracurriculares = df.loc[df['RA'] == ra, 'resposta_atividades_extracurriculares'].iloc[0]
            registro_resposta_medalha = df.loc[df['RA'] == ra, 'resposta_medalha'].iloc[0]
            registro_resposta_respeita_escola = df.loc[df['RA'] == ra, 'resposta_respeita_escola'].iloc[0]
            registro_resposta_atividades_obrigatorias_ismart = df.loc[df['RA'] == ra, 'resposta_atividades_obrigatorias_ismart'].iloc[0]
            registro_resposta_colaboracao = df.loc[df['RA'] == ra, 'resposta_colaboracao'].iloc[0]
            registro_resposta_atividades_nao_obrigatorias_ismart = df.loc[df['RA'] == ra, 'resposta_atividades_nao_obrigatorias_ismart'].iloc[0]
            registro_resposta_networking = df.loc[df['RA'] == ra, 'resposta_networking'].iloc[0]
            registro_resposta_proatividade = df.loc[df['RA'] == ra, 'resposta_proatividade'].iloc[0]
            registro_resposta_questoes_psiquicas = df.loc[df['RA'] == ra, 'resposta_questoes_psiquicas'].iloc[0]
            registro_resposta_questoes_familiares = df.loc[df['RA'] == ra, 'resposta_questoes_familiares'].iloc[0]
            registro_resposta_questoes_saude = df.loc[df['RA'] == ra, 'resposta_questoes_saude'].iloc[0]
            registro_resposta_ideacao_suicida = df.loc[df['RA'] == ra, 'resposta_ideacao_suicida'].iloc[0]
            registro_resposta_adaptacao_projeto = df.loc[df['RA'] == ra, 'resposta_adaptacao_projeto'].iloc[0]
            registro_resposta_seguranca_profissional = df.loc[df['RA'] == ra, 'resposta_seguranca_profissional'].iloc[0]
            registro_resposta_curso_apoiado = df.loc[df['RA'] == ra, 'resposta_curso_apoiado'].iloc[0]
            registro_resposta_nota_condizente = df.loc[df['RA'] == ra, 'resposta_nota_condizente'].iloc[0]
            

        #Dados pessoais
        st.title('Aluno')
        col1, col2 = st.columns([2, 5])
        col1.metric("RA", ra, border=True)
        col2.metric("Nome", nome, border=True)
        st.divider()
        st.title('Local')
        col1, col2 = st.columns(2)
        col1.metric("Escola", escola, border=True)
        col2.metric("Cidade", cidade, border=True)


        #Média das disciplinas
        st.divider()
        st.title('Notas')
        col1, col2, col3 = st.columns(3)
        col1.metric("Matemática", matematica, border=True)
        col2.metric("Português", portugues, border=True)
        col3.metric("Humanas", f"{humanas/qtd_somas_humanas:.2f}", border=True)
        col1, col2, col3 = st.columns(3)
        col1.metric("Idiomas", f"{idiomas/qtd_somas_idiomas:.2f}", border=True)
        col2.metric("Ciências Naturais", biologia, border=True)
        col1, col2 = st.columns(2)
        col1.metric("Enem Projetado", enem_projetado, border=True)
        col2.metric("Média PU", media_pu, border=True)

        #Dados Extras
        st.divider()
        col1, col2 = st.columns(2)
        col1.metric("Analista", analista, border=True)
        col2.metric("Segmento", segmento, border=True)

        #formulario
        st.divider()
        with st.form(key='formulario'):
            # Preencha
            st.header('Preencha o formulário')
            # Período
            st.subheader('Período')
            periodo = st.selectbox("Período",caixa_periodo,index=retornar_indice(lista=caixa_periodo,variavel=registro_periodo),placeholder="Período")
            nomenclatura = st.selectbox("Nomenclatura",caixa_nomenclatura,index=retornar_indice(lista=caixa_nomenclatura,variavel=registro_nomenclatura),placeholder="Nomenclatura")
            # Acadêmico
            st.divider()
            st.subheader('Acadêmico')
            resposta_argumentacao = st.radio('**O aluno traz conteúdos consistentes nas suas argumentações/interações (com analistas, escola parceira, outros)?**', caixa_argumentacao, index=retornar_indice(lista=caixa_argumentacao,variavel=registro_resposta_argumentacao))
            resposta_rotina_estudos = st.radio('**O aluno tem uma rotina de estudos adequada as suas necessidades?**', caixa_rotina_estudos, index=retornar_indice(lista=caixa_rotina_estudos,variavel=registro_resposta_rotina_estudos), horizontal=True)
            resposta_faltas = st.radio('**O aluno está com número de faltas e/ou atrasos que compromete o seu desempenho acadêmico?**', caixa_sim_nao, index=retornar_indice(lista=caixa_sim_nao,variavel=registro_resposta_faltas), horizontal=True)
            resposta_atividades_extracurriculares = st.radio('**O aluno faz atividades acadêmicas extracurriculares com vias a desenvolver seu talento acadêmico? (olimpiadas, projetos de iniciação cientifica, programação, Cultura inglesa/Inglês/Prep)**', caixa_atividades_extracurriculares, index=retornar_indice(lista=caixa_atividades_extracurriculares,variavel=registro_resposta_atividades_extracurriculares), horizontal=True)
            resposta_medalha = st.radio('**O aluno possui medalha em alguma olimpiada do conhecimento (oficial) ou é TOP 3 em competições acadêmicas no ano corrente?**', caixa_sim_nao, index=retornar_indice(lista=caixa_sim_nao,variavel=registro_resposta_medalha), horizontal=True)
            # Perfil
            st.divider()
            st.subheader('Perfil')
            resposta_respeita_escola = st.radio('**O aluno respeita as normas da escola parceira?**', caixa_nunca_eventualmente_sempre, index=retornar_indice(lista=caixa_nunca_eventualmente_sempre,variavel=registro_resposta_respeita_escola), horizontal=True)
            resposta_atividades_obrigatorias_ismart = st.radio('**O aluno aproveira as atividades abrigatórias oferecidas pelo Ismart? Qualidade do envolvimento nas atividades (pressupoe participação em 100% das atividades)**', caixa_nunca_eventualmente_sempre, index=retornar_indice(lista=caixa_nunca_eventualmente_sempre,variavel=registro_resposta_atividades_obrigatorias_ismart), horizontal=True)
            resposta_colaboracao = st.radio('**É colaborativo com os amigos? Oferece ajuda?**', caixa_nunca_eventualmente_sempre, index=retornar_indice(lista=caixa_nunca_eventualmente_sempre,variavel=registro_resposta_colaboracao), horizontal=True)
            resposta_atividades_nao_obrigatorias_ismart = st.radio('**O aluno aproveita e participa das atividades não obrigatórias do Ismart?**', caixa_nunca_eventualmente_sempre, index=retornar_indice(lista=caixa_nunca_eventualmente_sempre,variavel=registro_resposta_atividades_nao_obrigatorias_ismart), horizontal=True)
            resposta_networking = st.radio('**O aluno cultiva relação na escola parceira e em outros contextos que a escola possibilita?**', caixa_networking, index=retornar_indice(lista=caixa_networking,variavel=registro_resposta_networking), horizontal=True)
            resposta_proatividade = st.radio('**O aluno é pró-ativo, ou seja, traz questionamentos críticos, sugestões, problemas, soluções, dúvidas?**', caixa_nunca_eventualmente_sempre, index=retornar_indice(lista=caixa_nunca_eventualmente_sempre,variavel=registro_resposta_proatividade), horizontal=True)
            # Psicológico
            st.divider()
            st.subheader('Psicológico/Questões Familiares/Saúde')
            resposta_questoes_psiquicas = st.radio('**O aluno apresenta questões psíquicas que podem vir a impactar seu desenvolvimento no projeto?**', caixa_fragilidade, index=retornar_indice(lista=caixa_fragilidade,variavel=registro_resposta_questoes_psiquicas))
            resposta_questoes_familiares = st.radio('**O aluno apresenta questões familiares que podem vir a impactar seu desenvolvimento no projeto?**', caixa_fragilidade, index=retornar_indice(lista=caixa_fragilidade,variavel=registro_resposta_questoes_familiares))
            resposta_questoes_saude = st.radio('**O aluno apresenta questões de saúde que podem vir a impactar seu desenvolvimento no projeto?**', caixa_fragilidade, index=retornar_indice(lista=caixa_fragilidade,variavel=registro_resposta_questoes_saude))
            resposta_ideacao_suicida = st.radio('**O aluno apresenta ideação suicida?**', caixa_ideacao_suicida, index=retornar_indice(lista=caixa_ideacao_suicida,variavel=registro_resposta_ideacao_suicida), horizontal=True)
            #questão apenas para 8 e 1 anos
            if ano == 8 or ano == 1:
                st.divider()
                st.subheader('Questão de 8°/1° ano')
                resposta_adaptacao_projeto = st.radio('**O aluno conseguiu se adaptar bem ao projeto?**', caixa_sim_nao, index=retornar_indice(lista=caixa_sim_nao,variavel=registro_resposta_adaptacao_projeto))
            else:
                resposta_adaptacao_projeto = '-'
            #questão apenas para 2 ano
            if ano == 2:
                st.divider()
                st.subheader('Questão de 2° ano')
                resposta_seguranca_profissional = st.radio('**O aluno está seguro em seu processo de escolha profissional?**', caixa_sim_nao, index=retornar_indice(lista=caixa_sim_nao,variavel=registro_resposta_seguranca_profissional))
            else: 
                resposta_seguranca_profissional = '-'
            #questão apenas para 3 ano
            if ano == 3:
                st.divider()
                st.subheader('Questões de 3° ano')
                resposta_curso_apoiado = st.radio('**O aluno escolheu um curso apoiado pelo Ismart?**', caixa_sim_nao, index=retornar_indice(lista=caixa_sim_nao,variavel=registro_resposta_curso_apoiado))
                resposta_nota_condizente = st.radio('**O aluno tem desempenho acadêmico e demais notas (ENEM e Prova Única) condizentes com sua estratégia de vestibulares?**', caixa_nota_condizente, index=retornar_indice(lista=caixa_nota_condizente,variavel=registro_resposta_nota_condizente))
                resposta_seguranca_profissional = st.radio('**O aluno está seguro com a escolha profissional?**', caixa_sim_nao, index=retornar_indice(lista=caixa_sim_nao,variavel=registro_resposta_seguranca_profissional))
            else:
                resposta_curso_apoiado = '-'
                resposta_nota_condizente = '-'
                resposta_seguranca_profissional = '-'

            #Botão registrar
            submit_button = st.form_submit_button(label='REGISTRAR')
            if submit_button:
                if not periodo or not nomenclatura or not resposta_argumentacao or not resposta_rotina_estudos or not resposta_faltas or not resposta_atividades_extracurriculares or not resposta_medalha or not resposta_respeita_escola or not resposta_atividades_obrigatorias_ismart or not resposta_colaboracao or not resposta_atividades_nao_obrigatorias_ismart or not resposta_networking or not resposta_proatividade or not resposta_questoes_psiquicas or not resposta_questoes_familiares or not resposta_questoes_saude or not resposta_ideacao_suicida or not resposta_adaptacao_projeto or not resposta_seguranca_profissional or not resposta_curso_apoiado or not resposta_nota_condizente:
                    st.warning('Preencha o formuário')
                    st.stop()
                else:
                    df = ler_sheets('registro')
                    if not df.query(f'RA == {ra}').empty:
                        df = df[df['RA'] != ra]

                    for i in range(0, 3):
                        try:
                            #inserir classificação
                            df_insert = pd.DataFrame([{
                                                    'RA': ra, 
                                                    'nome': nome, 
                                                    'data_submit': datetime.now(fuso_horario), 
                                                    'classificacao': classificar(), 
                                                    'periodo': periodo,	
                                                    'nomenclatura': nomenclatura,	
                                                    'resposta_argumentacao': resposta_argumentacao,	
                                                    'resposta_rotina_estudos': resposta_rotina_estudos,	
                                                    'resposta_faltas': resposta_faltas,	
                                                    'resposta_atividades_extracurriculares': resposta_atividades_extracurriculares,	
                                                    'resposta_medalha': resposta_medalha,	
                                                    'resposta_respeita_escola': resposta_respeita_escola,	
                                                    'resposta_atividades_obrigatorias_ismart': resposta_atividades_obrigatorias_ismart,	
                                                    'resposta_colaboracao': resposta_colaboracao,	
                                                    'resposta_atividades_nao_obrigatorias_ismart': resposta_atividades_nao_obrigatorias_ismart,	
                                                    'resposta_networking': resposta_networking,	
                                                    'resposta_proatividade': resposta_proatividade,	
                                                    'resposta_questoes_psiquicas': resposta_questoes_psiquicas,	
                                                    'resposta_questoes_familiares': resposta_questoes_familiares,	
                                                    'resposta_questoes_saude': resposta_questoes_saude,	
                                                    'resposta_ideacao_suicida': resposta_ideacao_suicida,	
                                                    'resposta_adaptacao_projeto': resposta_adaptacao_projeto,	
                                                    'resposta_seguranca_profissional': resposta_seguranca_profissional,	
                                                    'resposta_curso_apoiado': resposta_curso_apoiado,	
                                                    'resposta_nota_condizente': resposta_nota_condizente,	
                                                    }])
                            updared_df = pd.concat([df, df_insert], ignore_index=True)


                            conn.update(worksheet="registro", data=updared_df)
                        except:
                            sleep(2)
                            continue

                        #verificar
                        sleep(3)
                        df = ler_sheets('registro')
                        if not df.query(f'RA == {ra}').empty:
                            st.success('Registrado com sucesso!')
                            sleep(2)
                            break
                        else:
                            st.error('Erro ao registrar')
                            sleep(1)
                            continue
                st.rerun()
                
                