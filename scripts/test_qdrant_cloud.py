import warnings
warnings.filterwarnings('ignore')

from langchain_qdrant import QdrantVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from qdrant_client import QdrantClient
import os
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# CẤU HÌNH QDRANT CLOUD
# ==========================================
QDRANT_CLOUD_URL = os.getenv(
    "QDRANT_URL",
    "https://f3636289-cb7b-42b1-ab07-b17b6ef9c217.sa-east-1-0.aws.cloud.qdrant.io"
)
QDRANT_CLOUD_API_KEY = os.getenv(
    "QDRANT_API_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwic3ViamVjdCI6ImFwaS1rZXk6NGJkZjVlMWYtYTk0NS00MmZjLWI4MGUtOWMyYTk0ZDQ2NTBlIn0.t2AGHYbrZ8Ddb-eYNwzxygYywaYD8W9vDtm-YBHzOcM"
)

def test_qdrant_cloud_query():
    print("1. Loading embeddings (BAAI/bge-m3)...")
    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-m3",
        model_kwargs={'device': 'cpu'}
    )
    
    print(f"2. Connecting to Qdrant Cloud ({QDRANT_CLOUD_URL})...")
    client = QdrantClient(
        url=QDRANT_CLOUD_URL,
        api_key=QDRANT_CLOUD_API_KEY
    )

    print("3. Loading vector store from Cloud...")
    qdrant = QdrantVectorStore(
        client=client,
        collection_name="techqa_corpus_bge_m3_section_clean",
        embedding=embeddings
    )
    
    query = "Web GUI 8.1 FP7 requires DASH 3.1.2.1 or later"
    print(f"\n4. Đang tìm kiếm (Truy vấn: '{query}')")
    results = qdrant.similarity_search(query, k=3)
    
    print("\n--- KẾT QUẢ TÌM KIẾM TỪ CLOUD ---")
    if not results:
        print("Không tìm thấy kết quả nào!")
    for i, res in enumerate(results):
        print(f"\n[Kết quả {i+1}]")
        print("Nội dung:", res.page_content[:300] + "...")
        print("Metadata:", {k: v for k, v in res.metadata.items() if k not in ['page_content', '_id', '_collection_name']})

if __name__ == "__main__":
    test_qdrant_cloud_query()
