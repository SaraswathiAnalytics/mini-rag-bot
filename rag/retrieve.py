import sqlite3
import sqlite_vec
import json
from sentence_transformers import SentenceTransformer

DB_PATH = "db/rag.db"

model = SentenceTransformer("all-MiniLM-L6-v2")

def retrieve(query: str, k: int = 4) -> str:
    conn = sqlite3.connect(DB_PATH)
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)

    # Encode + serialize embedding
    embedding = model.encode(query).tolist()
    embedding_json = json.dumps(embedding)

    rows = conn.execute("""
        SELECT d.content
        FROM embeddings e
        JOIN documents d ON d.id = e.rowid
        WHERE e.embedding MATCH json(?)
        AND k = ?
        ORDER BY e.distance
    """, (embedding_json, k)).fetchall()

    return "\n\n".join([r[0] for r in rows])
