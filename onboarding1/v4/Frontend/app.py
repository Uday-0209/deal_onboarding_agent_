import streamlit as st
import requests
import uuid

BACKEND = "http://localhost:8000"

st.set_page_config(page_title="Deal Intake", layout="centered")
st.title("Deal Intake Assistant")

# -------------------------
# Session state
# -------------------------

if "email" not in st.session_state:
    st.session_state.email = ""

if "deal_id" not in st.session_state:
    st.session_state.deal_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []


# -------------------------
# Email gate
# -------------------------

if not st.session_state.email:
    st.session_state.email = st.text_input(
        "Enter your email to start:",
        placeholder="you@company.com"
    )
    st.stop()


# -------------------------
# Render chat
# -------------------------

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])


# -------------------------
# Chat input
# -------------------------

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

    response = requests.post(
        f"{BACKEND}/chat",
        json=payload,
        timeout=120
    ).json()

    st.session_state.deal_id = response["deal_id"]

    st.session_state.messages.append({
        "role": "assistant",
        "content": response["reply"]
    })

    st.rerun()

# -------------------------
# sidebar
# -------------------------
with st.sidebar:
    st.title("Your Deals")

    # New deal button
    if st.button("➕ New Deal"):
        st.session_state.deal_id = None
        st.session_state.messages = []
        st.rerun()

    if st.session_state.email:
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

                # load messages
                msgs = requests.get(
                    f"{BACKEND}/deals/{deal['deal_id']}/messages",
                    timeout=10
                ).json()

                st.session_state.messages = msgs
                st.rerun()

    