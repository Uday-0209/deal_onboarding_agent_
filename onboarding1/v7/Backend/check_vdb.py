from v7.Backend.summary_store import vectore_store

def dump_all_vectors():
    collection = vectore_store._collection

    data = collection.get(
        include=["documents", "metadatas"]
    )

    ids = data.get("ids", [])
    documents = data.get("documents", [])
    metadatas = data.get("metadatas", [])

    print(f"\n📦 TOTAL DOCUMENTS IN VDB: {len(ids)}\n")

    if not ids:
        print("❌ VDB IS EMPTY")
        return

    for i in range(len(ids)):
        print("🆔 VECTOR ID:", ids[i])
        print("📄 CONTENT:")
        print(documents[i])
        print("🏷️ METADATA:")
        for k, v in metadatas[i].items():
            print(f"   {k}: {v}")
        print("-" * 70)


if __name__ == "__main__":
    dump_all_vectors()
