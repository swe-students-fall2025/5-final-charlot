import os
import io
import docx
import uvicorn

from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from PyPDF2 import PdfReader

from agents import build_graph, run_query
from utils import (
    get_embedder,
    load_vectorstore,
    save_vectorstore,
    build_vectorstore,
    chunk_text
)

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
            "Please upload a document first or wait for index to build."
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

    # Auto-build index on first deployment if it doesn't exist
    if not INDEX_PATH.exists():
        print("Vector index not found. Building index from CUAD dataset...")
        try:
            from utils import load_documents, save_vectorstore

            # Build with a reasonable number of contracts
            print("Loading documents...")
            texts, metadatas = load_documents(str(SERVICE_ROOT / "data"), max_contracts=50)

            print("Creating embeddings...")
            embedder = get_embedder()
            vector_db_temp = build_vectorstore(texts, metadatas, embedder)

            print(f"Saving index to {INDEX_PATH}...")
            save_vectorstore(vector_db_temp, str(INDEX_PATH))
            print("Index built successfully!")
        except Exception as e:
            print(f"Warning: Could not auto-build index: {e}")
            print("Service will work with user-uploaded documents only.")

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


@app.post("/index-document")
async def index_document(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    session_id: str = Form(None)
):
    """
    Upload and index a document for a specific user.

    Supported file types: .pdf, .txt, .md, .doc, .docx
    """
    try:
        # Read file
        file_bytes = await file.read()
        filename = file.filename.lower()

        # Extract text based on file type
        if filename.endswith('.pdf'):
            # PDF extraction
            pdf_file = io.BytesIO(file_bytes)
            reader = PdfReader(pdf_file)

            text_parts = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)

            if not text_parts:
                raise HTTPException(status_code=400, detail="No text could be extracted from PDF")

            full_text = "\n\n".join(text_parts)

        elif filename.endswith('.txt') or filename.endswith('.md'):
            # Plain text or Markdown
            try:
                full_text = file_bytes.decode('utf-8')
            except UnicodeDecodeError:
                # Try with different encoding
                full_text = file_bytes.decode('latin-1')

        elif filename.endswith('.doc') or filename.endswith('.docx'):
            # Word documents (requires python-docx)
            try:
                doc_file = io.BytesIO(file_bytes)
                doc = docx.Document(doc_file)
                full_text = "\n\n".join([para.text for para in doc.paragraphs if para.text.strip()])
            except ImportError:
                raise HTTPException(
                    status_code=400,
                    detail="Word document support not available. Please convert to PDF or TXT."
                )

        else:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file type. Supported: .pdf, .txt, .md, .doc, .docx"
            )

        if not full_text or not full_text.strip():
            raise HTTPException(status_code=400, detail="No text could be extracted from file")

        # Chunk the text
        chunks = chunk_text(full_text, chunk_size=1500, overlap=200)

        # Create metadata for each chunk
        metadatas = [
            {
                "source": file.filename,
                "user_id": user_id,
                "session_id": session_id or "",
                "chunk_index": i,
                "total_chunks": len(chunks),
                "type": "user_upload"
            }
            for i in range(len(chunks))
        ]

        # Get embedder
        embedder = get_embedder()

        # User-specific vector store path
        user_index_dir = SERVICE_ROOT / "data" / "embeddings" / "users"
        user_index_dir.mkdir(parents=True, exist_ok=True)
        user_index_path = user_index_dir / f"user_{user_id}_faiss"

        # Load or create vector store
        if user_index_path.exists():
            # Add to existing user index
            vector_db = load_vectorstore(str(user_index_path), embedder)
            vector_db.add_texts(texts=chunks, metadatas=metadatas)
        else:
            # Create new index - start with CUAD if available
            if INDEX_PATH.exists():
                # Copy CUAD index and add user documents
                vector_db = load_vectorstore(str(INDEX_PATH), embedder)
                vector_db.add_texts(texts=chunks, metadatas=metadatas)
            else:
                # Create completely new index
                vector_db = build_vectorstore(
                    texts=chunks,
                    metadatas=metadatas,
                    embedder=embedder
                )

        # Save updated index
        save_vectorstore(vector_db, str(user_index_path))

        return {
            "status": "success",
            "filename": file.filename,
            "user_id": user_id,
            "chunks_created": len(chunks),
            "index_path": str(user_index_path)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
