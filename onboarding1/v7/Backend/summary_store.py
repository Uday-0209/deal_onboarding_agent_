from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
import os
CHROMA_DIR = os.path.abspath("./chroma_db")

embeddings = HuggingFaceEmbeddings(
    model_name = 'sentence-transformers/all-mpnet-base-v2'
)

vectore_store = Chroma(
    persist_directory=CHROMA_DIR,
    embedding_function=embeddings
)


def store_deal_summary(deal_id: str, summary: str, intake: dict):
    doc = Document(
        page_content = summary,
        metadata = {
            "deal_id": deal_id,
            "company_name": intake.get("company_name"),
            "industry": intake.get("industry"),
            "deal_type": intake.get("deal_type"),
            "geography": intake.get("geography"),
        }
    )
    
    vectore_store.add_documents([doc])
    #vectore_store.persist()

