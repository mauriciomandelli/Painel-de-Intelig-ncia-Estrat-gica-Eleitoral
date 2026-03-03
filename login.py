import yaml
import streamlit as st
import hashlib


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def _carregar_usuarios() -> dict:
    try:
        with open("users.yaml", "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        st.error("Arquivo users.yaml não encontrado.")
        return {}


def login() -> tuple[bool, str, str]:
    """
    Exibe o formulário de login e retorna (autenticado, nome, role).
    role pode ser 'premium' ou 'free'.
    """
    config = _carregar_usuarios()
    usuarios = config.get("credentials", {}).get("usernames", {})

    # Inicializar estado de sessão
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False
        st.session_state.nome_usuario = ""
        st.session_state.role = "free"
        st.session_state.login_usuario = ""

    if st.session_state.autenticado:
        return True, st.session_state.nome_usuario, st.session_state.role

    # Layout do login
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
            <div style='text-align:center; padding: 30px 0 10px 0;'>
                <h1 style='font-size:2rem;'>📊 Radar Eleitoral SC</h1>
                <p style='color: gray;'>Inteligência Eleitoral para Santa Catarina</p>
            </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            usuario = st.text_input("👤 Usuário")
            senha   = st.text_input("🔑 Senha", type="password")
            entrar  = st.form_submit_button("Entrar", use_container_width=True)

        if entrar:
            if usuario in usuarios:
                senha_config = usuarios[usuario]["password"]
                # Aceita tanto senha em texto puro quanto hash SHA-256
                senha_ok = (senha == senha_config) or (_hash(senha) == senha_config)
                if senha_ok:
                    st.session_state.autenticado   = True
                    st.session_state.nome_usuario  = usuarios[usuario]["name"]
                    st.session_state.role          = usuarios[usuario].get("role", "free")
                    st.session_state.login_usuario = usuario
                    st.rerun()
                else:
                    st.error("Senha incorreta.")
            else:
                st.error("Usuário não encontrado.")

    return False, "", "free"


def logout():
    """Botão de logout na sidebar."""
    st.sidebar.divider()
    nome = st.session_state.get("nome_usuario", "")
    role = st.session_state.get("role", "free")
    icone = "⭐" if role == "premium" else "👤"
    st.sidebar.markdown(f"**{icone} {nome}**")
    if role == "premium":
        st.sidebar.caption("Acesso Premium")
    else:
        st.sidebar.caption("Acesso Free")
    if st.sidebar.button("🚪 Sair"):
        for key in ["autenticado", "nome_usuario", "role", "login_usuario"]:
            st.session_state.pop(key, None)
        st.rerun()


def is_premium() -> bool:
    return st.session_state.get("role") == "premium"


def gate_premium():
    """Bloqueia o conteúdo se o usuário não for premium."""
    if not is_premium():
        st.warning("⭐ Esta funcionalidade é exclusiva para usuários **Premium**.")
        st.info("Entre em contato com o administrador para obter acesso.")
        st.stop()
