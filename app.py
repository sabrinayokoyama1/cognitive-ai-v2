import os
from pathlib import Path
import streamlit as st
from rag_engine import answer

st.set_page_config(page_title="Cognitive AI", page_icon="🐙", layout="centered")
st.markdown("<style>.stApp{background:#090909;color:#f5f5f5}h1{color:#52d9c4}</style>", unsafe_allow_html=True)
st.title("COGNITIVE AI")
st.caption("Think twice. Ask why.")
st.write("Aprenda com perguntas, pistas e reflexão — não apenas respostas prontas.")
try:
    if "OPENAI_API_KEY" in st.secrets:
        os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
except (FileNotFoundError, KeyError):
    pass
uploaded = st.file_uploader("Base de conhecimento (.txt, UTF-8)", type=["txt"])
document = uploaded.getvalue().decode("utf-8") if uploaded else Path(__file__).with_name("knowledge.txt").read_text(encoding="utf-8")
if "messages" not in st.session_state:
    st.session_state.messages = []
if st.button("Nova conversa"):
    st.session_state.messages = []
    st.rerun()
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
if prompt := st.chat_input("O que você quer compreender hoje?"):
    previous = list(st.session_state.messages)
    st.session_state.messages.append({"role":"user", "content":prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        try:
            reply, matches = answer(prompt, document, history=previous)
            st.markdown(reply)
            with st.expander("Trechos consultados"):
                if matches:
                    for i, (passage, score) in enumerate(matches, 1):
                        st.write(f"Trecho {i} (relevância {score:.2f}): {passage}")
                else:
                    st.write("Nenhum trecho relevante encontrado.")
        except Exception as exc:
            st.error(f"Não foi possível consultar o GPT: {exc}")
        else:
            st.session_state.messages.append({"role":"assistant", "content":reply})
