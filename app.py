"""Interface web do tutor Cognitive AI."""

import base64
import os
from pathlib import Path

import streamlit as st
from openai import APIConnectionError, APIStatusError, AuthenticationError, NotFoundError, PermissionDeniedError, RateLimitError

from document_loader import extract_document
from rag_engine import answer


ROOT = Path(__file__).parent
LOGO = ROOT / "assets" / "logo-cognitive.svg"
STYLES = ROOT / "assets" / "styles.css"
DEFAULT_KNOWLEDGE = ROOT / "knowledge.txt"

st.set_page_config(
    page_title="Cognitive AI",
    page_icon=LOGO,
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(f"<style>{STYLES.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)
logo_uri = "data:image/svg+xml;base64," + base64.b64encode(LOGO.read_bytes()).decode("ascii")

try:
    secret_key = st.secrets.get("OPENAI_API_KEY", "")
except FileNotFoundError:
    secret_key = ""
if secret_key:
    os.environ["OPENAI_API_KEY"] = secret_key
api_ready = bool(os.getenv("OPENAI_API_KEY"))

with st.sidebar:
    st.markdown(
        f'<div class="cognitive-sidebar-brand"><img src="{logo_uri}" alt="Logo Cognitive AI">'
        '<strong>Cognitive <span>AI</span></strong></div>',
        unsafe_allow_html=True,
    )
    st.markdown("### Base de conhecimento")
    uploaded = st.file_uploader("Enviar material para consulta", type=["txt", "pdf"])
    st.caption("Aceita TXT em UTF-8 e PDF com texto selecionável, até 20 MB. Sem arquivo, usa a base padrão.")
    st.caption("Ao perguntar, trechos do material podem ser enviados à OpenAI para gerar a resposta.")
    status_class = "ready" if api_ready else ""
    status_text = "Chave da OpenAI configurada" if api_ready else "Chave da OpenAI pendente"
    st.markdown(
        f'<div class="cognitive-status {status_class}">{status_text}</div>',
        unsafe_allow_html=True,
    )
    if not api_ready:
        st.caption("Configure OPENAI_API_KEY nos Secrets da aplicação publicada.")

upload_error = None
if uploaded:
    try:
        document = extract_document(uploaded.name, uploaded.getvalue())
    except ValueError as exc:
        upload_error = str(exc)
        document = ""
else:
    document = DEFAULT_KNOWLEDGE.read_text(encoding="utf-8")

st.markdown(
    f"""
    <div class="cognitive-hero">
      <img class="cognitive-hero__logo" src="{logo_uri}"
           alt="Logo Cognitive AI, polvo verde-água com olhos roxos">
      <div class="cognitive-hero__body">
        <span class="cognitive-eyebrow">Tutor socrático com RAG</span>
        <h1>Cognitive <span>AI</span></h1>
        <p class="cognitive-slogan">Think twice. <strong>Ask why.</strong></p>
        <p class="cognitive-hero__description">Uma conversa para explorar ideias,
        construir respostas e pensar no próximo passo.</p>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if "messages" not in st.session_state:
    st.session_state.messages = []

section, reset = st.columns([3, 1], vertical_alignment="bottom")
with section:
    st.markdown(
        '<div class="cognitive-section"><h2>Sua conversa</h2>'
        '<p>Pergunte, tente e avance no seu ritmo</p></div>',
        unsafe_allow_html=True,
    )
with reset:
    if st.button("Nova conversa", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

if upload_error:
    st.error(upload_error)


def show_sources(matches):
    """Mantém os trechos consultados junto da resposta após reexecuções."""
    with st.expander("Trechos consultados"):
        if matches:
            for index, (passage, score) in enumerate(matches, 1):
                st.markdown(f"**Trecho {index}** · relevância {score:.2f}")
                st.write(passage)
        else:
            st.write("Nenhum trecho relevante encontrado.")


def api_error_message(exc):
    """Traduz falhas conhecidas sem expor a chave ou detalhes da requisição."""
    if isinstance(exc, AuthenticationError):
        return "A OpenAI recusou a chave. Confira se ela foi copiada por inteiro e está ativa no projeto da API."
    if isinstance(exc, RateLimitError):
        if getattr(exc, "code", None) in {"insufficient_quota", "credit_balance_exhausted", "billing_hard_limit_reached"}:
            return "A conta da API está sem créditos ou atingiu o limite de gastos. Confira o faturamento na OpenAI Platform."
        return "A API atingiu um limite de uso. Aguarde um pouco e tente novamente."
    if isinstance(exc, PermissionDeniedError):
        return "A chave não tem permissão para usar este modelo. Confira o projeto e as permissões na OpenAI Platform."
    if isinstance(exc, NotFoundError):
        return "O modelo configurado não está disponível para este projeto da API."
    if isinstance(exc, APIConnectionError):
        return "Não foi possível conectar à API da OpenAI. Tente novamente em instantes."
    if isinstance(exc, APIStatusError):
        return f"A API da OpenAI respondeu com erro HTTP {exc.status_code}. Confira o projeto da API e tente novamente."
    return "Não foi possível gerar a orientação. Verifique os registros da aplicação no Streamlit."


for message in st.session_state.messages:
    avatar = str(LOGO) if message["role"] == "assistant" else None
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])
        if message["role"] == "assistant":
            show_sources(message.get("matches", []))

suggestion = None
welcome = st.empty()
if not st.session_state.messages:
    with welcome.container():
        st.markdown(
            '<div class="cognitive-welcome">'
            '<div class="cognitive-welcome__icon">✦</div>'
            '<h3>Por onde começamos?</h3>'
            '<p>Traga uma dúvida ou escolha uma pergunta. O tutor oferece pistas e '
            'perguntas para ajudar você a desenvolver seu raciocínio.</p>'
            '</div><p class="cognitive-suggestion-label">Experimente perguntar</p>',
            unsafe_allow_html=True,
        )
        first, second = st.columns(2)
        with first:
            if st.button("O que é aprendizagem ativa?", use_container_width=True, disabled=bool(upload_error)):
                suggestion = "O que é aprendizagem ativa?"
        with second:
            if st.button("Como funcionam as pistas graduais?", use_container_width=True, disabled=bool(upload_error)):
                suggestion = "Como funcionam as pistas graduais?"

typed_prompt = st.chat_input("Escreva sua pergunta ou tentativa...", disabled=bool(upload_error))
prompt = suggestion or typed_prompt

if prompt:
    welcome.empty()
    previous = list(st.session_state.messages)
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant", avatar=str(LOGO)):
        if not api_ready:
            st.warning("Para conversar com o GPT, configure OPENAI_API_KEY nos Secrets da aplicação.")
        else:
            with st.spinner("Preparando uma orientação..."):
                try:
                    reply, matches = answer(prompt, document, history=previous)
                except Exception as exc:
                    st.error(api_error_message(exc))
                else:
                    reply = reply or "Não foi possível formular uma orientação para esta pergunta."
                    st.markdown(reply)
                    show_sources(matches)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": reply, "matches": matches}
                    )
