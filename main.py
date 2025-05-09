import streamlit as st


def check_password():
    def password_entered():
        if (
            st.session_state["username"] in st.secrets["passwords"]
            and st.session_state["password"] == st.secrets["passwords"][st.session_state["username"]]
        ):
            st.session_state["password_correct"] = True
            st.session_state["authenticated_username"] = st.session_state["username"]
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Usuário", key="username")
        st.text_input("Senha", type="password", key="password", on_change=password_entered)
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Usuário", key="username")
        st.text_input("Senha", type="password", key="password", on_change=password_entered)
        st.error("😕 Usuário desconhecido ou senha incorreta.")
        return False
    else:
        return True


def login_page():
    st.title("Login")
    if check_password():
        st.success(f"Bem-vindo, {st.session_state['authenticated_username']}!")
        st.rerun()  # Força a atualização para mostrar as páginas após login

def logout():
    st.session_state["password_correct"] = False
    st.session_state["authenticated_username"] = None
    st.rerun()

logout_page = st.Page(logout, title="Sair")

# --- PAGE SETUP ---
pagina_inicial = st.Page(
    "paginas/app.py",
    title= "Classificação",
    icon= "⚖️",
    default=True,
)

dash = st.Page(
    "paginas/dash.py",
    title= "Visualização",
    icon= "📊"
)

st.set_page_config(layout="wide")

# --- NAVIGATION SETUP [WITH SECTIONS]---
if st.session_state.get("password_correct"):
    pg = st.navigation({
        "Paginas": [pagina_inicial, dash],
    })    
else:
    pg = st.navigation([st.Page(login_page, title="Login")])
# --- RUN NAVIGATION ---
pg.run()
