# Dados mockados

Estrutura com subpastas:
- `data/source/`: fontes versionadas
  - `kb.json`: FAQ/políticas curtas (pergunta, resposta, tags).
  - `orders.json`: pedidos mock (PED-123 etc.) usados para status/reembolso/cancelamento.
  - `users.json`: usuários mock (perfil, região, tier, canal), úteis para personalização/segmentação.
  - `policies.json`: políticas detalhadas (reembolso, atraso, cancelamento, alergia, segurança).
- `data/ft/`: conjuntos de FT
  - `ft_openai.jsonl`: exemplos de chat para fine-tuning (OpenAI/Gemini).
- `data/cache/`: artefatos gerados (ignorados no git)
  - `kb_index.joblib`: índice TF-IDF gerado por `python -m app.ingest`.
