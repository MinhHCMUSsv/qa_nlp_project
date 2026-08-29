# TechQA Knowledge Base Report

## 1. Retrieval-Augmented Generation (RAG)

### The Retrieve-Generate Stages
Retrieval-Augmented Generation (RAG) is an architectural approach that bridges the gap between a Large Language Model's (LLM) internal knowledge and external, up-to-date, or proprietary data. The process fundamentally consists of two stages:
1. **Retrieve Stage**: When a user submits a query (e.g., a technical question), the system first converts this query into a vector representation. It then searches a pre-built knowledge base (in our case, the TechQA document chunks stored in Qdrant) to find the most contextually relevant documents. This is typically achieved using vector similarity metrics.
2. **Generate Stage**: The retrieved documents (the "context") are concatenated or formatted alongside the original user query. This enriched prompt is then fed into the LLM. The model synthesizes the provided context to generate a coherent, accurate, and context-aware answer.

### The Benefits of Grounding
"Grounding" refers to the practice of tying the LLM's responses to verifiable, external sources rather than relying solely on its pre-trained weights. The benefits of grounding include:
- **Mitigating Hallucinations**: By forcing the model to answer based on the provided retrieved text, the likelihood of the LLM inventing incorrect facts (hallucinations) is significantly reduced.
- **Traceability and Trust**: Grounded responses can be accompanied by citations or references to the source documents (e.g., specific TechQA notes), allowing users to verify the information and building trust in the system.
- **Up-to-date Information**: Without retraining the model, the knowledge base can be continuously updated with new documents, ensuring the LLM's answers reflect the latest data.

### The Role of RAG for Domain-Specific Knowledge
In the context of the TechQA program, answering technical questions often requires highly specialized, domain-specific knowledge that might not be well-represented in the LLM's general training data. RAG plays a critical role here by acting as an external, specialized memory module. Instead of fine-tuning the LLM on the TechQA corpus—which is computationally expensive and hard to update—RAG allows the system to dynamically inject the exact domain-specific technical notes needed to answer a specific question right at inference time. This ensures that the generated answers are highly relevant to the specific domain and accurately reflect the proprietary or specialized information.

## 2. Embedding Model and Vector Search

### Introduction to BGE-M3
For our knowledge base, we utilize the **BGE-M3** (BAAI General Embedding - Multilingual, Multi-granularity, Multi-functionality) model via `HuggingFaceEmbeddings`. BGE-M3 is a state-of-the-art embedding model designed to handle diverse retrieval tasks. It excels in generating high-quality representations for text across multiple languages and varying text lengths, making it ideal for embedding the complex and varied technical documents found in the TechQA dataset.

### Dense Vector Representations
To perform semantic search, text must be translated into a machine-readable format. BGE-M3 transforms our document chunks into **dense vector representations** (embeddings). A dense vector is an array of continuous floating-point numbers that captures the deep semantic meaning of the text. Unlike sparse representations (like TF-IDF or BM25) that rely on exact keyword matches, dense vectors encode concepts, allowing the system to recognize that "error connecting to DB" and "database connection failure" share similar meanings, even if the exact words differ.

### Cosine Similarity and Top-k Retrieval
Once queries and documents are mapped into the same dense vector space, we measure their semantic similarity using metrics such as **Cosine Similarity**. Cosine similarity calculates the cosine of the angle between two vectors. A value closer to 1 indicates that the vectors point in roughly the same direction, implying high semantic similarity. 
During the retrieval phase, the system computes the cosine similarity between the query vector and the document vectors in the database. It then returns the documents with the highest similarity scores. This process is known as **Top-k Retrieval**, where 'k' is the predefined number of most relevant document chunks fetched to form the context for the LLM.

### Document Storage and Indexing in Qdrant Cloud
To scale this process for the large TechQA dataset and overcome RAM limitations, our implementation features a robust streaming and batching pipeline before uploading to **Qdrant Cloud**:
- **Streaming and Text Cleaning**: Instead of loading the entire dataset into memory, we use `ijson` to stream documents. The text is normalized through a `clean_text` step to remove excessive whitespace and formatting issues while preserving technical information. We process these documents in batches (`DOC_BATCH_SIZE = 500`).
- **Section-aware Chunking**: Rather than splitting the whole document blindly, the pipeline is section-aware. It processes distinct sections separately. If sections are unavailable, it falls back to full text. Each section is then independently split using LangChain's `RecursiveCharacterTextSplitter` (`chunk_size = 1000`, `chunk_overlap = 150`). To ensure the LLM understands the context of every chunk, we prepend a metadata header (APAR ID, Title, Section) to each chunk before embedding.
- **Batch Embedding and Deterministic Uploading**: The chunks are embedded using BGE-M3 (`EMBED_BATCH_SIZE = 8`). To make the process fault-tolerant, we generate a deterministic UUID (using UUID5) for each chunk based on its source ID, section index, and chunk index. This enables safe upserts to the Qdrant Cloud collection (`techqa_corpus_bge_m3_section_clean`). A checkpointing mechanism (`techqa_qdrant_section_clean_checkpoint.json`) is implemented to save the state after each successful batch upload. This ensures that if the Colab session disconnects, the process can resume seamlessly without starting over or creating duplicate vectors.
- **Indexing and Retrieval**: Qdrant stores these document chunks as payloads alongside their dense vectors. To ensure rapid retrieval across potentially millions of vectors, Qdrant builds an index using the **HNSW (Hierarchical Navigable Small World)** algorithm. This allows Qdrant to perform approximate nearest neighbor (ANN) searches, returning the top-k results in logarithmic time (as demonstrated by our `client.query_points(query, limit=5)` calls).

## 3. Technote Corpus Preprocessing

To ensure high-quality retrieval and accurate generation, the IBM Technote corpus undergoes a dedicated preprocessing pipeline before embedding and indexing. This pipeline transforms raw, loosely structured records into highly contextualized vector points.

### Document Cleaning
Raw technical notes often contain inconsistent formatting. The `clean_text` function normalizes the text by:
- Replacing carriage returns (`\r\n`, `\r`) with standard newlines.
- Stripping leading and trailing whitespace from every line.
- Collapsing multiple consecutive blank lines into a single blank line to preserve paragraph boundaries without wasting tokens on empty space.
- Normalizing repeated spaces or tabs within lines into a single space.
This light cleaning ensures that critical technical information is preserved while formatting noise is removed.

### Section-Aware Processing and Filtering
Rather than treating an entire APAR document as a single continuous block of text, the pipeline extracts content iteratively section by section (e.g., ERROR DESCRIPTION, LOCAL FIX, PROBLEM CONCLUSION).
- **Filtering Criteria**: Sections that are completely empty or missing valid content are automatically skipped. 
- **Fallback Mechanism**: If a document has no valid sections, the pipeline falls back to using the full document text as a single "FULL_DOCUMENT" section.

### Text Chunking for Retrieval
To fit within the embedding model's optimal context length and the LLM's prompt limitations, each valid section is chunked independently.
- **Chunking Parameters**: We use LangChain's `RecursiveCharacterTextSplitter` configured with a `chunk_size` of 1000 characters and a `chunk_overlap` of 150 characters. 
- **Semantic Boundaries**: By splitting sections independently, we guarantee that chunks do not arbitrarily cross over semantic boundaries (e.g., mixing a bug description with a patch instruction).

### Metadata Preservation and Prepending
To provide maximum context to the LLM when a single chunk is retrieved out of isolation, metadata is preserved both structurally and textually:
- **Header Prepending**: A header is injected at the top of every chunk's text content (containing `APAR ID`, `Title`, and `Section`). This allows the LLM to instantly understand what document and section the chunk belongs to without needing to parse external JSON fields.
- **Payload Metadata**: The Qdrant payload natively preserves structural metadata such as `id`, `source_id`, `title`, `section`, `section_index`, and `chunk_index`.

### Duplicate Removal via Deterministic IDs
To handle interruptions and prevent storing duplicate vectors during batched uploads, the system computes a deterministic UUID (UUID5) for each chunk. The UUID is generated using a stable combination of the `source_id`, `section_index`, and `chunk_index`. If a batch is re-run due to a crash, Qdrant performs a safe upsert (overwriting the existing point with the same ID) rather than creating a duplicate entry.

### Final Format for Indexing
The final processed chunk is structured as a Qdrant `PointStruct` ready for uploading, containing:
- **`id`**: The deterministic UUID5 string.
- **`vector`**: The 1024-dimensional dense vector generated by the BGE-M3 model.
- **`payload`**: A JSON object containing the `page_content` (the text with the prepended header) and the structured `metadata` dictionary.

## 4. Document Indexing

### Loading and Chunking
Due to the large size of the TechQA corpus (approximately 800,000 documents), documents are loaded using a memory-efficient streaming approach with the `ijson` library. Technotes are processed in manageable batches (`DOC_BATCH_SIZE = 500`). 

**Targeted Corpus Scope**: While the full TechQA corpus contains approximately 800,000 documents, our program explicitly limits the active knowledge base to a targeted subset of 50,000 documents (`MAX_DOCS = 50000`). This operational design choice is directly driven by practical infrastructure constraints: the pipeline operates on the free tier of Google Colab (utilizing the T4 GPU) and the free tier of Qdrant Cloud. Processing and indexing the entire 800,000-document corpus with 1024-dimensional dense vectors would quickly exceed Colab's session time limits and Qdrant Cloud's free-tier storage quotas (typically 1GB RAM/Disk). By bounding the scope to 50,000 documents, the knowledge base remains operationally robust and highly relevant while strictly adhering to these cloud resource limitations.

The chunking process is section-aware; each distinct section (e.g., ERROR DESCRIPTION, LOCAL FIX) is independently split using LangChain's `RecursiveCharacterTextSplitter` with a `chunk_size` of 1000 characters and a `chunk_overlap` of 150 characters. This ensures that chunks do not arbitrarily cross semantic boundaries.

### Embedding Generation
Once chunked, the text is converted into dense vector representations. We utilize the **BGE-M3** model (`BAAI/bge-m3`) via `HuggingFaceEmbeddings`. The model outputs **1024-dimensional** embeddings for each chunk. Batched embedding (`EMBED_BATCH_SIZE = 8`) on a GPU is used to accelerate this computationally intensive process, producing high-quality vectors that capture the deep semantic meaning of the technical notes.

### Storage and Updating in Qdrant
The generated 1024-dimensional vectors and their corresponding textual metadata are stored in a **Qdrant Cloud** collection. To ensure fault tolerance and safe updates:
- **Deterministic IDs**: A stable UUID (UUID5) is generated for each chunk based on its source APAR ID, section index, and chunk index.
- **Upsert Mechanism**: When a batch is uploaded, Qdrant uses an `upsert` operation. If a chunk's ID already exists in the collection (e.g., when resuming from a failed batch upload), its vector and metadata are safely updated rather than duplicated.
- **Payload**: The chunk's text (prepended with context headers) and structured metadata are stored within the Qdrant point's `payload`, keeping all necessary information linked directly to the vector.

## 5. Retrieval Module

### Question Embedding and Similarity
When a user submits a query, the **Retrieval Module** first passes the raw text query through the exact same `BAAI/bge-m3` model to produce a 1024-dimensional query vector. Crucially, `normalize_embeddings=True` is used to ensure all vectors are L2-normalized. The similarity between the query vector and the document vectors in the Qdrant index is measured using **Cosine Similarity**, which evaluates the semantic alignment between the two points in the high-dimensional space.

### Top-k Selection and Score Thresholds
The system uses Qdrant's native `query_points` API to perform an approximate nearest neighbor (ANN) search. 
- **Top-k**: The retrieval is configured to select the most relevant chunks by setting a hard limit (e.g., `limit=5`).
- **Score Thresholds**: Along with the payload, Qdrant returns a cosine similarity score for each matched point. These continuous scores (ranging up to 1.0) allow the system to apply a score threshold in the future, filtering out low-confidence results if the query is out-of-domain or too ambiguous.

### Context Format for Generation
The retrieved points contain the `page_content` in their payloads. Because of our preprocessing pipeline, this content is not just an isolated snippet. It is formatted with a prepended header, yielding the following context format:
```text
APAR ID: [Source ID]
Title: [Technote Title]
Section: [Section Name]

[Chunk Text Content...]
```
This structured context is concatenated and passed directly to the generator LLM. The explicit metadata headers guarantee that the LLM is fully aware of the document origin and logical section of every retrieved chunk, maximizing the accuracy and traceability of the final answer.

## 6. End-to-End RAG Pipeline

### Complete Inference Flow
The end-to-end Retrieval-Augmented Generation (RAG) pipeline is fully encapsulated within the FastAPI backend (orchestrated through `qa_service.py` and `engine/pipeline.py`). When a user submits a technical question via the application interface, the following inference flow is triggered:
1. **Query Processing**: The raw query is received by the API endpoint and passed to the QA service. If the query is a simple greeting or non-technical chit-chat, the system intercepts it with a predefined conversational response, saving computational resources.
2. **Dense Retrieval**: For technical queries, the query is passed to the `BGEM3Embedder` to generate a 1024-dimensional normalized vector. This vector is then sent to Qdrant Cloud via the `QdrantVectorStore`. 
3. **Context Selection**: Qdrant performs a Cosine Similarity search and returns the top-k most relevant chunks along with their payloads (containing the text and metadata).
4. **Context Formatting**: The retrieved text chunks (which natively contain their metadata headers) are concatenated together into a single unified context block.
5. **Prompt Augmentation**: The user's query and the concatenated context block are formatted into a precise prompt structure using the Llama 3 Chat Template (with specific system instructions guiding the model to rely on the provided context).
6. **Generation**: The prompt is fed into the fine-tuned `AQUABOT/Llama-3.2-3B-TechQA` model (managed by `LlamaGenerator`). The model synthesizes the context and generates an accurate, domain-specific technical answer.
7. **Response Delivery**: The generated answer, along with the source references and latency metrics, is packaged into a structured JSON response and returned to the frontend.

### Handling Unrelated Queries or Missing Context
A robust RAG system must handle scenarios where the knowledge base does not contain information relevant to the user's query:
- **Empty Retrieval & Direct LLM Fallback**: If Qdrant returns no results, or if the user explicitly toggles the system to "Direct LLM" mode, the pipeline dynamically adjusts the prompt. It omits the `### Reference Context:` section entirely and switches to a standard `DEFAULT_SYSTEM_PROMPT`. The generator then attempts to answer the question using only its internal pre-trained weights (and fine-tuned knowledge).
- **Missing Information Clause**: When context *is* found but is insufficient, the `RAG_SYSTEM_PROMPT` explicitly instructs the LLM: *"If the context does not contain enough information to resolve the issue, state clearly what is known and what is missing."* This constraint acts as a safeguard, preventing the model from hallucinating technical steps when the retrieved documents are only marginally related to the query.

### Mechanism for Returning Source References
Transparency and trust are paramount in technical support. To achieve this, the pipeline is designed to preserve and return verifiable source references alongside every generated answer:
- **Source Tracing**: When documents are retrieved from Qdrant, their structural metadata (e.g., `id`, `title`, `url`, `category`) is carefully preserved. The `qa_service` maps these raw Qdrant points into a structured list of `SourceDocument` objects.
- **API Response Structure**: The final API response (`AnswerResponse`) contains not just the generated `answer` string, but also a `sources` array. 
- **Frontend Display**: This allows the frontend interface to display the exact Technote titles, Document IDs, and Similarity Scores that were used to ground the answer. Users can expand these references to verify the original text or click the provided URLs (if available) to navigate directly to the official IBM documentation.
