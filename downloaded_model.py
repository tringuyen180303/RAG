from sentence_transformers import SentenceTransformer

# Pick the model you want
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Save it to a local folder, e.g. "./models"
model.save("models/all-MiniLM-L6-v2")
