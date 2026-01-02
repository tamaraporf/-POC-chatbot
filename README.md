# Chatbot de Suporte para Entregas (passo a passo)

Vamos construir, do zero, um chatbot para suporte de entregas de alimentos. Cada etapa terá arquivos simples e comentados.

## Como rodar
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# Geração por OpenAI (recomendado p/ POC)
echo "OPENAI_API_KEY=<sua-chave>" >> .env
echo "OPENAI_MODEL=gpt-4o-mini" >> .env   # opcional, default já é gpt-4o-mini

# Alternativa: Gemini
echo "GEMINI_API_KEY=<sua-chave>" >> .env
echo "GEMINI_MODEL=gemini-1.5-flash" >> .env   # opcional, default já é gemini-1.5-flash

# Ou uso de modelo Hugging Face (precisa torch instalado)
# export HF_MODEL=google/flan-t5-small

uvicorn app.main:app --reload
```

## Base conceitual (antes do código)

### RAG (Retrieval-Augmented Generation)
- O que é: o modelo busca trechos em uma base (FAQ - Frequently Asked Questions, políticas, status) e gera resposta citando esses trechos.
- Por que usar aqui: suporte precisa estar sempre atualizado (políticas, promos, SLAs) sem re-treinar modelo.
- Dados necessários: corpus de FAQ/políticas (mock) em JSON/Markdown; índices de vetor ou TF-IDF simples.
- Como validar: checar se a resposta usa evidências corretas (groundedness) e se recupera o documento certo.

### Fine-tuning
- O que é: ajustar um modelo com exemplos de perguntas/respostas específicas.
- Quando usar: para reduzir alucinação de estilo ou seguir formatos fixos (ex.: campos JSON), NÃO para atualizar conhecimento factual diário.
- Dados necessários: pares pergunta→resposta aprovados; de preferência 500+ exemplos diversos. Neste projeto, manteremos só o mock e indicaremos onde encaixar FT depois.

### Combinação
- Fluxo principal usa RAG para trazer fatos atualizados (ex.: “qual SLA de atraso?”).
- Fine-tuning opcional para tom de voz/estilo de saída, mantendo RAG para fatos.

## Planejamento de dados (mock)
- FAQ/Políticas: arquivo JSON com pergunta, resposta, tags.
- Pedidos: arquivo JSON com pedidos fictícios e status.
- Políticas detalhadas: `data/policies.json` (reembolso, atraso, cancelamento, alergia, segurança).
- Usuários mock: `data/users.json` (100 usuários com região, tier, canal, flags).
- Avaliação: 20–50 casos de teste sintéticos (perguntas típicas) para checar se o RAG recupera e responde corretamente.

## Próximos passos (ordem sugerida)
1) Esqueleto do app (FastAPI) com `/healthz`.
2) Estrutura de dados mock: criar `data/kb.json` (FAQ) e `data/orders.json` (pedidos).
3) Retriever simples (TF-IDF) para o KB.
4) Agente RAG: recebe pergunta, chama retriever, monta resposta com evidências.
5) Agente de ferramentas (pedidos): consulta pedido mock por ID e dá status.
6) Orquestrador: decide entre RAG ou ferramenta.
7) Camada de política/tom (opcional) para segurança e estilo.

Podemos seguir criando cada arquivo nessa ordem, explicando o que faz. Diga se quer começar pelo esqueleto do app (passo 1) ou pelos dados mock (passo 2).
