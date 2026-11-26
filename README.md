# Cognitive AI

Tutor socrático com busca de trechos por TF-IDF e respostas geradas por GPT.

## Aplicação web

Execute em um ambiente remoto com:

```bash
pip install -r requirements.txt
streamlit run app.py
```

A interface usa `assets/logo-cognitive.svg`, uma reprodução vetorial provisória baseada na identidade visual compartilhada, e `assets/styles.css` para o tema responsivo.

## Publicação

No Streamlit Community Cloud, selecione o repositório `sabrinayokoyama1/cognitive-ai-v2`, a branch `main` e o arquivo `app.py`. Para ativar as respostas por GPT, configure `OPENAI_API_KEY` nos Secrets da aplicação. Nunca adicione a chave ao repositório. A API da OpenAI pode gerar custos de uso.

O arquivo `cognitive_rag.ipynb` preserva o desenvolvimento em notebook. A base padrão está em `knowledge.txt`; a interface também aceita um arquivo `.txt` enviado pelo usuário.
