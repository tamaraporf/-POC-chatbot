"""FastAPI com healthcheck e rota de chat usando RAG simples ou modelo HF.

Fluxo:
- Carrega um retriever baseado em TF-IDF lendo o KB mock (`data/kb.json`).
- Endpoint `/chat` recebe uma mensagem, busca a entrada mais relevante e devolve a resposta do KB.
- Se houver `HF_MODEL`, gera resposta com modelo Hugging Face usando a evidência do KB.
- Se nada for encontrado, pede mais detalhes ao usuário.
"""

import os
import logging
from pathlib import Path
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from dotenv import load_dotenv

from .auth import verify_api_key
from .retriever import KnowledgeBaseRetriever
from .vector_retriever import VectorRetriever
from .orders import get_order
from .policies import get_policy
from .users import get_user
from .llm_hf import get_hf_pipeline
from .openai_client import get_openai_client, generate_with_context
from .gemini_client import get_gemini_model, generate_with_context as gemini_generate
from .router import detect_intent

logger = logging.getLogger("uvicorn.error")

# Carrega variáveis do .env (OPENAI_API_KEY, OPENAI_MODEL, HF_MODEL etc.)
load_dotenv()


def _load_hf_pipeline():
    """Tenta carregar o pipeline HF; retorna None se faltar backend ou falhar."""
    try:
        import torch  # noqa: F401
    except Exception:
        logger.warning(
            "HF_MODEL definido, mas backend (torch) não está instalado. "
            "Instale torch ou remova HF_MODEL para evitar erro."
        )
        return None
    try:
        return get_hf_pipeline()
    except Exception as exc:  # pragma: no cover
        logger.warning("Falha ao carregar pipeline HF: %s", exc)
        return None


app = FastAPI(title="Chatbot Suporte Entregas", version="0.1.0")
data_dir = Path(__file__).resolve().parent.parent / "data"
kb_path = data_dir / "kb.json"
retriever = KnowledgeBaseRetriever(kb_path)
index_path = data_dir / "kb_index.joblib"
vector_retriever = VectorRetriever(index_path, top_k=3) if index_path.exists() else None
USE_HF = os.getenv("HF_MODEL") is not None
hf_pipe = _load_hf_pipeline() if USE_HF else None
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
openai_client = get_openai_client()
gemini_model = get_gemini_model()
logger.info("HF_MODEL ativo? %s | pipeline carregado? %s", USE_HF, hf_pipe is not None)
logger.info("OPENAI ativo? %s | modelo=%s", openai_client is not None, OPENAI_MODEL)
logger.info("GEMINI ativo? %s", gemini_model is not None)


@app.on_event("startup")
async def log_model_status() -> None:
    """Loga status do modelo HF na inicialização."""
    logger.info(
        "Startup: HF_MODEL=%s | pipeline carregado=%s", USE_HF, hf_pipe is not None
    )
    logger.info(
        "Startup: OPENAI ativo=%s modelo=%s", openai_client is not None, OPENAI_MODEL
    )
    logger.info("Startup: GEMINI ativo=%s", gemini_model is not None)
    print(f"Startup: HF_MODEL={USE_HF} | pipeline carregado={hf_pipe is not None}")
    print(f"Startup: OPENAI ativo={openai_client is not None} modelo={OPENAI_MODEL}")
    print(f"Startup: GEMINI ativo={gemini_model is not None}")


class ChatRequest(BaseModel):
    """Payload de entrada para o chat."""

    mensagem: str


class ChatResponse(BaseModel):
    """Payload de saída com resposta e fonte (pergunta do KB)."""

    resposta: str
    fonte: str | None = None
    via_modelo: bool = False
    aviso_modelo: str | None = None


class OrderResponse(BaseModel):
    """Resposta para consulta de pedido."""

    order_id: str
    status: str
    eta_minutos: int
    itens: list
    total: float


@app.get("/healthz")
def healthcheck() -> dict:
    """Endpoint de liveness simples."""
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse, dependencies=[Depends(verify_api_key)])
def chat(req: ChatRequest) -> ChatResponse:
    """Busca no KB e responde; se houver modelo, gera texto usando evidência."""
    intent = detect_intent(req.mensagem)
    # preferir índice vetorial, se existir
    if vector_retriever:
        resultados = vector_retriever.retrieve(req.mensagem)
    else:
        resultados = retriever.retrieve(req.mensagem)

    # Respostas específicas por intenção simples
    if intent == "pedido":
        # Tentar extrair PED- na mensagem
        # Reuso do endpoint /pedido não está integrado; aqui perguntamos pelo id.
        return ChatResponse(
            resposta="Para consultar ou agir em um pedido, compartilhe o código (PED-123).",
            fonte=None,
            via_modelo=False,
            aviso_modelo="Intent pedido detectada; aguardando ID.",
        )
    if intent == "politica":
        pol = get_policy("reembolso") or {}
        resposta_pol = pol.get(
            "passos",
            "Consigo ajudar com políticas de reembolso, atraso, cancelamento e alergia.",
        )
        return ChatResponse(
            resposta=f"Política exemplo (reembolso): {resposta_pol}",
            fonte="policies.json",
            via_modelo=False,
            aviso_modelo="Intent política detectada; usando política mock.",
        )
    if intent == "usuario":
        return ChatResponse(
            resposta="Para consultar um usuário, informe o código (ex.: USR-001).",
            fonte=None,
            via_modelo=False,
            aviso_modelo="Intent usuario detectada; aguardando ID.",
        )
    if not resultados:
        return ChatResponse(
            resposta="Não encontrei nada no KB. Pode reformular ou dar mais detalhes?",
            fonte=None,
            via_modelo=False,
            aviso_modelo=None,
        )
    top = resultados[0]
    # Preferir OpenAI se disponível
    if openai_client:
        try:
            generated = generate_with_context(
                openai_client,
                OPENAI_MODEL,
                req.mensagem,
                top["resposta"],
            )
            return ChatResponse(
                resposta=generated,
                fonte=top["pergunta"],
                via_modelo=True,
                aviso_modelo=None,
            )
        except Exception as exc:  # pragma: no cover
            logger.warning("Falha OpenAI, caindo para HF/KB: %s", exc)
    # Se Gemini estiver disponível, usar como fallback antes do HF
    if gemini_model:
        try:
            generated = gemini_generate(
                gemini_model,
                req.mensagem,
                top["resposta"],
            )
            return ChatResponse(
                resposta=generated,
                fonte=top["pergunta"],
                via_modelo=True,
                aviso_modelo=None,
            )
        except Exception as exc:  # pragma: no cover
            logger.warning("Falha Gemini, caindo para HF/KB: %s", exc)
    # Se tiver modelo HF configurado, gera resposta usando contexto do KB.
    if hf_pipe:
        contexto = (
            "Instrução: responda em português em 1 frase. Use apenas a evidência. "
            "Se a evidência já responde, repita-a exatamente (sem mudar acentuação). "
            "Se faltar informação, peça dados adicionais.\n\n"
            f"Evidência: {top['resposta']}\n"
            f"Pergunta: {req.mensagem}\n"
            "Resposta:"
        )
        generated = hf_pipe(
            contexto,
            max_new_tokens=130,
            num_return_sequences=1,
            do_sample=False,
        )[0]["generated_text"]
        return ChatResponse(
            resposta=generated.strip(),
            fonte=top["pergunta"],
            via_modelo=True,
            aviso_modelo=None,
        )
    # Caso contrário, devolve resposta direta do KB.
    aviso = None
    if openai_client is None and gemini_model is None and not USE_HF:
        aviso = "Nenhum modelo configurado; usando resposta direta do KB."
    elif openai_client is None and gemini_model is None and USE_HF and not hf_pipe:
        aviso = "HF_MODEL definido, mas pipeline não carregou."
    return ChatResponse(
        resposta=top["resposta"],
        fonte=top["pergunta"],
        via_modelo=False,
        aviso_modelo=aviso,
    )


@app.get(
    "/pedido/{order_id}",
    response_model=OrderResponse,
    dependencies=[Depends(verify_api_key)],
)
def pedido(order_id: str) -> OrderResponse:
    """Consulta um pedido mock pelo ID (formato PED-123)."""
    order = get_order(order_id)
    if not order:
        # FastAPI transformará ValueError em 422; mantemos simples.
        raise ValueError("Pedido não encontrado.")
    return OrderResponse(
        order_id=order["order_id"],
        status=order["status"],
        eta_minutos=order["eta_minutos"],
        itens=order["itens"],
        total=order["total"],
    )
