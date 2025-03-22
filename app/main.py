# from fastapi import FastAPI, UploadFile, File, HTTPException, Form
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# import tempfile
# import os
# from dotenv import load_dotenv
# from pdf_processor import PDFProcessor
# from gcp_storage import GCPStorageHandler
# from vector_database import PineconeClient
# import openai
# from openai import OpenAI

# load_dotenv()
# app = FastAPI(title="PDF RAG with Pinecone")
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# pdf_processor = PDFProcessor()
# #gcp_storage = GCPStorageHandler(bucket_name="rag-practice-storage")

# class QueryRequest(BaseModel):
#     query: str
#     top_k: int = 5

# @app.get("/health")
# def health():
#     return {"status": "Service is running smoothly!"}

# @app.post("/upload")
# async def upload_pdf(file: UploadFile = File(...)):
#     """
#     Basic endpoint to upload a PDF and index it,
#     without asking any query. 
#     """
#     if not file.filename.endswith('.pdf'):
#         raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

#     try:
#         # 1) Save PDF to a temp file
#         with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
#             temp_pdf.write(await file.read())
#             temp_pdf_path = temp_pdf.name

#         # 2) Upload to GCP
#         #pdf_url = gcp_storage.upload_file(temp_pdf_path)

#         # 3) Process PDF
#         chunks = pdf_processor.process_pdf(temp_pdf_path)

#         # 4) Index chunks into Pinecone
#         vector_database = PineconeClient("pdf-rag-index")
#         vector_database.insert_documents(chunks)

#         # 5) Cleanup
#         os.unlink(temp_pdf_path)

#         return {
#             "message": "PDF successfully uploaded and indexed.",
#             #"pdf_url": pdf_url,
#             "chunks_processed": len(chunks)
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))




# def generate_answer(query, retrieved_docs):
#     """Generate response using OpenAI's GPT with retrieved context."""
#     context = "\n".join([doc["metadata"]["text"] for doc in retrieved_docs])
    
#     prompt = f"""
#     You are an AI assistant. Use the following context to answer the query.
    
#     Context:
#     {context}
    
#     Query:
#     {query}
    
#     Answer:
#     """
#     client = OpenAI(api_key=OPENAI_API_KEY)
#     response = client.chat.completions.create(
#     model="gpt-4o",
#     messages=[{"role": "system", "content": prompt}],
#     temperature=0.5,
# )
    
#     return response.choices[0].message.content

# @app.post("/upload_and_query")
# async def upload_and_query(
#     file: UploadFile = File(...),
#     question: str = Form(...),
#     top_k: int = Form(5)
# ):
#     """
#     Endpoint that both uploads/indexes the PDF and 
#     queries Pinecone in a single request.
#     """
#     if not file.filename.endswith('.pdf'):
#         raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

#     try:
#         # 1) Save PDF to a temp file
#         with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
#             temp_pdf.write(await file.read())
#             temp_pdf_path = temp_pdf.name

#         # 2) Upload to GCP
#         #pdf_url = gcp_storage.upload_file(temp_pdf_path)

#         # 3) Process the PDF (create text chunks)
#         chunks = pdf_processor.process_pdf(temp_pdf_path)

#         # 4) Index chunks into Pinecone
#         vector_database = PineconeClient("pdf-rag-index")
#         vector_database.insert_documents(chunks)

#         # 5) Run the query against the newly indexed PDF
#         results = vector_database.query_documents(query=question, top_k=top_k)

#         answer = generate_answer(question, results)

#         # 6) Cleanup temp PDF
#         os.unlink(temp_pdf_path)

#         return {
#             # "message": "PDF successfully uploaded, indexed, and queried.",
#             # "pdf_url": pdf_url,
#             # "chunks_processed": len(chunks),
#             # "query": question,
#             # "top_k": top_k,
#             # "results": results,
#             "answer": answer
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import tempfile
import os
from dotenv import load_dotenv

# OpenTelemetry imports:
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry import trace

# Your existing imports:
from pdf_processor import PDFProcessor
from vector_database import PineconeClient
import openai
from openai import OpenAI

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = FastAPI(title="PDF RAG with Pinecone")

# 1) Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2) Setup your existing classes
class QueryRequest(BaseModel):
    query: str
    top_k: int = 5

# 3) Integrate OpenTelemetry
resource = Resource(attributes={SERVICE_NAME: "fastapi-rag-service"})
tracer_provider = TracerProvider(resource=resource)
otlp_exporter = OTLPSpanExporter(
    endpoint="http://jaeger:4317"
)
processor = BatchSpanProcessor(otlp_exporter)
tracer_provider.add_span_processor(processor)
trace.set_tracer_provider(tracer_provider)

# Automatically trace incoming requests to FastAPI
FastAPIInstrumentor.instrument_app(app, tracer_provider=tracer_provider)

pdf_processor = PDFProcessor()
# gcp_storage = GCPStorageHandler(bucket_name="rag-practice-storage")  # If you want GCP again

@app.get("/health")
def health():
    return {"status": "Service is running smoothly!"}

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    # same logic as before
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf.write(await file.read())
            temp_pdf_path = temp_pdf.name

        # process
        chunks = pdf_processor.process_pdf(temp_pdf_path)
        vector_database = PineconeClient("pdf-rag-index")
        vector_database.insert_documents(chunks)
        os.unlink(temp_pdf_path)

        return {"message": "PDF successfully uploaded and indexed.", 
                "chunks_processed": len(chunks)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def generate_answer(query, retrieved_docs):
    context = "\n".join([doc["metadata"]["text"] for doc in retrieved_docs])
    prompt = f"""
    You are an AI assistant. Use the following context to answer the query.
    
    Context:
    {context}
    
    Query:
    {query}
    
    Answer:
    """
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": prompt}],
        temperature=0.5,
    )
    return response.choices[0].message.content

@app.post("/upload_and_query")
async def upload_and_query(file: UploadFile = File(...),
                           question: str = Form(...),
                           top_k: int = Form(5)):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf.write(await file.read())
            temp_pdf_path = temp_pdf.name

        # process
        chunks = pdf_processor.process_pdf(temp_pdf_path)
        vector_database = PineconeClient("pdf-rag-index")
        vector_database.insert_documents(chunks)
        results = vector_database.query_documents(query=question, top_k=top_k)
        answer = generate_answer(question, results)

        os.unlink(temp_pdf_path)

        return {"answer": answer}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
