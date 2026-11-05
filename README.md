# Cognitive AI V2

*Think twice. Ask why.*

Assistente educacional socrático com **GPT + RAG**, dividido em duas partes.

1. `cognitive_rag.ipynb` contém o código de recuperação de trechos e geração de respostas. A célula de exportação atualiza o `rag_engine.py`, usado pela interface.
2. `app.py` é a aplicação web em Streamlit, com chat e upload de arquivos `.txt`.

Arquivos de apoio incluem `rag_engine.py`, `knowledge.txt`, `requirements.txt` e `.gitignore`.

## Executar localmente

Configure a variável de ambiente `OPENAI_API_KEY` e mantenha a chave fora do Git. Depois, execute os comandos abaixo.

```bash
pip install -r requirements.txt
streamlit run app.py
