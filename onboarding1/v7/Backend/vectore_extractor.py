from v7.Backend.redis_client import (
    get_messages,
    get_intake_field
)
from v7.Backend.summary_generator import generate_deal_summary
from v7.Backend.summary_store import store_deal_summary, vectore_store


# 🔴 CHANGE THIS to a real deal_id from Redis
# DEAL_ID = "6a2f3b18-6a00-45e2-9e54-6312d713c589"


# def search_deals(query):
#     # print("\n🔍 Fetching intake fields...")
#     # intake = get_intake_field(DEAL_ID)
#     # print(intake)

#     # if not intake:
#     #     print("❌ No intake fields found. Extraction may not have run.")
#     #     return

#     # print("\n💬 Fetching full conversation...")
#     # messages = get_messages(DEAL_ID)
#     # for m in messages:
#     #     print(f"{m['role'].upper()}: {m['content']}")

#     # print("\n🧠 Generating deal summary using LLM...")
#     # summary = generate_deal_summary(DEAL_ID)
#     # print("\n📄 GENERATED SUMMARY:\n")
#     # print(summary)

#     # print("\n💾 Storing summary in ChromaDB...")
#     # store_deal_summary(DEAL_ID, summary, intake)

#     print("\n🔎 Testing semantic retrieval from ChromaDB...")
    # results = vectore_store.similarity_search(
    #     query=query,
    #     k=10
    # )

    # if results:
    #     print("\n✅ RETRIEVED FROM CHROMA:\n")
    #     print(results[0].page_content)
    #     print("\n📎 METADATA:")
    #     print(results[0].metadata)
    #     return 
    # else:
    #     print("❌ No results found in ChromaDB")

    # print("\n🎉 TEST COMPLETED SUCCESSFULLY")

def search_deals(query: str, k: int = 1):

    results = vectore_store.similarity_search(
        query=query,
        k=k
    )

    formatted_results = []

    for doc in results:
        formatted_results.append({
            "summary": doc.page_content,
            "metadata": doc.metadata
        })

    return formatted_results

# if __name__ == "__main__":
#     search_deals('real estate')
if __name__ == "__main__":
    output = search_deals("real estate")
    print(output)
