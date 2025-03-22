import os
import torch
from dotenv import load_dotenv
from typing import List, Dict, Any
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer

load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = "pdf-rag-index"

pc = Pinecone(api_key=PINECONE_API_KEY)

# Initialize embedding model
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model = SentenceTransformer('models/all-MiniLM-L6-v2')
EMBED_DIMENSION = model.get_sentence_embedding_dimension()

class PineconeClient:
    def __init__(self, index_name=INDEX_NAME):
        """Initialize Pinecone index and model."""
        self.index_name = index_name
        
        # Ensure index exists
        if not pc.has_index(name=self.index_name):
            pc.create_index(
                name=self.index_name,
                dimension=EMBED_DIMENSION,
                metric='cosine',
                spec=ServerlessSpec(cloud='aws', region='us-east-1')
            )
        
        # Connect to the index
        self.index = pc.Index(name=self.index_name)
    
    
    def insert_documents(self, documents: List[Dict[str, Any]]):
        """Insert documents into Pinecone."""
        
        vectors = []
        for i, doc in enumerate(documents):
            # Put the text into metadata
            meta = doc.get("metadata", {})
            meta["text"] = doc["text"]  # store chunk text in "metadata"

            vectors.append({
                "id": str(i),
                "values": self.create_embedding(doc["text"]),
                "metadata": meta  # This is the only place for extra data
            })

        self.index.upsert(vectors)
        print(f"Inserted {len(vectors)} documents into Pinecone.")
        
    def create_embedding(self, text: str) -> List[float]:
        """Create an embedding for a text string."""
        return model.encode(text).tolist()
    
    
    def query_documents(self, query: str, top_k=5):
        """
        Query Pinecone for similar documents.

        :param query: User's search query
        :param top_k: Number of relevant documents to retrieve
        :return: List of relevant documents
        """
        query_embedding = self.create_embedding(query)
        results = self.index.query(vector=query_embedding, top_k=top_k, include_metadata=True)

        raw_matches = results.get("matches", [])
        #print(raw_matches)
        sanitized_matches = []

        for match in raw_matches:
            # If needed, remove or rename any big or circular fields 
            sanitized_matches.append({
                "id": match["id"],
                "score": match["score"],
                "metadata": match["metadata"],
                "text": match["metadata"].get("text", "")
                
            })

        return sanitized_matches

        