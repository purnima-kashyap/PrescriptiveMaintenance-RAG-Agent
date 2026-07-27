# backend folder mein quick_check.py banao
from app.vectorstore.vector_store import collection
print(f"Total chunks in collection: {collection.count()}")

# Check for duplicate documents
all_data = collection.get()
texts = all_data['documents']
print(f"Total documents: {len(texts)}")
print(f"Unique documents: {len(set(texts))}")

if len(texts) != len(set(texts)):
    print("⚠️ DUPLICATES FOUND!")
else:
    print("✅ No duplicates in collection.")