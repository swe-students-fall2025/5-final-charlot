import os
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from agents import build_graph, run_query
from utils import get_embedder, load_vectorstore

# os.environ["TOKENIZERS_PARALLELISM"] = "false"
load_dotenv()

SERVICE_ROOT = Path(__file__).parent.parent
VECTOR_DB_PATH = os.getenv(
    "VECTOR_DB_PATH",
    str(SERVICE_ROOT.parent / "data" / "embeddings" / "faiss_index")
)
INDEX_PATH = Path(VECTOR_DB_PATH)

ml_agent = None
vector_db = None


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    query: str
    retrieved_documents: list[str]
    reasoning_chain: list[str]
    verification_status: str
    final_explanation: str


def _lazy_load_agent():
    """Load agent only when first needed."""
    global ml_agent, vector_db

    if ml_agent is not None:
        return ml_agent

    if not INDEX_PATH.exists():
        raise RuntimeError(
            f"Vector index not found at {INDEX_PATH}. "
            "Set VECTOR_DB_PATH environment variable or run build script."
        )

    print(f"Loading ML agent from {INDEX_PATH}...")
    embedder = get_embedder()
    vector_db = load_vectorstore(str(INDEX_PATH), embedder)
    ml_agent = build_graph(vector_db=vector_db)
    print("ML agent loaded!")

    return ml_agent


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("ML Agent Service starting...")
    print(f"Vector DB path: {INDEX_PATH}")
    yield
    print("Shutting down ML Agent Service...")


app = FastAPI(
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "status": "running",
        "agent_ready": ml_agent is not None,
        "vector_db_path": str(INDEX_PATH)
    }


@app.get("/health")
def health():
    return {
        "status": "healthy" if ml_agent else "degraded",
        "vector_db_loaded": vector_db is not None,
        "index_exists": INDEX_PATH.exists(),
        "index_path": str(INDEX_PATH)
    }


@app.post("/query", response_model=QueryResponse)
def query_agent(request: QueryRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    try:
        agent = _lazy_load_agent()

        result = run_query(agent, request.query.strip())
        return QueryResponse(
            query=result["user_query"],
            retrieved_documents=result["retrieved_documents"],
            reasoning_chain=result["reasoning_chain"],
            verification_status=result["verification_status"],
            final_explanation=result["final_explanation"]
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
