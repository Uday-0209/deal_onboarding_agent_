from v8.Backend.summary_store import vectore_store

def delete_by_deal_id(deal_id: str):
    vectore_store.delete(where={"company_name": deal_id})
    print(f"✅ Deleted vectors for deal_id: {deal_id}")


if __name__ == "__main__":
    delete_by_deal_id("Stockies")
