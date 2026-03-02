from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter

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
            "type":"chat_summary"
        }
    )
    
    vectore_store.add_documents([doc])
    #vectore_store.persist()

def store_document_summary(deal_id: str, full_text: str, intake: dict):
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 250,
        chunk_overlap = 40
    )
    chunks = splitter.split_text(full_text)
    documents = []
    
    for i, chunk in enumerate(chunks):
        documents.append(
            Document(
                page_content= chunk,
                metadata = {
                    "deal_id": deal_id,
                    "company_name": intake.get("company_name"),
                    "industry": intake.get("industry"),
                    "deal_type": intake.get("deal_type"),
                    "geography": intake.get("geography"),
                    "type": "document_chunk",
                    "chunk_index": i                    
                }
            )
        )
    vectore_store.add_documents(documents)