import streamlit as st
import requests

BACKEND = "http://localhost:8000"

st.set_page_config(page_title="Deal Intake", layout="centered")
st.title("Deal Intake Assistant")

# =========================
# SESSION STATE
# =========================

if "email" not in st.session_state:
    st.session_state.email = ""

if "deal_id" not in st.session_state:
    st.session_state.deal_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Chat"

# =========================
# EMAIL GATE
# =========================

if not st.session_state.email:
    st.session_state.email = st.text_input(
        "Enter your email to start:",
        placeholder="you@company.com"
    )
    st.stop()

# =========================
# TAB SWITCHER
# =========================

col1, col2 = st.columns(2)

with col1:
    if st.button("💬 Chat", use_container_width=True):
        st.session_state.active_tab = "Chat"

with col2:
    if st.button("🔎 RAG Retrival", use_container_width=True):
        st.session_state.active_tab = "Search"

st.divider()

# =========================
# SIDEBAR (ONLY FOR CHAT)
# =========================

if st.session_state.active_tab == "Chat":
    with st.sidebar:
        st.title("Your Deals")

        if st.button("➕ New Deal"):
            st.session_state.deal_id = None
            st.session_state.messages = []
            st.rerun()

        try:
            resp = requests.get(
                f"{BACKEND}/deals",
                params={"email": st.session_state.email},
                timeout=10
            )
            deals = resp.json()
        except Exception:
            deals = []

        st.divider()

        for deal in deals:
            label = deal["title"]
            if st.button(label, key=deal["deal_id"]):
                st.session_state.deal_id = deal["deal_id"]

                msgs = requests.get(
                    f"{BACKEND}/deals/{deal['deal_id']}/messages",
                    timeout=10
                ).json()

                st.session_state.messages = msgs
                st.rerun()

# =========================
# 💬 CHAT TAB
# =========================

if st.session_state.active_tab == "Chat":

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    user_input = st.chat_input("Describe your deal...")

    if user_input:
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })

        payload = {
            "email": st.session_state.email,
            "deal_id": st.session_state.deal_id,
            "message": user_input
        }

        # response = requests.post(
        #     f"{BACKEND}/chat",
        #     json=payload,
        #     timeout=120
        # ).json()
        try:            
            resp = requests.post(
                f"{BACKEND}/chat",
                json=payload,
                timeout=120
            )

            if resp.status_code != 200:
                st.error(f"Backend error: {resp.status_code}")
                st.stop()

            response = resp.json()

        except Exception as e:
            st.error("Failed to connect to backend.")
            st.stop()

        st.session_state.deal_id = response["deal_id"]

        st.session_state.messages.append({
            "role": "assistant",
            "content": response["reply"]
        })

        st.rerun()

# =========================
# 🔎 VECTOR SEARCH TAB
# =========================

if st.session_state.active_tab == "Search":

    st.subheader("Search Similar Deals")

    query = st.text_input(
        "Enter your search query",
        placeholder="Commercial real estate in Bangalore"
    )

    if st.button("Search Deals"):
        if query.strip():

            try:
                results = requests.get(
                    f"{BACKEND}/search",
                    params={"query": query},
                    timeout=20
                ).json()
            except Exception:
                results = []

        #     if results:
        #         for result in results:

        #             meta = result.get("metadata", {})
        #             summary = result.get("summary", "")

        #             company = meta.get("company_name", "Unknown Company")
        #             industry = meta.get("industry", "N/A")
        #             deal_type = meta.get("deal_type", "N/A")
        #             geography = meta.get("geography", "N/A")
        #             deal_id = meta.get("deal_id", "")

        #             # ---- Professional Card Layout ----
        #             st.markdown(f"## 🏢 {company}")

        #             col1, col2 = st.columns(2)

        #             with col1:
        #                 st.write(f"**Deal Type:** {deal_type}")
        #                 st.write(f"**Industry:** {industry.title()}")

        #             with col2:
        #                 st.write(f"**Location:** {geography}")
        #                 if deal_id:
        #                     st.caption(f"Deal ID: {deal_id[:8]}")

        #             st.divider()

        #             st.markdown("### 📝 Deal Summary")
        #             st.write(summary)

        #             st.divider()

        #     else:
        #         st.warning("No similar deals found.")
        # else:
        #     st.warning("Please enter a search query.")
        if results:
            for result in results:

                meta = result.get("metadata", {})
                summary = result.get("summary", "")

                company = meta.get("company_name", "Unknown Company")
                industry = meta.get("industry", "N/A")
                deal_type = meta.get("deal_type", "N/A")
                geography = meta.get("geography", "N/A")
                deal_id = meta.get("deal_id", "")

                # ---- Professional Card Layout ----
                with st.container():

                    st.markdown(f"## 🏢 {company}")

                    col1, col2 = st.columns(2)

                    with col1:
                        st.write(f"**Deal Type:** {deal_type}")
                        st.write(f"**Industry:** {industry.title()}")

                    with col2:
                        st.write(f"**Location:** {geography}")
                        if deal_id:
                            st.caption(f"Deal ID: {deal_id[:8]}")

                    st.markdown("### 📝 Deal Summary")
                    st.write(summary)

                    st.divider()
        else:
            st.warning("No similar deals found.")

# =========================
# DOCUMENT UPLOAD SECTION
# =========================

doc_requested = False
doc_status = None

if st.session_state.deal_id:
    try:
        meta = requests.get(
            f"{BACKEND}/deals/{st.session_state.deal_id}/meta",
            timeout = 10            
        ).json()
        
        doc_requested = meta.get('documents_requested')
        doc_stats = meta.get("deal_status")
    except Exception:
        pass
    
if doc_requested:

    st.divider()
    st.subheader("📄 Upload Supporting Documents")

    if doc_status == "processing":
        st.info("Document is being processed...")

    elif doc_status == "completed":
        st.success("Document processed successfully!")

    elif doc_status == "failed":
        st.error("Document processing failed. Please retry.")

    if doc_requested:

        uploaded_file = st.file_uploader(
            "Drag and drop or browse PDF file",
            type=["pdf"],
            key="doc_upload"
        )

        if uploaded_file is not None and not st.session_state.get("upload_in_progress", False):
            
            st.session_state.upload_in_progress = True

            with st.spinner("Uploading and processing..."):

                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        "application/pdf"
                    )
                }

                response = requests.post(
                    f"{BACKEND}/deals/{st.session_state.deal_id}/upload",
                    files=files,
                    timeout=120
                )

            if response.status_code == 200:
                st.success("Upload successful. Processing started.")
                st.rerun()
            else:
                st.error("Upload failed.")
            st.session_state.upload_in_progress = False
            st.rerun()
