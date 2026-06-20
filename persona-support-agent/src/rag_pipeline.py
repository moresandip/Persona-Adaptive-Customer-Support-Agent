import os
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from google import genai
import chromadb
from src import config

class LocalRAGPipeline:
    def __init__(self, db_dir=None):
        if db_dir is None:
            db_dir = config.CHROMA_DB_DIR
            
        self.chroma_client = chromadb.PersistentClient(path=db_dir)
        self.collection = self.chroma_client.get_or_create_collection(
            name="support_kb",
            metadata={"hnsw:space": "cosine"}
        )
        self._client = None

    @property
    def client(self):
        if self._client is None:
            api_key = config.GEMINI_API_KEY
            if not api_key:
                api_key = os.environ.get("GEMINI_API_KEY", "")
            if not api_key:
                raise ValueError("No Google Gemini API Key found. Please add your key in the sidebar or configured .env.")
            self._client = genai.Client(api_key=api_key)
        return self._client


    def get_embedding(self, text: str) -> list:
        """Calls Gemini text-embedding-004 to create a dense vector embedding."""
        try:
            response = self.client.models.embed_content(
                model=config.EMBEDDING_MODEL,
                contents=text
            )
            return response.embeddings[0].values
        except Exception as e:
            # Return a zero vector fallback in case of API exception for structural safety
            print(f"Embedding API error: {e}")
            return [0.0] * 768

    def parse_document(self, filepath: str) -> tuple[str, list[dict]]:
        """Parses txt, md, and pdf files returning full content and chunk-level metadata."""
        ext = os.path.splitext(filepath)[1].lower()
        filename = os.path.basename(filepath)
        
        if ext in ['.txt', '.md']:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            return content, [{"source": filename, "type": ext[1:], "page": 1}]
            
        elif ext == '.pdf':
            pdf_text = ""
            reader = PdfReader(filepath)
            page_metadatas = []
            
            for idx, page in enumerate(reader.pages):
                page_num = idx + 1
                page_text = page.extract_text() or ""
                pdf_text += page_text + "\n"
                
                # We store character offsets to map chunk positions to page numbers if possible, 
                # but for simplicity, we map chunks based on approximate content or page metadata.
                # In this system, we will store page markers in the text or associate pages.
                # Let's save a list of page boundaries.
                page_metadatas.append({
                    "page_num": page_num,
                    "text_length": len(page_text)
                })
                
            return pdf_text, page_metadatas
            
        else:
            raise ValueError(f"Unsupported file type: {ext}")

    def ingest_document(self, filepath: str):
        """Extracts text, chunks it, converts to embeddings, and indexes in ChromaDB."""
        filename = os.path.basename(filepath)
        
        try:
            content, raw_meta = self.parse_document(filepath)
        except Exception as e:
            print(f"Error parsing {filepath}: {e}")
            return
            
        if not content.strip():
            print(f"Skipping empty document: {filename}")
            return

        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = splitter.split_text(content)

        # Track character offset to map chunk to page number for PDFs
        current_char_offset = 0
        
        for idx, chunk in enumerate(chunks):
            embedding = self.get_embedding(chunk)
            chunk_id = f"{filename}_chunk_{idx}"
            
            # Map chunk back to page number for PDFs
            page_num = 1
            if filepath.endswith('.pdf'):
                accumulated = 0
                for pm in raw_meta:
                    accumulated += pm["text_length"] + 1 # +1 for newline
                    if current_char_offset < accumulated:
                        page_num = pm["page_num"]
                        break
            
            current_char_offset += len(chunk)

            self.collection.add(
                ids=[chunk_id],
                embeddings=[embedding],
                metadatas=[{
                    "source": filename,
                    "chunk_index": idx,
                    "page": page_num
                }],
                documents=[chunk]
            )
        print(f"Ingested {filename}: split into {len(chunks)} chunks.")

    def ingest_directory(self, directory_path: str, force_reindex: bool = False):
        """Ingests all valid text, markdown, and PDF documents in the directory."""
        if not os.path.exists(directory_path):
            print(f"Directory {directory_path} does not exist.")
            return

        if force_reindex:
            print("Clearing existing collections in vector DB.")
            self.chroma_client.delete_collection("support_kb")
            self.collection = self.chroma_client.create_collection(
                name="support_kb",
                metadata={"hnsw:space": "cosine"}
            )
        elif self.collection.count() > 0:
            print(f"Chroma DB already populated with {self.collection.count()} chunks. Skipping ingestion.")
            return

        for filename in os.listdir(directory_path):
            filepath = os.path.join(directory_path, filename)
            if os.path.isfile(filepath) and filename.lower().endswith(('.txt', '.md', '.pdf')):
                print(f"Processing document for index: {filename}")
                self.ingest_document(filepath)

    def retrieve_context(self, query: str, top_k: int = 3) -> list[dict]:
        """Queries ChromaDB using Cosine similarity. Returns top-k matching snippets."""
        if self.collection.count() == 0:
            print("Vector database is empty. Call ingest_directory first.")
            return []

        query_vector = self.get_embedding(query)

        results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=top_k
        )

        retrieved_items = []
        if results and results['documents'] and len(results['documents']) > 0:
            docs = results['documents'][0]
            metas = results['metadatas'][0]
            distances = results['distances'][0] if results['distances'] else [1.0] * len(docs)

            for i in range(len(docs)):
                # In ChromaDB with HNSW cosine, distance ranges from 0.0 (exact match) to 2.0
                # Similarity is calculated as: 1 - distance
                similarity = 1.0 - distances[i]
                
                # Keep score within reasonable bounds [0.0, 1.0]
                similarity = max(0.0, min(1.0, similarity))

                retrieved_items.append({
                    "text": docs[i],
                    "source": metas[i].get("source", "Unknown"),
                    "page": metas[i].get("page", 1),
                    "score": round(similarity, 4)
                })
                
        # Sort by similarity score descending
        retrieved_items.sort(key=lambda x: x["score"], reverse=True)
        return retrieved_items
