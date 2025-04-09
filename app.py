
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
from time import sleep
import pytz

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
        st.text_input("Senha", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input("Usuário", on_change=password_entered, key="username")
        st.text_input("Senha", type="password", on_change=password_entered, key="password")
        st.error("😕 Usuário desconhecido ou senha incorreta.")
        return False
    else:
        # Password correct.
        return True


if check_password():
    st.set_page_config(layout="wide")

    #ler planilha
    conn = st.connection("gsheets", type=GSheetsConnection)

    def ler_sheets(pagina):
        for i in range(0, 10):
            try:
                df = conn.read(worksheet=pagina, ttl=1)
                return df
            except:
                sleep(3)
                pass
        st.error('Erro ao conectar com o sheets')
        if st.button('Tentar novamente'):
            st.rerun()
        st.stop()
        
    def pontuar(resposta, lista):
        try:
            for index, elemento in enumerate(lista):
                if elemento == resposta:
                    return int(index + 1)    
        except:
            return st.error('Erro Interno No Formulário')

    caixa_classificacao = ['Destaque', 'Pré-Destaque', 'Mediano', 'Atenção', 'Crítico', 'Crítico OP']
    caixa_justificativa_classificacao = ['Acadêmico', 'Perfil', 'Familiar', 'Saúde', 'Psicológico', 'Curso não apoiado', 'Curso concorrido', 'Escolha frágil']

    def classificar(media_calibrada, portugues, matematica, humanas, idiomas, ciencias_naturais, resposta_faltas, ano, caixa_nota_condizente, resposta_adaptacao_projeto , resposta_nota_condizente, resposta_seguranca_profissional, resposta_curso_apoiado , caixa_fragilidade, resposta_questoes_saude, resposta_questoes_familiares, resposta_questoes_psiquicas, resposta_ideacao_suicida , caixa_ideacao_suicida , resposta_argumentacao, resposta_rotina_estudos, resposta_atividades_extracurriculares, resposta_respeita_escola, resposta_atividades_obrigatorias_ismart, resposta_colaboracao, resposta_atividades_nao_obrigatorias_ismart, resposta_networking, resposta_proatividade,caixa_argumentacao,caixa_rotina_estudos,caixa_nao_sim,caixa_atividades_extracurriculares,caixa_nunca_eventualmente_sempre,caixa_networking, caixa_classificacao, caixa_justificativa_classificacao):
        classificacao = ''
        motivo = ''
        
        #Classificação Psicológico/Questões Familiares/Saúde
            #Psicológico - critico
        if resposta_ideacao_suicida == caixa_ideacao_suicida[1] or resposta_ideacao_suicida == caixa_ideacao_suicida[2]:
            classificacao = 'Crítico'
            motivo += 'Psicológico'+'; '
        elif resposta_questoes_psiquicas == caixa_fragilidade[3]:
            classificacao = 'Crítico'
            motivo += 'Psicológico'+'; '
            #Familiares - critico
        if resposta_questoes_familiares == caixa_fragilidade[3]:
            classificacao = 'Crítico'
            motivo += 'Familiar'+'; '
            #Saúde - critico
        if resposta_questoes_saude == caixa_fragilidade[3]:
            classificacao = 'Crítico'
            motivo += 'Saúde'+'; '   
        if classificacao != 'Crítico':
                #Psicológico - Atenção
            if resposta_questoes_psiquicas == caixa_fragilidade[2]:
                classificacao = 'Atenção'
                motivo += 'Psicológico'+'; '
                #Familiares - Atenção
            if resposta_questoes_familiares == caixa_fragilidade[2]:
                classificacao = 'Atenção'
                motivo += 'Familiar'+'; '
                #Saúde - Atenção
            if resposta_questoes_saude == caixa_fragilidade[2]:
                classificacao = 'Atenção'
                motivo += 'Saúde'+'; ' 
            # opcional 2° ano - Atenção
            if ano == '2º EM': 
                if resposta_seguranca_profissional == caixa_nao_sim[0]:
                    classificacao = 'Atenção'
                    motivo += 'Escolha frágil'+'; '
        # opcional 3° ano - Critico OP
        if classificacao == '':
            if ano == '3º EM':
                if resposta_curso_apoiado == caixa_nao_sim[0]:
                    classificacao = 'Crítico OP'
                    motivo += 'Curso não apoiado'+'; ' 
                if resposta_seguranca_profissional == caixa_nao_sim[0]:
                    classificacao = 'Crítico OP'
                    motivo += 'Escolha frágil'+'; ' 
                if resposta_nota_condizente == caixa_nota_condizente[0]:
                    classificacao = 'Crítico OP'
                    motivo += 'Curso concorrido'+'; ' 
        # Número de faltas
        if classificacao == 'Atenção' or classificacao == 'Crítico' or classificacao == '':
            if resposta_faltas == caixa_nao_sim[1]:
                classificacao = 'Crítico'
                motivo += 'Acadêmico'+'; ' 
                motivo += 'Perfil'+'; ' 
                motivo = motivo[:-2]
                return classificacao, motivo
        
        #Nota escolar 
        critico_escolar = 0
        atencao_escolar = 0
        mediano_escolar = 0
        destaque_escolar = 0
        materias = [portugues, matematica, humanas, idiomas, ciencias_naturais]
        
        #Contagem das matérias
        for i in materias:
            if i < (media_calibrada - 1):
                critico_escolar += 1
            elif (media_calibrada - 1) <= i and i < media_calibrada:
                atencao_escolar += 1
            elif media_calibrada <= i and i < (media_calibrada + 2):
                mediano_escolar += 1
            elif i > (media_calibrada + 2):
                destaque_escolar += 1
        
        #status_nota
        if critico_escolar > 0 or atencao_escolar > 2:
            status_nota_escolar = 0
        elif atencao_escolar == 1 or atencao_escolar == 2:
            status_nota_escolar = 1
        elif mediano_escolar > 0 and critico_escolar == 0 and atencao_escolar == 0 and destaque_escolar < 3:
            status_nota_escolar = 2
        elif mediano_escolar >= 1 and destaque_escolar > 2:
            status_nota_escolar = 3
        elif destaque_escolar == 5:
            status_nota_escolar = 4
                
        #Pontuacao academica
        pontuacao_perfil = 0
        pontuacao_perfil += pontuar(resposta_respeita_escola , caixa_nunca_eventualmente_sempre)
        pontuacao_perfil += pontuar(resposta_atividades_obrigatorias_ismart , caixa_nunca_eventualmente_sempre)
        pontuacao_perfil += pontuar(resposta_colaboracao , caixa_nunca_eventualmente_sempre)
        pontuacao_perfil += pontuar(resposta_atividades_nao_obrigatorias_ismart , caixa_nunca_eventualmente_sempre)
        pontuacao_perfil += pontuar(resposta_networking , caixa_networking)
        pontuacao_perfil += pontuar(resposta_proatividade , caixa_nunca_eventualmente_sempre)
        if pontuacao_perfil < 11:
            status_perfil = 0
        else:
            status_perfil = 1
        #Pontuação Perfil 
        pontuacao_academico = 0
        pontuacao_academico += pontuar(resposta_argumentacao, caixa_argumentacao)
        pontuacao_academico += pontuar(resposta_rotina_estudos , caixa_rotina_estudos)
        pontuacao_academico += pontuar(resposta_atividades_extracurriculares , caixa_atividades_extracurriculares)
        if pontuacao_academico < 6:
            status_academico = 0
        else:
            status_academico = 1

        #Classificação notas
        if status_nota_escolar == 0 and (classificacao == 'Crítico' or classificacao == 'Atenção'):
            classificacao = 'Crítico'
            motivo += 'Acadêmico'+'; '
        elif status_nota_escolar == 1 and classificacao == 'Atenção':
            motivo += 'Acadêmico'+'; '
        elif classificacao == '':
            if status_nota_escolar == 0 or (status_nota_escolar == 1 and status_perfil == 0 and status_academico == 0):
                classificacao = 'Crítico'                                      
                motivo = 'Acadêmico'+'; '
                if status_perfil == 0:
                    motivo += 'Perfil'+'; '
            elif status_nota_escolar == 1 or (status_nota_escolar == 2 and status_perfil ==0 and status_academico == 0):
                classificacao = 'Atenção'
                motivo = 'Acadêmico'+'; '
                if status_perfil == 0:
                    motivo += 'Perfil'+'; '
            elif status_nota_escolar == 2:
                classificacao = 'Mediano'
                motivo = 'Acadêmico'+'; '
                if status_perfil == 0:
                    motivo += 'Perfil'+'; '
            elif status_nota_escolar == 3:
                if status_perfil == 1:
                    classificacao = 'Pré-Destaque'
                    motivo = 'Acadêmico'+'; '
                    if status_academico == 1:
                        motivo += 'Perfil'+'; '
                else:  
                    classificacao = 'Atenção'    
                    motivo = 'Perfil'+'; '
            elif status_nota_escolar == 4:
                if status_perfil == 1:
                    classificacao = 'Destaque'
                    motivo = 'Acadêmico'+'; '
                    if status_academico == 1:
                        motivo += 'Perfil'+'; '
                else:  
                    classificacao = 'Atenção'    
                    motivo = 'Perfil'+'; '
        
        motivo = motivo[:-2]
        return classificacao, motivo

    def retornar_indice(lista, variavel):
        if variavel == None:
            return None
        try:
            for indice, valor in enumerate(lista):
                if valor == variavel:
                    return indice
        except:
            return None
        
    def registrar(df_insert, aba, coluna_apoio, ra):
        df = ler_sheets(aba)
        #Limpar linhas repetidas
        if type(ra) == list:
            for i in ra:
                ra_referencia = i
                df = df[df['RA'] != i]
        else:
            df = df[df['RA'] != ra]

        #REGISTRAR
        for a in range(1, 4):
            try:
                updared_df = pd.concat([df, df_insert], ignore_index=True)
                conn.update(worksheet="registro", data=updared_df)
            except:
                sleep(2)
                continue

        #VERIFICAR
        sleep(2)
        for a in range(1, 4):
            df = ler_sheets(aba)
            sleep(1)
            if type(ra) != list:
                if not df.query(f'RA == {ra} and {coluna_apoio} == {coluna_apoio}').empty:
                    st.success('Sucesso!')
                    break
                else:
                    st.warning('Erro')
                    sleep(1)
                    continue
            else:
                if not df.query(f'RA == {ra_referencia} and {coluna_apoio} == {coluna_apoio}').empty:
                    st.success('Sucesso!')
                    break
                else:
                    st.warning('Erro')
                    sleep(1)
                    continue
        st.rerun()

    #importar e tratar datasets
    df = ler_sheets('registro')
    bd = ler_sheets('bd')
    bd = bd.dropna(subset=['RA - NOME'])
    bd['RA'] = bd['RA'].astype(int)
    ra = None
    bd['apoio_registro'] = bd['apoio_registro'].astype(str)
    bd['apoio_registro_final'] = bd['apoio_registro_final'].astype(str)
    bd = bd.sort_values(by=['apoio_registro_final','apoio_registro'], ascending = False)
    #df['RA'] = df['RA'].astype(int)
    df_login = ler_sheets('login')
    df_escola = ler_sheets('media_calibrada')

    st.title('Formulário de Classificação')
    #Seleção do aluno
    if df_login.query(f'login == "{st.session_state["authenticated_username"]}"')["cargo"].iloc[0] == "coordenação":
        df_coord = df.query('confirmacao_classificacao_orientadora == "Não" and confirmacao_classificacao_coordenacao != "Sim" and confirmacao_classificacao_coordenacao != "Não"')
        bd_segmentado = bd.query('apoio_registro == "Não" and apoio_registro_final != "Não" and apoio_registro_final != "Sim"')
        cidade_login = df_login.query(f'login == "{st.session_state["authenticated_username"]}"')["cidade"].iloc[0]
        bd_segmentado = bd_segmentado.query(f'Cidade == "{cidade_login}"')
        # filtros bd
        col1, col2, col3, col4 = st.columns(4)
        # Aplique os filtros
        valores_segmento = col1.multiselect("Filtro de Segmento", bd_segmentado['Segmento'].unique())
        if valores_segmento:
            bd_segmentado = bd_segmentado.query(f"Segmento in {valores_segmento}")
        valores_escola = col2.multiselect("Filtro de Escola", bd_segmentado['Escola'].unique())
        if valores_escola:
            bd_segmentado = bd_segmentado.query(f"Escola in {valores_escola}")
        valores_ano = col3.multiselect("Filtro de Ano", bd_segmentado['Ano'].unique())
        if valores_ano:
            bd_segmentado = bd_segmentado.query(f"Ano in {valores_ano}")
        selecao_orientadora = col4.multiselect("Filtro Orientadora", bd_segmentado['Orientadora'].unique())
        if selecao_orientadora:
            bd_segmentado = bd_segmentado.query(f"Orientadora in {selecao_orientadora}")
        st.divider()
        ra_nome_bd = bd_segmentado['RA - NOME - FINAL']
        df_coord = df_coord[df_coord['RA'].isin(bd_segmentado['RA'])]

        ra_nome = st.selectbox(
        "Seleção dos Alunos",
        ra_nome_bd,
        index=None,
        placeholder="RA")

        # progresso
        qtd_praca = bd.query(f"Cidade == '{cidade_login}'").shape[0]
        qtd_registrados_praca = bd.query(f"Cidade == '{cidade_login}'")
        qtd_registrados_praca = qtd_registrados_praca.query("apoio_registro == 'Não' or apoio_registro == 'Sim'").shape[0]

        qtd_alunos = bd.shape[0]
        qtd_alunos_registrados = bd.query(f"apoio_registro == 'Não' or apoio_registro == 'Sim'").shape[0]

        try:
            st.progress(qtd_alunos_registrados/qtd_alunos, f'Status Preenchimento das orientadoras de Todas as Praças: **{qtd_alunos_registrados}/{qtd_alunos}**')
            st.progress(qtd_registrados_praca/qtd_praca, f'Status Preenchimento das orientadoras da Praça {cidade_login}: **{qtd_registrados_praca}/{qtd_praca}**')
        except ZeroDivisionError:
            st.error('Zero Resultados')
    else:
        cidade_login = df_login.query(f'login == "{st.session_state["authenticated_username"]}"')["cidade"].iloc[0]
        bd_segmentado = bd.query(f"Orientadora == '{st.session_state["authenticated_username"]}'")

        # filtros
        col1, col2, col3 = st.columns(3)
        # Aplique os filtros
        valores_segmento = col1.multiselect("Filtro de Segmento", bd_segmentado['Segmento'].unique())
        if valores_segmento:
            bd_segmentado = bd_segmentado.query(f"Segmento in {valores_segmento}")
        valores_escola = col2.multiselect("Filtro de Escola", bd_segmentado['Escola'].unique())
        if valores_escola:
            bd_segmentado = bd_segmentado.query(f"Escola in {valores_escola}")
        valores_ano = col3.multiselect("Filtro de Ano", bd_segmentado['Ano'].unique())
        if valores_ano:
            bd_segmentado = bd_segmentado.query(f"Ano in {valores_ano}")
        st.divider()

        ra_nome_bd = bd_segmentado.query("apoio_registro != 'Não' and apoio_registro != 'Sim'")['RA - NOME']
        ra_nome = st.selectbox(
        "Seleção dos Alunos",
        ra_nome_bd,
        index=None,
        placeholder="RA")
        if 'ra_nome' not in st.session_state:
            st.session_state['ra_nome'] = ra_nome
        if st.session_state['ra_nome'] != ra_nome:
            try:
                del st.session_state['classificacao_atual']
                del st.session_state['motivo_atual']
                del st.session_state['confirmacao_alterada']
            except:
                pass
            del st.session_state['ra_nome']
            
        # progresso
        qtd_alunos_registrados_orientadoras = bd_segmentado.query(f"apoio_registro == 'Não' or apoio_registro == 'Sim'").shape[0]
        try:
            st.progress(qtd_alunos_registrados_orientadoras/bd_segmentado.shape[0], f'Você registrou: **{qtd_alunos_registrados_orientadoras}/{bd_segmentado.shape[0]}**')
        except ZeroDivisionError:
            st.error('Zero Resultados')

    if ra_nome is not None:
        if df_login.query(f'login == "{st.session_state["authenticated_username"]}"')["cargo"].iloc[0] == "coordenação":
            try:
                st.session_state["ra"] = bd.loc[bd['RA - NOME - FINAL'] == ra_nome, 'RA'].iloc[0]
                ra = st.session_state["ra"]
            except IndexError:
                st.warning('Aluno não encontrado na base.')
                st.stop()
        else:
            try:
                st.session_state["ra"] = bd.loc[bd['RA - NOME'] == ra_nome, 'RA'].iloc[0]
                ra = st.session_state["ra"]
            except IndexError:
                st.warning('Aluno não encontrado na base.')
                st.stop()
            
            
        #pessoal
        nome = bd.loc[bd['RA'] == ra, 'Nome'].iloc[0]
        escola = bd.loc[bd['RA'] == ra, 'Escola'].iloc[0]
        cidade = bd.loc[bd['RA'] == ra, 'Cidade'].iloc[0]

        #materias
        matematica = bd.loc[bd['RA'] == ra, 'Nota Matemática'].iloc[0]
        ingles = bd.loc[bd['RA'] == ra, 'Nota Inglês'].iloc[0]
        portugues = bd.loc[bd['RA'] == ra, 'Nota Português'].iloc[0]
        outras_linguas = bd.loc[bd['RA'] == ra, 'Nota Francês/Alemão e Outros'].iloc[0]
        historia = bd.loc[bd['RA'] == ra, 'Nota História'].iloc[0]
        espanhol = bd.loc[bd['RA'] == ra, 'Nota Espanhol'].iloc[0]
        geografia = bd.loc[bd['RA'] == ra, 'Nota Geografia'].iloc[0]
        biologia = bd.loc[bd['RA'] == ra, 'Nota Biologia'].iloc[0]
        quimica = bd.loc[bd['RA'] == ra, 'Nota Química'].iloc[0]    
        fisica = bd.loc[bd['RA'] == ra, 'Nota Física'].iloc[0]

        try:
            media_calibrada = df_escola.loc[df_escola['escola'] == escola, 'media_calibrada'].iloc[0]
        except:
            st.error('Escola do aluno não encontrada na planilha')
            st.stop()
        
        if matematica == '-':
            matematica = media_calibrada
        if portugues == '-':
            portugues = media_calibrada
        
        qtd_somas_ciencias_naturais = 0
        ciencias_naturais = 0

        if fisica != '-':
            ciencias_naturais += fisica
            qtd_somas_ciencias_naturais += 1
        if quimica != '-':
            ciencias_naturais += quimica
            qtd_somas_ciencias_naturais += 1
        if biologia != '-':
            ciencias_naturais += biologia
            qtd_somas_ciencias_naturais += 1

        try:
            ciencias_naturais = ciencias_naturais/qtd_somas_ciencias_naturais
        except:
            ciencias_naturais = media_calibrada
        
        qtd_somas_idiomas = 0
        idiomas = 0
        if ingles != '-':
            idiomas += ingles
            qtd_somas_idiomas += 1
        if outras_linguas != '-':
            idiomas += outras_linguas
            qtd_somas_idiomas += 1
        if espanhol != '-':
            idiomas += espanhol
            qtd_somas_idiomas += 1
        
        try:
            idiomas = idiomas/qtd_somas_idiomas
        except:
            idiomas = media_calibrada

        qtd_somas_humanas = 0
        humanas = 0
        if geografia != '-':
            humanas += geografia
            qtd_somas_humanas += 1
        if historia != '-':
            humanas += historia
            qtd_somas_humanas += 1

        try:
            humanas = humanas/qtd_somas_humanas
        except:
            humanas = media_calibrada
        
        #extras
        orientadora = bd.loc[bd['RA'] == ra, 'Orientadora'].iloc[0]
        segmento = bd.loc[bd['RA'] == ra, 'Segmento'].iloc[0]
        ano = bd.loc[bd['RA'] == ra, 'Ano'].iloc[0]
        # periodo = bd.loc[bd['RA'] == ra, 'periodo'].iloc[0]
        # nomenclatura = bd.loc[bd['RA'] == ra, 'nomenclatura'].iloc[0]
            
        #Dados pessoais
        st.title('Aluno')
        col1, col2 = st.columns([2, 5])
        col1.metric("RA", ra, border=True)
        col2.metric("Nome", nome, border=True)
        st.divider()
        #Segmento
        st.header('Segmento')
        col1, col2 = st.columns(2)
        col1.metric("Orientadora", orientadora, border=True)
        col2.metric("Segmento", segmento, border=True)
        # st.divider()
        # st.header('Local')
        # col1, col2 = st.columns(2)
        # col1.metric("Escola", escola, border=True)
        # col2.metric("Cidade", cidade, border=True)
        #Média das disciplinas
        st.divider()
        st.header('Notas')
        st.subheader(f'Média calibrada: {media_calibrada:.2f}')
        col1, col2, col3 = st.columns(3)
        col1.metric("Matemática", f'{matematica:.2f}', border=True)
        col2.metric("Português", f'{portugues:.2f}', border=True)
        try:
            col3.metric("Humanas", f"{humanas:.2f}", border=True)
        except:
            col3.metric("Humanas", f"{0}", border=True)
        col1, col2, col3 = st.columns(3)
        try:
            col1.metric("Idiomas", f"{idiomas:.2f}", border=True)
        except:
            col1.metric("Idiomas", f"{0}", border=True)
        col2.metric("Ciências Naturais", f'{ciencias_naturais:.2f}', border=True)
        with st.expander("Notas detalhadas"):
            st.subheader('Ciências Naturais')
            col1, col2, col3 = st.columns(3)
            try:
                col1.metric('Biologia', f'{biologia:.2f}', border=True)
            except:
                col1.metric('Biologia', biologia, border=True)
            try:
                col2.metric('Química', f'{quimica:.2f}', border=True)
            except:
                col2.metric('Química', quimica, border=True)
            try:
                col3.metric('Física', f'{fisica:.2f}', border=True)
            except:
                col3.metric('Física', fisica, border=True)
            st.subheader('Idiomas')
            col1, col2, col3 = st.columns(3)
            try:
                col1.metric('Inglês', f'{ingles:.2f}', border=True)
            except:
                col1.metric('Inglês', ingles, border=True)
            try:
                col2.metric('Outras Línguas', f'{outras_linguas:.2f}', border=True)
            except:
                col2.metric('Outras Línguas', outras_linguas, border=True)
            try:
                col3.metric('Espanhol', f'{espanhol:.2f}', border=True)
            except:
                col3.metric('Espanhol', espanhol, border=True)
            st.subheader('Humanas')
            col1, col2 = st.columns(2)
            try:
                col1.metric('Geografia', f'{geografia:.2f}', border=True)
            except:
                col1.metric('Geografia', geografia, border=True)
            try:
                col2.metric('História', f'{historia:.2f}', border=True)
            except:
                col2.metric('História', historia, border=True)

        # col1, col2 = st.columns(2)
        # col1.metric("Período", f'{periodo:.2f}, border=True)
        # col2.metric("Nomenclatura", f'{nomenclatura:.2f}, border=True)


        #formulario
        st.divider()
        caixa_sim_nao = ['Não', 'Sim']
        caixa_classificacao = ['Destaque', 'Pré-Destaque', 'Mediano', 'Atenção', 'Crítico', 'Crítico OP']
        caixa_reversao = ["Alta", "Média", "Baixa"]
        caixa_justificativa_classificacao = ['Acadêmico', 'Perfil', 'Familiar', 'Saúde', 'Psicológico', 'Curso não apoiado', 'Curso concorrido', 'Escolha frágil']
        if df_login.query(f'login == "{st.session_state["authenticated_username"]}"')["cargo"].iloc[0] == "coordenação":
            #colunas
            classificacao_automatica = df.loc[df['RA'] == ra, 'classificacao_automatica'].iloc[0]
            motivo_classificao_automatica = df.loc[df['RA'] == ra, 'motivo_classificao_automatica'].iloc[0]
            nova_classificacao_orientadora = df.loc[df['RA'] == ra, 'nova_classificacao_orientadora'].iloc[0]
            novo_motivo_classificacao_orientadora = df.loc[df['RA'] == ra, 'novo_motivo_classificacao_orientadora'].iloc[0]
            nova_justificativa_classificacao_orientadora = df.loc[df['RA'] == ra, 'nova_justificativa_classificacao_orientadora'].iloc[0]
            reversao = df.loc[df['RA'] == ra, 'reversao'].iloc[0]
            descricao_caso = df.loc[df['RA'] == ra, 'descricao_caso'].iloc[0]
            plano_intervencao = df.loc[df['RA'] == ra, 'plano_intervencao'].iloc[0]
            
            st.divider()
          

            #Formulario
            st.title('Confirmar classificação')
            col1, col2 = st.columns(2)
            col1.metric("Classificação\nAutomatica", classificacao_automatica, border=True)
            col2.metric("Motivo Classificação\nAutomatica", motivo_classificao_automatica, border=True)
            st.divider()
            col1, col2 = st.columns(2)
            col1.metric("Classificação", nova_classificacao_orientadora, border=True)
            col2.metric("Motivo Classificação", novo_motivo_classificacao_orientadora, border=True)
            with st.expander("Justificativa e Detalhes"):
                st.metric("Justificativa", nova_justificativa_classificacao_orientadora, border=True)
                st.metric("Reversao", reversao, border=True)
                st.metric("Descricao do Caso", descricao_caso, border=True)
                st.metric("Plano de Intervencao", plano_intervencao, border=True)

            resposta_confirmar_classificacao = st.selectbox("Confirma classificação?",caixa_sim_nao,index=1,placeholder="Confirma classificação?")            

            if resposta_confirmar_classificacao == 'Sim':
                resposta_classificacao_final = nova_classificacao_orientadora
                resposta_motivo_final = novo_motivo_classificacao_orientadora
                resposta_justificativa_classificacao_coord = 'nan'
            else:
                resposta_classificacao_final = classificacao_automatica
                resposta_motivo_final = motivo_classificao_automatica
                resposta_justificativa_classificacao_coord = st.text_area(placeholder='Justifique', label='Justifique (opcional)')

            if st.button(label='REGISTRAR'):
                if not resposta_justificativa_classificacao_coord:
                    resposta_justificativa_classificacao_coord = 'nan'

                df_insert = pd.DataFrame([{
                                            'RA': ra, 
                                            'nome': nome, 
                                            'data_submit': datetime.now(fuso_horario), 
                                            'resposta_argumentacao':df.loc[df['RA'] == ra, 'resposta_argumentacao'].iloc[0],
                                            'resposta_rotina_estudos':df.loc[df['RA'] == ra, 'resposta_rotina_estudos'].iloc[0],
                                            'resposta_faltas':	df.loc[df['RA'] == ra, 'resposta_faltas'].iloc[0],
                                            'resposta_atividades_extracurriculares':df.loc[df['RA'] == ra, 'resposta_atividades_extracurriculares'].iloc[0],
                                            'resposta_respeita_escola':df.loc[df['RA'] == ra, 'resposta_respeita_escola'].iloc[0],
                                            'resposta_atividades_obrigatorias_ismart':df.loc[df['RA'] == ra, 'resposta_atividades_obrigatorias_ismart'].iloc[0],
                                            'resposta_colaboracao':df.loc[df['RA'] == ra, 'resposta_colaboracao'].iloc[0],
                                            'resposta_atividades_nao_obrigatorias_ismart':df.loc[df['RA'] == ra, 'resposta_atividades_nao_obrigatorias_ismart'].iloc[0],
                                            'resposta_networking':df.loc[df['RA'] == ra, 'resposta_networking'].iloc[0],
                                            'resposta_proatividade':df.loc[df['RA'] == ra, 'resposta_proatividade'].iloc[0],
                                            'resposta_questoes_psiquicas':df.loc[df['RA'] == ra, 'resposta_questoes_psiquicas'].iloc[0],
                                            'resposta_questoes_familiares':df.loc[df['RA'] == ra, 'resposta_questoes_familiares'].iloc[0],
                                            'resposta_questoes_saude':df.loc[df['RA'] == ra, 'resposta_questoes_saude'].iloc[0],
                                            'resposta_ideacao_suicida':df.loc[df['RA'] == ra, 'resposta_ideacao_suicida'].iloc[0],
                                            'resposta_adaptacao_projeto':df.loc[df['RA'] == ra, 'resposta_adaptacao_projeto'].iloc[0],
                                            'resposta_seguranca_profissional':df.loc[df['RA'] == ra, 'resposta_seguranca_profissional'].iloc[0],
                                            'resposta_curso_apoiado':df.loc[df['RA'] == ra, 'resposta_curso_apoiado'].iloc[0],
                                            'resposta_nota_condizente':df.loc[df['RA'] == ra, 'resposta_nota_condizente'].iloc[0],
                                            'classificacao_automatica':df.loc[df['RA'] == ra, 'classificacao_automatica'].iloc[0],
                                            'motivo_classificao_automatica':df.loc[df['RA'] == ra, 'motivo_classificao_automatica'].iloc[0],
                                            'confirmacao_classificacao_orientadora':df.loc[df['RA'] == ra, 'confirmacao_classificacao_orientadora'].iloc[0],
                                            'nova_classificacao_orientadora':df.loc[df['RA'] == ra, 'nova_classificacao_orientadora'].iloc[0],
                                            'novo_motivo_classificacao_orientadora':df.loc[df['RA'] == ra, 'novo_motivo_classificacao_orientadora'].iloc[0],
                                            'nova_justificativa_classificacao_orientadora':df.loc[df['RA'] == ra, 'nova_justificativa_classificacao_orientadora'].iloc[0],                                            
                                            'reversao':	df.loc[df['RA'] == ra, 'reversao'].iloc[0],  
                                            'descricao_caso':df.loc[df['RA'] == ra, 'descricao_caso'].iloc[0],    
                                            'plano_intervencao':df.loc[df['RA'] == ra, 'plano_intervencao'].iloc[0],    
                                            'confirmacao_classificacao_coordenacao': resposta_confirmar_classificacao,
                                            'justificativa_classificacao_coord': resposta_justificativa_classificacao_coord,
                                            'classificacao_final': resposta_classificacao_final,
                                            'motivo_final': resposta_motivo_final
                                            }])
                registrar(df_insert, 'registro', 'confirmacao_classificacao_coordenacao', ra)
        if df.query(f"RA == {ra} and confirmacao_classificacao_orientadora == confirmacao_classificacao_orientadora").empty:
            #Variaveis Registro
            if df.query(f'RA == {ra}').empty:
                registro_data_submit = None
                registro_classificacao = None
                registro_motivo_classificao_automatica = None
                registro_resposta_argumentacao = None
                registro_resposta_rotina_estudos = None
                registro_resposta_faltas = None
                registro_resposta_atividades_extracurriculares = None
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
                registro_classificacao = df.loc[df['RA'] == ra, 'classificacao_automatica'].iloc[0]
                registro_motivo_classificao_automatica = df.loc[df['RA'] == ra, 'motivo_classificao_automatica'].iloc[0]
                registro_resposta_argumentacao = df.loc[df['RA'] == ra, 'resposta_argumentacao'].iloc[0]
                registro_resposta_rotina_estudos = df.loc[df['RA'] == ra, 'resposta_rotina_estudos'].iloc[0]
                registro_resposta_faltas = df.loc[df['RA'] == ra, 'resposta_faltas'].iloc[0]
                registro_resposta_atividades_extracurriculares = df.loc[df['RA'] == ra, 'resposta_atividades_extracurriculares'].iloc[0]
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

            with st.form(key='formulario'):
                # Acadêmico
                caixa_argumentacao = ['Superficial - apenas reproduz', 
                                    'Argumenta e se posiciona, trazendo sua opinião de forma consistente', 
                                    'Sempre traz elementos além dos solicitados']
                caixa_rotina_estudos = ['Não', 'Precisa melhorar', 'Sim']
                caixa_atividades_extracurriculares = ['Nenhuma', 'Uma', 'Mais de uma']
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
                caixa_nota_condizente = ['Não', 'Sim', 'Sim para ser recomendado pelo Ismart para cursinho Med']
                # Preencha
                st.header('Preencha o formulário')
                # Acadêmico
                st.divider()
                st.subheader('Acadêmico')
                resposta_argumentacao = st.radio('**O aluno traz conteúdos consistentes nas suas argumentações/interações (com orientadoras, escola parceira, outros)?**', caixa_argumentacao, index=retornar_indice(lista=caixa_argumentacao,variavel=registro_resposta_argumentacao))
                resposta_rotina_estudos = st.radio('**O aluno tem uma rotina de estudos adequada as suas necessidades?**', caixa_rotina_estudos, index=retornar_indice(lista=caixa_rotina_estudos,variavel=registro_resposta_rotina_estudos), horizontal=True)
                resposta_atividades_extracurriculares = st.radio('**O aluno faz atividades acadêmicas extracurriculares com vias a desenvolver seu talento acadêmico? (olimpiadas, projetos de iniciação cientifica, programação, Cultura inglesa/Inglês/Prep)**', caixa_atividades_extracurriculares, index=retornar_indice(lista=caixa_atividades_extracurriculares,variavel=registro_resposta_atividades_extracurriculares), horizontal=True)
                resposta_faltas = st.radio('**O aluno está com número de faltas e/ou atrasos que compromete o seu desempenho acadêmico?**', caixa_sim_nao, index=retornar_indice(lista=caixa_sim_nao,variavel=registro_resposta_faltas), horizontal=True)
                # Perfil
                st.divider()
                st.subheader('Perfil')
                resposta_respeita_escola = st.radio('**O aluno respeita as normas da escola parceira?**', caixa_nunca_eventualmente_sempre, index=retornar_indice(lista=caixa_nunca_eventualmente_sempre,variavel=registro_resposta_respeita_escola), horizontal=True)
                resposta_atividades_obrigatorias_ismart = st.radio('**O aluno aproveita as atividades obrigatórias oferecidas pelo Ismart? Qualidade do envolvimento nas atividades (pressupõe participação em 100% das atividades)**', caixa_nunca_eventualmente_sempre, index=retornar_indice(lista=caixa_nunca_eventualmente_sempre,variavel=registro_resposta_atividades_obrigatorias_ismart), horizontal=True)
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
                if ano == '8º EF' or ano == '1º EM':
                    st.divider()
                    st.subheader('Questão de 8°/1° ano')
                    resposta_adaptacao_projeto = st.radio('**O aluno conseguiu se adaptar bem ao projeto?**', caixa_sim_nao, index=retornar_indice(lista=caixa_sim_nao,variavel=registro_resposta_adaptacao_projeto))
                else:
                    resposta_adaptacao_projeto = '-'
                #questão apenas para 2 ano
                if ano == '2º EM':
                    st.divider()
                    st.subheader('Questão de 2° ano')
                    resposta_seguranca_profissional = st.radio('**O aluno está seguro em seu processo de escolha profissional?**', caixa_sim_nao, index=retornar_indice(lista=caixa_sim_nao,variavel=registro_resposta_seguranca_profissional))
                else: 
                    resposta_seguranca_profissional = '-'
                #questão apenas para 3 ano
                if ano == '3º EM':
                    st.divider()
                    st.subheader('Questões de 3° ano')
                    resposta_curso_apoiado = st.radio('**O aluno escolheu um curso apoiado pelo Ismart?**', caixa_sim_nao, index=retornar_indice(lista=caixa_sim_nao,variavel=registro_resposta_curso_apoiado))
                    resposta_nota_condizente = st.radio('**O aluno tem desempenho acadêmico e demais notas (ENEM e Prova Única) condizentes com sua estratégia de vestibulares?**', caixa_nota_condizente, index=retornar_indice(lista=caixa_nota_condizente,variavel=registro_resposta_nota_condizente))
                    resposta_seguranca_profissional = st.radio('**O aluno está seguro com a escolha profissional?**', caixa_sim_nao, index=retornar_indice(lista=caixa_sim_nao,variavel=registro_resposta_seguranca_profissional))
                else:
                    resposta_curso_apoiado = '-'
                    resposta_nota_condizente = '-'
                    if ano != '2º EM':
                        resposta_seguranca_profissional = '-'

                #Botão registrar
                submit_button = st.form_submit_button(label='SALVAR')
                if submit_button:
                    if not resposta_argumentacao or not resposta_rotina_estudos or not resposta_atividades_extracurriculares or not resposta_faltas:
                        st.warning('Questões em **Acadêmico** do formulário não estão preenchidas')
                        st.stop()
                    if not resposta_respeita_escola or not resposta_atividades_obrigatorias_ismart or not resposta_colaboracao or not resposta_atividades_nao_obrigatorias_ismart or not resposta_networking or not resposta_proatividade:
                        st.warning('Questões em **Perfil** do formulário não estão preenchidas')
                        st.stop()
                    if not resposta_questoes_psiquicas or not resposta_questoes_familiares or not resposta_questoes_saude or not resposta_ideacao_suicida:
                        st.warning('Questões em **Psicológico/Questões Familiares/Saúde** do formulário não estão preenchidas')
                        st.stop()
                    if not resposta_adaptacao_projeto or not resposta_seguranca_profissional or not resposta_curso_apoiado or not resposta_nota_condizente:
                        st.warning('**Questões de ano** do formulário não estão preenchidas')
                        st.stop()
                    else:    
                        #inserir classificação
                        df_insert = pd.DataFrame([{
                                                'RA': ra, 
                                                'nome': nome, 
                                                'data_submit': datetime.now(fuso_horario), 
                                                'resposta_argumentacao': resposta_argumentacao,	
                                                'resposta_rotina_estudos': resposta_rotina_estudos,	
                                                'resposta_faltas': resposta_faltas,	
                                                'resposta_atividades_extracurriculares': resposta_atividades_extracurriculares,	
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
                                                'classificacao_automatica': classificar(media_calibrada, portugues, matematica, humanas, idiomas, ciencias_naturais, resposta_faltas, ano, caixa_nota_condizente, resposta_adaptacao_projeto , resposta_nota_condizente, resposta_seguranca_profissional, resposta_curso_apoiado , caixa_fragilidade, resposta_questoes_saude, resposta_questoes_familiares, resposta_questoes_psiquicas, resposta_ideacao_suicida , caixa_ideacao_suicida , resposta_argumentacao, resposta_rotina_estudos, resposta_atividades_extracurriculares, resposta_respeita_escola, resposta_atividades_obrigatorias_ismart, resposta_colaboracao, resposta_atividades_nao_obrigatorias_ismart, resposta_networking, resposta_proatividade,caixa_argumentacao,caixa_rotina_estudos,caixa_sim_nao,caixa_atividades_extracurriculares,caixa_nunca_eventualmente_sempre,caixa_networking, caixa_classificacao, caixa_justificativa_classificacao)[0], 
                                                'motivo_classificao_automatica': classificar(media_calibrada, portugues, matematica, humanas, idiomas, ciencias_naturais, resposta_faltas, ano, caixa_nota_condizente, resposta_adaptacao_projeto , resposta_nota_condizente, resposta_seguranca_profissional, resposta_curso_apoiado , caixa_fragilidade, resposta_questoes_saude, resposta_questoes_familiares, resposta_questoes_psiquicas, resposta_ideacao_suicida , caixa_ideacao_suicida , resposta_argumentacao, resposta_rotina_estudos, resposta_atividades_extracurriculares, resposta_respeita_escola, resposta_atividades_obrigatorias_ismart, resposta_colaboracao, resposta_atividades_nao_obrigatorias_ismart, resposta_networking, resposta_proatividade,caixa_argumentacao,caixa_rotina_estudos,caixa_sim_nao,caixa_atividades_extracurriculares,caixa_nunca_eventualmente_sempre,caixa_networking, caixa_classificacao, caixa_justificativa_classificacao)[1],
                                                }])
                        registrar(df_insert, 'registro', 'classificacao_automatica', ra)
            if not df.query(f"RA == {ra} and classificacao_automatica == classificacao_automatica").empty:
                #colunas
                classificacao_automatica = df.loc[df['RA'] == ra, 'classificacao_automatica'].iloc[0]
                motivo_classificao_automatica = df.loc[df['RA'] == ra, 'motivo_classificao_automatica'].iloc[0]
                nova_classificacao_orientadora = df.loc[df['RA'] == ra, 'nova_classificacao_orientadora'].iloc[0]
                novo_motivo_classificacao_orientadora = df.loc[df['RA'] == ra, 'novo_motivo_classificacao_orientadora'].iloc[0]
                nova_justificativa_classificacao_orientadora = df.loc[df['RA'] == ra, 'nova_justificativa_classificacao_orientadora'].iloc[0]
                reversao = df.loc[df['RA'] == ra, 'reversao'].iloc[0]
                descricao_caso = df.loc[df['RA'] == ra, 'descricao_caso'].iloc[0]
                plano_intervencao = df.loc[df['RA'] == ra, 'plano_intervencao'].iloc[0]
                confirmacao_classificacao_coordenacao = df.loc[df['RA'] == ra, 'confirmacao_classificacao_coordenacao'].iloc[0]
                classificacao_final = df.loc[df['RA'] == ra, 'classificacao_final'].iloc[0]
                motivo_final = df.loc[df['RA'] == ra, 'motivo_final'].iloc[0]

                if 'confirmacao_alterada' not in st.session_state:
                    st.session_state['confirmacao_alterada'] = 'Não'

                if st.session_state['confirmacao_alterada'] == 'Não':
                    st.session_state['classificacao_atual'] = classificacao_automatica
                    st.session_state['motivo_atual'] = motivo_classificao_automatica

                #Formulario
                st.title('Confirmar classificação')
                st.metric("Classificação", st.session_state['classificacao_atual'], border=True)
                st.metric("Motivo", st.session_state['motivo_atual'], border=True)
                
                if st.session_state['confirmacao_alterada'] == 'Sim':
                    resposta_confirmar_classificacao = 'Não'
                else:
                    resposta_confirmar_classificacao = st.selectbox("Confirma classificação?",caixa_sim_nao,index=1,placeholder="Confirma classificação?")

                if resposta_confirmar_classificacao == 'Não' and st.session_state['confirmacao_alterada'] == 'Não':
                    with st.form(key='formulario_registrar_orientadora'):
                        resposta_nova_classificacao_orientadora = st.selectbox("Nova classificação",caixa_classificacao,index=None,placeholder="Nova classificação")
                        resposta_novo_motivo_classificacao_orientadora_lista = st.multiselect("Novo motivo da classificação",caixa_justificativa_classificacao,placeholder="Novo motivo da classificação")
                        resposta_novo_motivo_classificacao_orientadora = ''
                        for i in resposta_novo_motivo_classificacao_orientadora_lista:
                            resposta_novo_motivo_classificacao_orientadora += f'{i}; '
                        resposta_novo_motivo_classificacao_orientadora = resposta_novo_motivo_classificacao_orientadora[:-2]
                        resposta_nova_justificativa_classificacao_orientadora = st.text_area(placeholder='Justifique a mudança de classificação', label='Justifique a mudança de classificação')

                        submit_button = st.form_submit_button(label='ALTERAR')
                        if submit_button:  
                            if not resposta_nova_classificacao_orientadora or not resposta_novo_motivo_classificacao_orientadora or not resposta_nova_justificativa_classificacao_orientadora:
                                st.warning('Preencha os dados de classificação')
                                st.stop()
                            else:
                                st.session_state['classificacao_atual'] = resposta_nova_classificacao_orientadora
                                st.session_state['motivo_atual'] = resposta_novo_motivo_classificacao_orientadora
                                st.session_state['confirmacao_alterada'] = 'Sim'
                                df_insert = pd.DataFrame([{
                                                        'RA': ra, 
                                                        'nome': nome, 
                                                        'data_submit': datetime.now(fuso_horario), 
                                                        'resposta_argumentacao': resposta_argumentacao,	
                                                        'resposta_rotina_estudos': resposta_rotina_estudos,	
                                                        'resposta_faltas': resposta_faltas,	
                                                        'resposta_atividades_extracurriculares': resposta_atividades_extracurriculares,	
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
                                                        'classificacao_automatica': classificar(media_calibrada, portugues, matematica, humanas, idiomas, ciencias_naturais, resposta_faltas, ano, caixa_nota_condizente, resposta_adaptacao_projeto , resposta_nota_condizente, resposta_seguranca_profissional, resposta_curso_apoiado , caixa_fragilidade, resposta_questoes_saude, resposta_questoes_familiares, resposta_questoes_psiquicas, resposta_ideacao_suicida , caixa_ideacao_suicida , resposta_argumentacao, resposta_rotina_estudos, resposta_atividades_extracurriculares, resposta_respeita_escola, resposta_atividades_obrigatorias_ismart, resposta_colaboracao, resposta_atividades_nao_obrigatorias_ismart, resposta_networking, resposta_proatividade,caixa_argumentacao,caixa_rotina_estudos,caixa_sim_nao,caixa_atividades_extracurriculares,caixa_nunca_eventualmente_sempre,caixa_networking, caixa_classificacao, caixa_justificativa_classificacao)[0], 
                                                        'motivo_classificao_automatica': classificar(media_calibrada, portugues, matematica, humanas, idiomas, ciencias_naturais, resposta_faltas, ano, caixa_nota_condizente, resposta_adaptacao_projeto , resposta_nota_condizente, resposta_seguranca_profissional, resposta_curso_apoiado , caixa_fragilidade, resposta_questoes_saude, resposta_questoes_familiares, resposta_questoes_psiquicas, resposta_ideacao_suicida , caixa_ideacao_suicida , resposta_argumentacao, resposta_rotina_estudos, resposta_atividades_extracurriculares, resposta_respeita_escola, resposta_atividades_obrigatorias_ismart, resposta_colaboracao, resposta_atividades_nao_obrigatorias_ismart, resposta_networking, resposta_proatividade,caixa_argumentacao,caixa_rotina_estudos,caixa_sim_nao,caixa_atividades_extracurriculares,caixa_nunca_eventualmente_sempre,caixa_networking, caixa_classificacao, caixa_justificativa_classificacao)[1],
                                                        'confirmacao_classificacao_orientadora': '',
                                                        'nova_classificacao_orientadora' : resposta_nova_classificacao_orientadora,
                                                        'novo_motivo_classificacao_orientadora': resposta_novo_motivo_classificacao_orientadora,
                                                        'nova_justificativa_classificacao_orientadora': resposta_nova_justificativa_classificacao_orientadora,
                                                        }])
                                registrar(df_insert, 'registro', 'nova_classificacao_orientadora', ra) 
                else:
                    with st.form(key='formulario_descricao'):
                        resposta_nova_classificacao_orientadora = df.loc[df['RA'] == ra, 'nova_classificacao_orientadora'].iloc[0]
                        resposta_novo_motivo_classificacao_orientadora = df.loc[df['RA'] == ra, 'novo_motivo_classificacao_orientadora'].iloc[0]
                        resposta_nova_justificativa_classificacao_orientadora = df.loc[df['RA'] == ra, 'nova_justificativa_classificacao_orientadora'].iloc[0]
                        
                        if st.session_state['classificacao_atual'] == 'Crítico':
                            resposta_reversao = st.radio('**Reversão**', caixa_reversao, index=retornar_indice(lista=caixa_reversao,variavel=reversao), horizontal=True)
                            resposta_descricao_caso = st.text_input(placeholder='Descrição do caso', label='Descrição do caso')
                            resposta_plano_intervencao = st.text_input(placeholder='Plano de intervenção', label='Plano de intervenção')
                        elif st.session_state['classificacao_atual'] == 'Atenção':
                            resposta_reversao = '-'
                            resposta_descricao_caso = '-'
                            resposta_plano_intervencao = st.text_input(placeholder='Plano de intervenção', label='Plano de intervenção')
                        else:
                            resposta_reversao = '-'
                            resposta_descricao_caso = '-'
                            resposta_plano_intervencao = '-'
                    
                        if cidade_login == 'SP':
                            caixa_tier = ['2c', '2i', '3c', '3i', '4']

                            resposta_tier = st.multiselect('Deseja Indicar Tiers?', caixa_tier, placeholder="Tiers")
                            tier = ''

                            for i in resposta_tier:
                                tier += f'{i}; '
                            tier = tier[:-2]

                        else:
                            tier = '-'
                        submit_button = st.form_submit_button(label='REGISTRAR')
                        if submit_button:
                            if not resposta_reversao:    
                                st.warning('Preencha os dados da reversão')
                                st.stop()
                            elif not resposta_plano_intervencao:
                                st.warning('Preencha os dados da intervenção')
                                st.stop()
                            else:
                                if resposta_confirmar_classificacao == 'Sim':
                                    df_insert = pd.DataFrame([{
                                                        'RA': ra, 
                                                        'nome': nome, 
                                                        'data_submit': datetime.now(fuso_horario), 
                                                        'resposta_argumentacao': resposta_argumentacao,	
                                                        'resposta_rotina_estudos': resposta_rotina_estudos,	
                                                        'resposta_faltas': resposta_faltas,	
                                                        'resposta_atividades_extracurriculares': resposta_atividades_extracurriculares,	
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
                                                        'classificacao_automatica': classificar(media_calibrada, portugues, matematica, humanas, idiomas, ciencias_naturais, resposta_faltas, ano, caixa_nota_condizente, resposta_adaptacao_projeto , resposta_nota_condizente, resposta_seguranca_profissional, resposta_curso_apoiado , caixa_fragilidade, resposta_questoes_saude, resposta_questoes_familiares, resposta_questoes_psiquicas, resposta_ideacao_suicida , caixa_ideacao_suicida , resposta_argumentacao, resposta_rotina_estudos, resposta_atividades_extracurriculares, resposta_respeita_escola, resposta_atividades_obrigatorias_ismart, resposta_colaboracao, resposta_atividades_nao_obrigatorias_ismart, resposta_networking, resposta_proatividade,caixa_argumentacao,caixa_rotina_estudos,caixa_sim_nao,caixa_atividades_extracurriculares,caixa_nunca_eventualmente_sempre,caixa_networking, caixa_classificacao, caixa_justificativa_classificacao)[0], 
                                                        'motivo_classificao_automatica': classificar(media_calibrada, portugues, matematica, humanas, idiomas, ciencias_naturais, resposta_faltas, ano, caixa_nota_condizente, resposta_adaptacao_projeto , resposta_nota_condizente, resposta_seguranca_profissional, resposta_curso_apoiado , caixa_fragilidade, resposta_questoes_saude, resposta_questoes_familiares, resposta_questoes_psiquicas, resposta_ideacao_suicida , caixa_ideacao_suicida , resposta_argumentacao, resposta_rotina_estudos, resposta_atividades_extracurriculares, resposta_respeita_escola, resposta_atividades_obrigatorias_ismart, resposta_colaboracao, resposta_atividades_nao_obrigatorias_ismart, resposta_networking, resposta_proatividade,caixa_argumentacao,caixa_rotina_estudos,caixa_sim_nao,caixa_atividades_extracurriculares,caixa_nunca_eventualmente_sempre,caixa_networking, caixa_classificacao, caixa_justificativa_classificacao)[1],
                                                        'confirmacao_classificacao_orientadora': resposta_confirmar_classificacao,
                                                        'nova_classificacao_orientadora' : '-',
                                                        'novo_motivo_classificacao_orientadora': '-',
                                                        'nova_justificativa_classificacao_orientadora': '-',
                                                        'reversao': resposta_reversao,
                                                        'descricao_caso': resposta_descricao_caso,
                                                        'plano_intervencao': resposta_plano_intervencao,
                                                        'tier': tier,
                                                        'confirmacao_classificacao_coordenacao': '-',
                                                        'justificativa_classificacao_coord': '-',
                                                        'classificacao_final': classificar(media_calibrada, portugues, matematica, humanas, idiomas, ciencias_naturais, resposta_faltas, ano, caixa_nota_condizente, resposta_adaptacao_projeto , resposta_nota_condizente, resposta_seguranca_profissional, resposta_curso_apoiado , caixa_fragilidade, resposta_questoes_saude, resposta_questoes_familiares, resposta_questoes_psiquicas, resposta_ideacao_suicida , caixa_ideacao_suicida , resposta_argumentacao, resposta_rotina_estudos, resposta_atividades_extracurriculares, resposta_respeita_escola, resposta_atividades_obrigatorias_ismart, resposta_colaboracao, resposta_atividades_nao_obrigatorias_ismart, resposta_networking, resposta_proatividade,caixa_argumentacao,caixa_rotina_estudos,caixa_sim_nao,caixa_atividades_extracurriculares,caixa_nunca_eventualmente_sempre,caixa_networking, caixa_classificacao, caixa_justificativa_classificacao)[0],
                                                        'motivo_final': classificar(media_calibrada, portugues, matematica, humanas, idiomas, ciencias_naturais, resposta_faltas, ano, caixa_nota_condizente, resposta_adaptacao_projeto , resposta_nota_condizente, resposta_seguranca_profissional, resposta_curso_apoiado , caixa_fragilidade, resposta_questoes_saude, resposta_questoes_familiares, resposta_questoes_psiquicas, resposta_ideacao_suicida , caixa_ideacao_suicida , resposta_argumentacao, resposta_rotina_estudos, resposta_atividades_extracurriculares, resposta_respeita_escola, resposta_atividades_obrigatorias_ismart, resposta_colaboracao, resposta_atividades_nao_obrigatorias_ismart, resposta_networking, resposta_proatividade,caixa_argumentacao,caixa_rotina_estudos,caixa_sim_nao,caixa_atividades_extracurriculares,caixa_nunca_eventualmente_sempre,caixa_networking, caixa_classificacao, caixa_justificativa_classificacao)[1]
                                                        }])
                                    registrar(df_insert, 'registro', 'confirmacao_classificacao_orientadora', ra)   
                                elif resposta_confirmar_classificacao == 'Não':
                                    df_insert = pd.DataFrame([{
                                                        'RA': ra, 
                                                        'nome': nome, 
                                                        'data_submit': datetime.now(fuso_horario), 
                                                        'resposta_argumentacao': resposta_argumentacao,	
                                                        'resposta_rotina_estudos': resposta_rotina_estudos,	
                                                        'resposta_faltas': resposta_faltas,	
                                                        'resposta_atividades_extracurriculares': resposta_atividades_extracurriculares,	
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
                                                        'classificacao_automatica': classificar(media_calibrada, portugues, matematica, humanas, idiomas, ciencias_naturais, resposta_faltas, ano, caixa_nota_condizente, resposta_adaptacao_projeto , resposta_nota_condizente, resposta_seguranca_profissional, resposta_curso_apoiado , caixa_fragilidade, resposta_questoes_saude, resposta_questoes_familiares, resposta_questoes_psiquicas, resposta_ideacao_suicida , caixa_ideacao_suicida , resposta_argumentacao, resposta_rotina_estudos, resposta_atividades_extracurriculares, resposta_respeita_escola, resposta_atividades_obrigatorias_ismart, resposta_colaboracao, resposta_atividades_nao_obrigatorias_ismart, resposta_networking, resposta_proatividade,caixa_argumentacao,caixa_rotina_estudos,caixa_sim_nao,caixa_atividades_extracurriculares,caixa_nunca_eventualmente_sempre,caixa_networking, caixa_classificacao, caixa_justificativa_classificacao)[0], 
                                                        'motivo_classificao_automatica': classificar(media_calibrada, portugues, matematica, humanas, idiomas, ciencias_naturais, resposta_faltas, ano, caixa_nota_condizente, resposta_adaptacao_projeto , resposta_nota_condizente, resposta_seguranca_profissional, resposta_curso_apoiado , caixa_fragilidade, resposta_questoes_saude, resposta_questoes_familiares, resposta_questoes_psiquicas, resposta_ideacao_suicida , caixa_ideacao_suicida , resposta_argumentacao, resposta_rotina_estudos, resposta_atividades_extracurriculares, resposta_respeita_escola, resposta_atividades_obrigatorias_ismart, resposta_colaboracao, resposta_atividades_nao_obrigatorias_ismart, resposta_networking, resposta_proatividade,caixa_argumentacao,caixa_rotina_estudos,caixa_sim_nao,caixa_atividades_extracurriculares,caixa_nunca_eventualmente_sempre,caixa_networking, caixa_classificacao, caixa_justificativa_classificacao)[1],
                                                        'confirmacao_classificacao_orientadora': resposta_confirmar_classificacao,
                                                        'nova_classificacao_orientadora' : nova_classificacao_orientadora,
                                                        'novo_motivo_classificacao_orientadora': novo_motivo_classificacao_orientadora,
                                                        'nova_justificativa_classificacao_orientadora': nova_justificativa_classificacao_orientadora,
                                                        'reversao': resposta_reversao,
                                                        'descricao_caso': resposta_descricao_caso,
                                                        'plano_intervencao': resposta_plano_intervencao,
                                                        'tier': tier
                                                        }])
                                    registrar(df_insert, 'registro', 'confirmacao_classificacao_orientadora', ra) 
                                
    elif not ra_nome and df_login.query(f'login == "{st.session_state["authenticated_username"]}"')["cargo"].iloc[0] == "coordenação":
        with st.form(key='tabela_editavel'):
            colunas_nao_editaveis = df.columns.to_list()
            colunas_nao_editaveis.remove('confirmacao_classificacao_coordenacao')
            colunas_nao_editaveis.remove('justificativa_classificacao_coord')
            df_coord['confirmacao_classificacao_coordenacao'] = df_coord['confirmacao_classificacao_coordenacao'].astype(str)
            df_coord['justificativa_classificacao_coord'] = df_coord['justificativa_classificacao_coord'].astype(str)

            # Configure o data editor
            edited_df = st.data_editor(
                df_coord[['confirmacao_classificacao_coordenacao', 'justificativa_classificacao_coord','RA', 'nome', 'classificacao_automatica', 'motivo_classificao_automatica', 'nova_classificacao_orientadora','novo_motivo_classificacao_orientadora','nova_justificativa_classificacao_orientadora','reversao','descricao_caso','plano_intervencao']],
                column_config={
                    "confirmacao_classificacao_coordenacao": st.column_config.SelectboxColumn(
                        "Confirmar?",
                        help="Selecione Sim ou Não",
                        options=['Sim', 'Não'],
                        required=True
                    ),
                    "justificativa_classificacao_coord": st.column_config.TextColumn(
                        "Justifique",
                        required=False
                    ),
                    "classificacao_automatica": st.column_config.TextColumn(
                        "Classificação Automatica",
                        required=False
                    ),
                    "motivo_classificao_automatica": st.column_config.TextColumn(
                        "Motivo Classificação Automatica",
                        required=False
                    ),
                    "nova_classificacao_orientadora": st.column_config.TextColumn(
                        "Classificação da Orientadora",
                        required=False
                    ),
                    "novo_motivo_classificacao_orientadora": st.column_config.TextColumn(
                        "Motivo Classificação da Orientadora",
                        required=False
                    ),
                    "nova_justificativa_classificacao_orientadora": st.column_config.TextColumn(
                        "Justificativa Classificação",
                        required=False
                    ),
                    "reversao": st.column_config.TextColumn(
                        "Reversão",
                        required=False
                    ),
                    "descricao_caso": st.column_config.TextColumn(
                        "Descrição do caso",
                        required=False
                    ),
                    "plano_intervencao": st.column_config.TextColumn(
                        "Plano de intervenção",
                        required=False
                    )
                },
                disabled=colunas_nao_editaveis,
                hide_index=True,
            )
            submit_button = st.form_submit_button(label='REGISTRAR')
            
        if submit_button:
            #filtrar do df_tabela_editavel aqueles com confirmar 
            df_tabela_editavel = edited_df.loc[edited_df['confirmacao_classificacao_coordenacao'].isin(['Sim', 'Não'])]
            
            if df_tabela_editavel.shape[0] == 0:
                st.warning('Revise ao menos um aluno antes de salvar')
            else:
                df_insert = pd.DataFrame()
                for ra in df_tabela_editavel['RA']:
                    nome = df.loc[df['RA'] == ra, 'nome'].iloc[0]
                    resposta_argumentacao = df.loc[df['RA'] == ra, 'resposta_argumentacao'].iloc[0]
                    resposta_rotina_estudos = df.loc[df['RA'] == ra, 'resposta_rotina_estudos'].iloc[0]
                    resposta_faltas = df.loc[df['RA'] == ra, 'resposta_faltas'].iloc[0]
                    resposta_atividades_extracurriculares = df.loc[df['RA'] == ra, 'resposta_atividades_extracurriculares'].iloc[0]
                    resposta_respeita_escola = df.loc[df['RA'] == ra, 'resposta_respeita_escola'].iloc[0]
                    resposta_atividades_obrigatorias_ismart = df.loc[df['RA'] == ra, 'resposta_atividades_obrigatorias_ismart'].iloc[0]
                    resposta_colaboracao = df.loc[df['RA'] == ra, 'resposta_colaboracao'].iloc[0]
                    resposta_atividades_nao_obrigatorias_ismart = df.loc[df['RA'] == ra, 'resposta_atividades_nao_obrigatorias_ismart'].iloc[0]
                    resposta_networking = df.loc[df['RA'] == ra, 'resposta_networking'].iloc[0]
                    resposta_proatividade = df.loc[df['RA'] == ra, 'resposta_proatividade'].iloc[0]
                    resposta_questoes_psiquicas = df.loc[df['RA'] == ra, 'resposta_questoes_psiquicas'].iloc[0]
                    resposta_questoes_familiares = df.loc[df['RA'] == ra, 'resposta_questoes_familiares'].iloc[0]
                    resposta_questoes_saude = df.loc[df['RA'] == ra, 'resposta_questoes_saude'].iloc[0]
                    resposta_ideacao_suicida = df.loc[df['RA'] == ra, 'resposta_ideacao_suicida'].iloc[0]
                    resposta_adaptacao_projeto = df.loc[df['RA'] == ra, 'resposta_adaptacao_projeto'].iloc[0]
                    resposta_seguranca_profissional = df.loc[df['RA'] == ra, 'resposta_seguranca_profissional'].iloc[0]
                    resposta_curso_apoiado = df.loc[df['RA'] == ra, 'resposta_curso_apoiado'].iloc[0]
                    resposta_nota_condizente = df.loc[df['RA'] == ra, 'resposta_nota_condizente'].iloc[0]
                    classificacao_automatica = df.loc[df['RA'] == ra, 'classificacao_automatica'].iloc[0]
                    motivo_classificao_automatica = df.loc[df['RA'] == ra, 'motivo_classificao_automatica'].iloc[0]
                    confirmacao_classificacao_orientadora = df.loc[df['RA'] == ra, 'confirmacao_classificacao_orientadora'].iloc[0]
                    nova_classificacao_orientadora = df.loc[df['RA'] == ra, 'nova_classificacao_orientadora'].iloc[0]
                    novo_motivo_classificacao_orientadora = df.loc[df['RA'] == ra, 'novo_motivo_classificacao_orientadora'].iloc[0]
                    nova_justificativa_classificacao_orientadora = df.loc[df['RA'] == ra, 'nova_justificativa_classificacao_orientadora'].iloc[0]
                    reversao = df.loc[df['RA'] == ra, 'reversao'].iloc[0]
                    descricao_caso = df.loc[df['RA'] == ra, 'descricao_caso'].iloc[0]
                    plano_intervencao = df.loc[df['RA'] == ra, 'plano_intervencao'].iloc[0]
                    tier = df.loc[df['RA'] == ra, 'tier'].iloc[0]
                    
                    
                    confirmacao_classificacao_coordenacao = df_tabela_editavel.loc[df_tabela_editavel['RA'] == ra, 'confirmacao_classificacao_coordenacao'].iloc[0]
                    justificativa_classificacao_coord = df_tabela_editavel.loc[df_tabela_editavel['RA'] == ra, 'justificativa_classificacao_coord'].iloc[0]
                    if confirmacao_classificacao_coordenacao == 'Sim':
                        classificacao_final = nova_classificacao_orientadora
                        motivo_final = novo_motivo_classificacao_orientadora
                    elif confirmacao_classificacao_coordenacao == 'Não':
                        classificacao_final = classificacao_automatica
                        motivo_final = motivo_classificao_automatica

                    nova_linha = pd.DataFrame([{
                        'RA': ra,
                        'nome': nome, 
                        'data_submit': datetime.now(fuso_horario), 
                        'resposta_argumentacao': resposta_argumentacao,	
                        'resposta_rotina_estudos': resposta_rotina_estudos,	
                        'resposta_faltas': resposta_faltas,	
                        'resposta_atividades_extracurriculares': resposta_atividades_extracurriculares,	
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
                        'classificacao_automatica': classificacao_automatica, 
                        'motivo_classificao_automatica': motivo_classificao_automatica,
                        'confirmacao_classificacao_orientadora': confirmacao_classificacao_orientadora,
                        'nova_classificacao_orientadora' : nova_classificacao_orientadora,
                        'novo_motivo_classificacao_orientadora': novo_motivo_classificacao_orientadora,
                        'nova_justificativa_classificacao_orientadora': nova_justificativa_classificacao_orientadora,
                        'reversao': reversao,
                        'descricao_caso': descricao_caso,
                        'plano_intervencao': plano_intervencao,
                        'tier': tier,
                        'confirmacao_classificacao_coordenacao': confirmacao_classificacao_coordenacao,
                        'justificativa_classificacao_coord': justificativa_classificacao_coord,
                        'classificacao_final': classificacao_final,
                        'motivo_final': motivo_final
                        }])
                    
                    df_insert = pd.concat([df_insert, nova_linha], ignore_index=True)
                lista_ras = df_insert['RA']
                lista_ras = lista_ras.to_list()
                registrar(df_insert, 'registro', 'confirmacao_classificacao_coordenacao', lista_ras) 
