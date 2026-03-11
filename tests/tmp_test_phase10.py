import asyncio
from unittest.mock import MagicMock
from analyzer.text_processor import discover_new_technologies, get_category
from analyzer.embeddings import get_embedding_generator

def test_discovery():
    print("=== Testing Tech Discovery ===")
    emb_gen = get_embedding_generator()
    unknown_topics = ["agentic-ai", "rag-pipeline", "rust-web-framework", "cat-pictures", "personal-blog"]
    discovered = discover_new_technologies(unknown_topics, emb_gen)
    print("Discovered Mapping:", discovered)
    print("Test get_category for rag-pipeline:", get_category("rag-pipeline"))

if __name__ == "__main__":
    test_discovery()
