# Cognitive AI V2 — Think twice. Ask why.

Assistente educacional socrático com **GPT + RAG**, apresentado em duas partes:

1. `cognitive_rag.ipynb` — notebook do motor de recuperação e geração. Ao executar a célula de exportação, atualiza `rag_engine.py` (módulo de apoio para a interface).
2. `app.py` — aplicação web Streamlit, com chat e upload de `.txt`.

Arquivos de apoio: `rag_engine.py`, `knowledge.txt`, `requirements.txt` e `.gitignore`.

## Executar localmente

```bash
pip install -r requirements.txt
# Configure OPENAI_API_KEY no ambiente (não inclua a chave no Git)
streamlit run app.py
```

## Deploy gratuito da interface

1. Publique estes arquivos em um repositório GitHub.
2. Entre em https://share.streamlit.io/ e escolha **Create app** > **Deploy a public app from GitHub**.
3. Selecione o repositório, branch `main` e arquivo principal `app.py`.
4. Em **Advanced settings / Secrets**, informe:

```toml
OPENAI_API_KEY = "sua-chave-da-api"
```

5. Clique em **Deploy**. O Streamlit Community Cloud oferece hospedagem gratuita sujeita a limites e políticas do serviço. **A API GPT é cobrada separadamente** conforme uso.

## Arquitetura

Estudante → Streamlit → `rag_engine.py` (exportado do notebook) → TF-IDF recupera trechos do documento → GPT responde com orientação socrática.

**Limitações:** RAG lexical simples com TF-IDF, sem banco vetorial; documentos `.txt` pequenos; base de conhecimento enviada ao GPT no contexto; sem autenticação, rate limiting ou proteção de custos. Para um protótipo acadêmico, mantenha limites de uso e monitore gastos da API.
