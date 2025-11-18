# test_intent_retrieval.py
import os
import sys
from pathlib import Path
import logging

# --- Setup Project Path ---
# This is crucial to ensure all modules are found correctly.
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Main Test Logic ---
def test_retrieval():
    """
    Initializes RAGManager and tests intent space retrieval for a specific query.
    """
    try:
        from src.retriever import RAGManager
        logger.info("Successfully imported RAGManager.")
    except Exception as e:
        logger.error(f"Failed to import RAGManager: {e}", exc_info=True)
        return

    try:
        logger.info("Initializing RAGManager...")
        # Make sure to load all configurations correctly
        rag_manager = RAGManager()
        logger.info("RAGManager initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize RAGManager: {e}", exc_info=True)
        return

    if rag_manager.intent_index is None:
        logger.error("Intent index is not available in RAGManager.")
        return

    query = "什么是RAG?"
    top_k = 3 # Let's get top 3 to see what's happening

    logger.info(f"Performing retrieval for query: '{query}' with top_k={top_k}")

    try:
        retriever = rag_manager.intent_index.as_retriever(similarity_top_k=top_k)
        results = retriever.retrieve(query)
    except Exception as e:
        logger.error(f"An error occurred during retrieval: {e}", exc_info=True)
        return

    if not results:
        logger.warning("Retrieval returned no results.")
        return

    logger.info("--- Retrieval Results ---")
    for i, node_with_score in enumerate(results):
        score = node_with_score.score
        text = node_with_score.node.text
        metadata = node_with_score.node.metadata
        logger.info(f"Result {i+1}:")
        logger.info(f"  Score: {score:.4f}")
        logger.info(f"  Matched Question: {text}")
        logger.info(f"  Metadata: {metadata}")
        logger.info("-" * 20)

    highest_score = results[0].score
    logger.info(f"Highest intent score found: {highest_score:.4f}")

if __name__ == "__main__":
    test_retrieval()
