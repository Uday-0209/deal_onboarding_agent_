from v4.Backend.summary_store import store_deal_summary, vectore_store

def run_test():
    deal_id = "test-deal-001"

    summary = """
    ABC Fintech is a Singapore-based fintech startup seeking $5M in Series A funding.
    The company operates in the payments space and is expanding across Southeast Asia.
    """

    intake = {
        "company_name": "ABC Fintech",
        "industry": "Fintech",
        "deal_type": "Series A",
        "deal_size": "$5M",
        "geography": "Singapore",
    }

    print("🔹 Storing deal summary...")
    store_deal_summary(deal_id, summary, intake)

    print("🔹 Running similarity search...")
    results = vectore_store.similarity_search(
        "fintech startup in singapore",
        k=1
    )

    print("\n✅ Retrieved document:")
    print("-" * 50)
    print(results[0].page_content)
    print("-" * 50)
    print("Metadata:", results[0].metadata)


if __name__ == "__main__":
    run_test()