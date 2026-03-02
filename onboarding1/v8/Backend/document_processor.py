from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from v8.Backend.redis_client import redis_client, get_intake_field, update_deal_meta_data
from v8.Backend.llm_client import chat_llm, extract_document_parameters
from v8.Backend.summary_store import store_document_summary
import json
import re

def clean_document_text(text: str) -> str:

    # 1️⃣ Remove duplicate section headers
    text = re.sub(r"(Employment Impact\s+){2,}", "Employment Impact\n", text)

    # 2️⃣ Fix words split across lines with hyphen
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)

    # 3️⃣ Replace newline inside sentences with space
    text = re.sub(r"(?<!\.)\n", " ", text)

    # 4️⃣ Remove multiple spaces
    text = re.sub(r"\s{2,}", " ", text)

    # 5️⃣ Remove stray spaces before punctuation
    text = re.sub(r"\s+([.,])", r"\1", text)

    # 6️⃣ Final strip
    text = text.strip()

    return text
# def process_document(deal_id: str, file_path: str, intake: dict):
#     try:
#         loader = PyMuPDFLoader(file_path)

#         docs = loader.load()
#         print(docs)

#         # splitter = RecursiveCharacterTextSplitter(
#         #     chunk_size = 1000,
#         #     chunk_overlap = 150
#         # )

#         # chunks = splitter.split_documents(docs)
#         full_text = "\n".join(doc.page_content for doc in docs)
#         #intake = get_intake_field(deal_id)
#         print(clean_document_text(full_text))
#         cleaned_text = clean_document_text(full_text)
        
#         store_document_summary(deal_id, cleaned_text, intake)       
        

#         update_deal_meta_data(
#             deal_id, 
#             {"doc_status":"completed"}
#         )
#         #return cleaned
#         print('The extracted doc info is stored as vector in VDB')
#         #return 'The extracted doc info is stored as vector in VDB'
#     except Exception as e:
        
#         update_deal_meta_data(
#             deal_id,
#             {"doc_status": "failed"}
#         )
#         print('document processing failed')
    
def process_document(deal_id: str, file_path: str):
    try:
        loader = PyMuPDFLoader(file_path)

        docs = loader.load()
        print(docs)

        # splitter = RecursiveCharacterTextSplitter(
        #     chunk_size = 1000,
        #     chunk_overlap = 150
        # )

        # chunks = splitter.split_documents(docs)
        full_text = "\n".join(doc.page_content for doc in docs)
        intake = get_intake_field(deal_id)
        print(clean_document_text(full_text))
        cleaned_text = clean_document_text(full_text)
        
        store_document_summary(deal_id, cleaned_text, intake)       
        

        update_deal_meta_data(
            deal_id, 
            {"doc_status":"completed"}
        )
        #return cleaned
        print('The extracted doc info is stored as vector in VDB')
        #return 'The extracted doc info is stored as vector in VDB'
    except Exception as e:
        
        update_deal_meta_data(
            deal_id,
            {"doc_status": "failed"}
        )
        print('document processing failed')
    # extracted = extract_document_parameters(full_text)
    # return extracted
    # if extracted:
    #     store_extended_data(deal_id, extracted)
        
        