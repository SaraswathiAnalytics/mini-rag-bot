import os
import sqlite3
import sqlite_vec
import json
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter

DB_PATH = "db/rag.db"
DOCS_PATH = "data/docs"

os.makedirs("db", exist_ok=True)

model = SentenceTransformer("all-MiniLM-L6-v2")

conn = sqlite3.connect(DB_PATH)
conn.enable_load_extension(True)
sqlite_vec.load(conn)

conn.execute("""
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY,
    content TEXT
)
""")

conn.execute("""
CREATE VIRTUAL TABLE IF NOT EXISTS embeddings
USING vec0(embedding FLOAT[384]);
""")

splitter = RecursiveCharacterTextSplitter(
    chunk_size=400,
    chunk_overlap=50
)

def ingest():
    for file in os.listdir(DOCS_PATH):
        path = os.path.join(DOCS_PATH, file)
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        chunks = splitter.split_text(text)

        for chunk in chunks:
            embedding = model.encode(chunk).tolist()

            cur = conn.cursor()
            cur.execute(
                "INSERT INTO documents (content) VALUES (?)",
                (chunk,)
            )
            doc_id = cur.lastrowid

            # serialize embedding
            conn.execute(
                "INSERT INTO embeddings(rowid, embedding) VALUES (?, json(?))",
                (doc_id, json.dumps(embedding))
            )

    conn.commit()
    print("Documents ingested successfully")

if __name__ == "__main__":
    ingest()
