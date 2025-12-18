from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from config.settings import OPENAI_API_KEY, EMBED_MODEL, CHROMA_DIR
from core.usage_tracker import get_tracker

def get_embeddings(track_usage=True):
    """
    Initialize OpenAI embedding model with optional usage tracking.
    
    Parameters
    ----------
    track_usage : bool
        If True, tracks token usage and costs
    """
    embeddings = OpenAIEmbeddings(model=EMBED_MODEL, api_key=OPENAI_API_KEY, max_retries=10)
    
    if track_usage:
        # Wrap embed_documents to track usage
        original_embed_documents = embeddings.embed_documents
        def tracked_embed_documents(texts, *args, **kwargs):
            result = original_embed_documents(texts, *args, **kwargs)
            # Estimate tokens (rough approximation: ~4 chars = 1 token)
            total_chars = sum(len(text) for text in texts)
            estimated_tokens = total_chars // 4
            tracker = get_tracker()
            tracker.track_embedding_call(model=EMBED_MODEL, tokens=estimated_tokens)
            return result
        embeddings.embed_documents = tracked_embed_documents
        
        # Wrap embed_query to track usage
        original_embed_query = embeddings.embed_query
        def tracked_embed_query(text, *args, **kwargs):
            result = original_embed_query(text, *args, **kwargs)
            estimated_tokens = len(text) // 4
            tracker = get_tracker()
            tracker.track_embedding_call(model=EMBED_MODEL, tokens=estimated_tokens)
            return result
        embeddings.embed_query = tracked_embed_query
    
    return embeddings

def get_vectorstore(collection_name='test'):
    """Load (or create empty) ChromaDB vectorstore."""
    embeddings = get_embeddings()
    vectordb = Chroma(collection_name = collection_name, persist_directory=CHROMA_DIR, embedding_function=embeddings)
    return vectordb

def main():
    emb = get_embeddings()
    vector = emb.embed_query("deep learning microscopy image analysis")
    print("Embedding vector length:", len(vector))
    print("Example values:", vector[:10])
    vectordb = get_vectorstore()
    print("💾 Loaded Chroma directory:", CHROMA_DIR)

def list_collections():
    chroma = Chroma(persist_directory=CHROMA_DIR)
    print("Collections:", chroma._client.list_collections())

if __name__ == "__main__":
    list_collections()
