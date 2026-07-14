import chromadb

# Create or connect to a local Chroma database
client = chromadb.PersistentClient(path="./chroma_db")

# Create a collection (or load it if it already exists)
collection = client.get_or_create_collection(
    name="maintenance_manuals"
)

print("✅ ChromaDB initialized successfully!")