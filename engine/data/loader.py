"""
TechQA Dataset Loader

Loads and parses the PrimeQA/TechQA dataset from HuggingFace.
Handles both the QA pairs (for fine-tuning) and the technote corpus (for RAG indexing).

Dataset structure:
- Train/Dev/Test splits with question-answer pairs
- ~801K technotes as the retrieval corpus

Usage:
    from engine.data.loader import TechQALoader

    loader = TechQALoader()
    qa_pairs = loader.load_qa_pairs(split="train")
    corpus = loader.load_corpus()
"""

# TODO: Implement in Phase 3
# - load_qa_pairs() for fine-tuning data
# - load_corpus() for RAG indexing
# - Data validation and cleaning
