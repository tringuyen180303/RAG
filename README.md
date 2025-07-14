# PDF RAG System

A system that allows users to upload PDF files, store them in Google Cloud Storage, and use RAG (Retrieval-Augmented Generation) to analyze and retrieve information from them.

## Features

- PDF file upload and storage in Google Cloud Storage
- PDF text extraction and chunking
- Vector database storage using Milvus
- RAG-based querying of PDF content
- RESTful API endpoints

## Prerequisites

- Python 3.8+
- Docker and Docker Compose
- Google Cloud Platform account with:
  - Cloud Storage bucket
  - Service account with appropriate permissions
- Milvus vector database

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Start Milvus and its dependencies:
```bash
docker-compose up -d
```

6. Set up Google Cloud credentials:
- Create a service account in GCP
- Download the service account key JSON file
- Set the path in GOOGLE_APPLICATION_CREDENTIALS in .env

7. Start the application:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

### Upload PDF
```http
POST /upload-pdf
Content-Type: multipart/form-data

file: <pdf_file>
```

### Query PDF Content
```http
POST /query
Content-Type: application/json

{
    "query": "your question here",
    "limit": 5
}
```

### Health Check
```http
GET /health
```

## Usage Example

1. Upload a PDF file:
```bash
curl -X POST -F "file=@/path/to/your/document.pdf" http://localhost:8000/upload-pdf
```

2. Query the PDF content:
```bash
curl -X POST -H "Content-Type: application/json" \
     -d '{"query": "What are the main topics discussed?", "limit": 5}' \
     http://localhost:8000/query
```

## Architecture

The system consists of several components:

1. **PDF Processor**: Extracts text from PDFs and splits it into chunks
2. **GCP Storage**: Stores the original PDF files
3. **Vector Database**: Stores document embeddings for similarity search
4. **FastAPI Application**: Handles HTTP requests and orchestrates the components

## Configuration

Key configuration options in `.env`:

- `GCP_BUCKET_NAME`: Your GCP storage bucket name
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to your GCP service account key
- `CHUNK_SIZE`: Size of text chunks for processing
- `CHUNK_OVERLAP`: Overlap between chunks

## Development

To run tests:
```bash
pytest
```

## License

MIT License
