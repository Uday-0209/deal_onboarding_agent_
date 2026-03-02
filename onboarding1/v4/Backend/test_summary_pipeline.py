from v4.Backend.redis_client import (
    get_messages,
    get_intake_field
)
from v4.Backend.summary_generator import generate_deal_summary
from v4.Backend.summary_store import store_deal_summary, vectore_store


# 🔴 CHANGE THIS to a real deal_id from Redis
DEAL_ID = "e6697d35-a072-47a7-9f64-ff9f7eb0ac4f"


def main():
    # print("\n🔍 Fetching intake fields...")
    # intake = get_intake_field(DEAL_ID)
    # print(intake)

    # if not intake:
    #     print("❌ No intake fields found. Extraction may not have run.")
    #     return

    # print("\n💬 Fetching full conversation...")
    # messages = get_messages(DEAL_ID)
    # for m in messages:
    #     print(f"{m['role'].upper()}: {m['content']}")

    # print("\n🧠 Generating deal summary using LLM...")
    # summary = generate_deal_summary(DEAL_ID)
    # print("\n📄 GENERATED SUMMARY:\n")
    # print(summary)

    # print("\n💾 Storing summary in ChromaDB...")
    # store_deal_summary(DEAL_ID, summary, intake)

    # print("\n🔎 Testing semantic retrieval from ChromaDB...")
    results = vectore_store.similarity_search(
        query="equity sale",
        k=1
    )

    if results:
        print("\n✅ RETRIEVED FROM CHROMA:\n")
        print(results[0].page_content)
        print("\n📎 METADATA:")
        print(results[0].metadata)
    else:
        print("❌ No results found in ChromaDB")

    print("\n🎉 TEST COMPLETED SUCCESSFULLY")


if __name__ == "__main__":
    main()
