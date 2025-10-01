import os, glob, re, json
import numpy as np
import faiss
import litellm
import json
from config import MODEL
#from sentence_transformers import SentenceTransformer

EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 200
TOP_K = 4 # best result
SIM_THRESHOLD = 0.25

def read_corpus(pattern="data/*"):
   docs = []
   for path in glob.glob(pattern):
       with open(path, "r", encoding="utf-8", errors="ignore") as f:
           text = f.read().strip()
           docs.append({"path": path, "text": text})
   return docs

def chunk_text(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
   sents = re.split(r"(?<=[.!?])\s+", text)
   chunks, buf = [], ""
   for s in sents:
       if len(buf) + len(s) + 1 <= size:
           buf = (buf + " " + s).strip()
       else:
           if buf:
               chunks.append(buf)
           start = max(0, len(buf) - overlap)
           carry = buf[start:]
           buf = (carry + " " + s).strip()
   if buf:
       chunks.append(buf)

   return chunks

def embed_texts(texts, model=EMBED_MODEL):
    embs = []
    for t in texts:
        response = litellm.embedding(model=model, input=t)
        emb = response['data'][0]['embedding']  # depends on the exact format of litellm output
        embs.append(np.array(emb, dtype="float32"))
    return np.vstack(embs)


#def embed_texts(texts, model=EMBED_MODEL):
#   embs = []
#   for t in texts:
#       #r = litellm.embedding(model=model, input=t)
#       embeding_model = SentenceTransformer(EMBED_MODEL)
#       emb = embeding_model.encode(t, normalize_embeddings=True)
#       embs.append(np.array(emb, dtype="float32")) # vectors
#   return np.vstack(embs)


def build_index(chunks):
   embs = embed_texts([c["text"] for c in chunks])
   faiss.normalize_L2(embs)
   index = faiss.IndexFlatIP(embs.shape[1])
   index.add(embs)
   return index


class RAG:
   def __init__(self):
       self.docs = None
       self.chunks = None
       self.index = None

   #def ingest(self, pattern="data/*"):
   #    self.docs = read_corpus(pattern)
   #    self.chunks = []
   #    for d in self.docs:
   #        for i, ch in enumerate(chunk_text(d["text"])):
   #            self.chunks.append({
   #                "doc": d["path"],
   #                "chunk_id": i,
   #                "text": ch,
   #            })

   #    base_name = os.path.basename(d["path"])
   #    save_chunks(self.chunks, f"chunks/{basename}.json")
   #    self.index = build_index(self.chunks)
   #    return len(self.chunks)

   def save_chunks(self, path="chunks/all_chunks.json"):
       with open(path, "w", encoding="utf-8") as f:
           json.dump(self.chunks, f, ensure_ascii=False, indent=2)

   def load_chunks(self, path="chunks/all_chunks.json"):
       with open(path, "r", encoding="utf-8") as f:
           self.chunks = json.load(f)

   def save_index(self, path="chunks/faiss.index"):
       faiss.write_index(self.index, path)

   def load_index(self, path="chunks/faiss.index"):
       self.index = faiss.read_index(path)

   def ingest(self, pattern="data/*", chunk_dir="chunks/"):
       os.makedirs(chunk_dir, exist_ok=True)  # ensure chunk dir exists
       self.docs = read_corpus(pattern)
       self.chunks = []

       for d in self.docs:
           text_chunks = chunk_text(d["text"])
           doc_chunks = []
           for i, ch in enumerate(text_chunks):
               chunk_dict = {
                   "doc": d["path"],
                   "chunk_id": i,
                   "text": ch,
               }
               doc_chunks.append(chunk_dict)
               self.chunks.append(chunk_dict)

           base_name = os.path.basename(d["path"])
           save_chunks(doc_chunks, os.path.join(chunk_dir, base_name + ".chunks.json"))

       self.index = build_index(self.chunks)
       return len(self.chunks)


   def retrieve(self, query, k=TOP_K):
       q_emb = embed_texts([query])
       faiss.normalize_L2(q_emb)
       D, I = self.index.search(q_emb, k)
       results = []
       for score, idx in zip(D[0].tolist(), I[0].tolist()):
           ch = self.chunks[idx]
           results.append({
               "score": float(score),
               "doc": ch["doc"],
               "chunk_id": ch["chunk_id"],
               "text": ch["text"],
           })
       return results


   def answer(self, query, k=TOP_K, threshold=SIM_THRESHOLD):
       hits = self.retrieve(query, k=k)
       filtered = [h for h in hits if h["score"] >= threshold]
       if not filtered:
           return {"answer": "I couldn't find reliable context."}
       context = "\n\n".join([f"[{i+1}] {h['text']}" for i, h in enumerate(filtered)])
       prompt = f"Use only the context to answer. If not found, say so.\n\nContext:\n{context}\n\nQuestion: {query}"
       #prompt = f"Answea the question based on the given context, if the answear isn't contain"
       r = litellm.completion(
           model=MODEL,
           messages=[{"role":"user","content": prompt}],
           max_tokens=300,
           temperature=0.2,
       )
       return {"answer": r.choices[0].message["content"], "hits": filtered}


   def prep(self, data_pattern="data/*", chunk_dir="chunks/"):
       chunks_path = os.path.join(chunk_dir, "all_chunks.json")
       index_path = os.path.join(chunk_dir, "faiss.index")

       # If both saved files exist, load them
       if os.path.exists(chunks_path) and os.path.exists(index_path):
           print("Loading saved chunks and index...")
           self.load_chunks(chunks_path)
           self.load_index(index_path)
       else:
           # Otherwise ingest new data and save
           print("Ingesting data and building index...")
           n = self.ingest(data_pattern, chunk_dir=chunk_dir)
           print(f"Ingested {n} chunks.")
           self.save_chunks(chunks_path)
           self.save_index(index_path)

       return len(self.chunks) if self.chunks else 0
