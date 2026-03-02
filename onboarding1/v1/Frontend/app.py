# # import streamlit as st
# # import requests
# # import uuid

# # st.set_page_config(page_title="ITTIKAR DEAL ONBOARDING", layout="centered")

# # if "session_id" not in st.session_state:
# #     st.session_state.session_id = str(uuid.uuid4())
    
# # if "messages" not in st.session_state:
# #     st.session_state.messages = []
    
# # st.title("ITTIKAR DEAL ONBOARDING AGENT")

# # for msg in st.session_state.messages:
# #     with st.chat_message(msg['role']):
# #         st.write(msg['content'])
        
# # if user_input :=  st.chat_input("Welcome to ITIKKAR Deal Onboarding! How can I assist you today?"):
# #         st.session_state.messages.append({
# #             'role':'user',
# #             'content':user_input
# #         })
        
# #         response = requests.post(
# #             "http://localhost:8000/chat",
# #             json={
# #                 "session_id": st.session_state.session_id,
# #                 "message": user_input
# #             }
# #         )
# #         response_data = response.json()
# #         st.session_state.messages.append({
# #             'role':'assistant',
# #             'content':response_data['reply']
# #         })

# import streamlit as st
# import requests
# import uuid

# BACKEND = "http://localhost:8000"

# st.set_page_config(page_title="ITIKKAR DEAL ONBOARDING", layout="wide")
# st.title("ITIKKAR DEAL ONBOARDING AGENT")

# if "is_streaming" not in st.session_state:
#     st.session_state.is_streaming = False

# #------------------------------------
# #user email input
# #------------------------------------
# if 'email' not in st.session_state:
#     st.session_state.email = ''
# if not st.session_state.email:
#     st.session_state.email = st.text_input(
#         "Please enter your email to start:",
#         placeholder="your@company.com"
#         )
#     st.stop()
# email = st.session_state.email.lower().strip()

# #------------------------------------
# #sidebar chats
# #------------------------------------
# st.sidebar.title('your Deals')

# #load_user_chats from backend
# chat_list_resp = requests.get(
#     f"{BACKEND}/user_chats",
#     params={"email":email}
# )
# chat_ids = chat_list_resp.json().get("chats", [])

# if "active_chat_id" not in st.session_state:
#     st.session_state.active_chat_id = None
    
# # if st.sidebar.button("➕ New Deal"):
# #     st.session_state.active_chat_id = None
# #     st.session_state.messages = []
# if not st.session_state.is_streaming:
#     if st.sidebar.button("➕ New Deal"):
#         st.session_state.active_chat_id = None
#         st.session_state.messages = []


# # for chat_id in chat_ids:
# #     if st.sidebar.button(f"📄 Deal {chat_id[:8]}"):
# #         st.session_state.active_chat_id = chat_id
# # Chat selector
# for chat_id in chat_ids:
#     chat_state = requests.get(
#         f"{BACKEND}/chat_state",
#         params={"chat_id": chat_id}
#     ).json()

#     label = chat_state.get("deal_title") or f"Deal {chat_id[:8]}"

#     if st.sidebar.button(f"📄 {label}",
#                          key = f"chat_button_{chat_id}"):
#         st.session_state.active_chat_id = chat_id
# #------------------------------------
# #load active chat state
# #------------------------------------

# if st.session_state.active_chat_id:
#     chat_state = requests.get(
#         f"{BACKEND}/chat_state",
#         params={"chat_id":st.session_state.active_chat_id}
#     ).json()
#     st.session_state.messages = chat_state.get("messages", [])
    
#     deal_title = chat_state.get("deal_title")
#     # if deal_title:
#     #     st.success(f"✅ Deal Title Generated: {deal_title}")
#     # else:
#     #     st.info("ℹ️ Deal Title: Not generated yet (send 4+ messages to generate)")
# else:
#     st.session_state.messages = []
    
# #------------------------------------
# #render chat
# #------------------------------------

# for msg in st.session_state.messages:
#     with st.chat_message(msg['role']):
#         st.write(msg['content'])
        
# #------------------------------------
# #chat input
# #------------------------------------

# user_input = st.chat_input('Enter your message here...')
# if user_input:
#     st.session_state.is_streaming = True
#     st.session_state.messages.append({
#         'role':'user',
#         'content':user_input
#     })
#     with st.chat_message('user'):
#         st.write(user_input)
        
#     assistant_placeholder = st.empty()
    
#     with assistant_placeholder.container():
#         with st.chat_message('assistant'):
#             st.write("Typing...")
            
#     payload = {
#         "email": email,
#         "chat_id": st.session_state.active_chat_id,
#         "message": user_input
#     }
#     # response = requests.post(
#     #     f"{BACKEND}/chat",
#     #     json = payload,
#     #     timeout = 60
#     # ).json()
    
#     # reply = response['reply']
        
#     # st.session_state.active_chat_id = response['chat_id']
    
#     # assistant_placeholder.empty()
#     # with st.chat_message('assistant'):
#     #     st.write(reply)
        
#     # st.session_state.messages.append({
#     #     'role':'assistant',
#     #     'content':reply
#     # })
#     assistant_text = ""

#     with requests.post(
#         f"{BACKEND}/chat/stream",
#         json=payload,
#         stream=True,
#         timeout=300
#     ) as response:
#         response.raise_for_status()

#         with st.chat_message("assistant"):
#             placeholder = st.empty()

#             for chunk in response.iter_content(chunk_size=None):
#                 if chunk:
#                     token = chunk.decode("utf-8")
#                     assistant_text += token
#                     placeholder.markdown(assistant_text)

#     # save assistant message locally
#     st.session_state.messages.append({
#         "role": "assistant",
#         "content": assistant_text
#     })
    
#     st.session_state.is_streaming = False
#     st.rerun()
#     # 
#     # chat_state = requests.get(
#     #     f"{BACKEND}/chat_state",
#     #     params={"chat_id":st.session_state.active_chat_id}
#     # ).json()
#     # st.session_state.messages = chat_state.get("messages", [])
#     # st.rerun()

#-----------------------------------------------------------------------------
# import streamlit as st
# import requests
# import uuid

# BACKEND = "http://localhost:8000"

# # ------------------------------
# # Page config
# # ------------------------------
# st.set_page_config(page_title="ITIKKAR DEAL ONBOARDING", layout="wide")
# st.title("ITIKKAR DEAL ONBOARDING AGENT")

# # ------------------------------
# # Session state initialization
# # ------------------------------
# if "email" not in st.session_state:
#     st.session_state.email = ""

# if "messages" not in st.session_state:
#     st.session_state.messages = []

# if "active_chat_id" not in st.session_state:
#     st.session_state.active_chat_id = None

# if "is_streaming" not in st.session_state:
#     st.session_state.is_streaming = False

# # ------------------------------
# # Email gate
# # ------------------------------
# if not st.session_state.email:
#     st.session_state.email = st.text_input(
#         "Please enter your email to start:",
#         placeholder="your@company.com"
#     )
#     st.stop()

# email = st.session_state.email.lower().strip()

# # ------------------------------
# # Sidebar – deals list
# # ------------------------------
# st.sidebar.title("Your Deals")

# # Load user chats
# try:
#     chat_list_resp = requests.get(
#         f"{BACKEND}/user_chats",
#         params={"email": email},
#         timeout=10
#     )
#     chat_ids = chat_list_resp.json().get("chats", [])
# except Exception:
#     chat_ids = []

# # New Deal button (DISABLED while streaming)
# if not st.session_state.is_streaming:
#     if st.sidebar.button("➕ New Deal"):
#         st.session_state.active_chat_id = None
#         st.session_state.messages = []
#         st.rerun()

# # Existing deals
# for chat_id in chat_ids:
#     try:
#         chat_state = requests.get(
#             f"{BACKEND}/chat_state",
#             params={"chat_id": chat_id},
#             timeout=10
#         ).json()
#         label = chat_state.get("deal_title") or f"Deal {chat_id[:8]}"
#     except Exception:
#         label = f"Deal {chat_id[:8]}"

#     if st.sidebar.button(f"📄 {label}", key=f"chat_{chat_id}"):
#         st.session_state.active_chat_id = chat_id
#         st.session_state.messages = chat_state.get("messages", [])
#         st.rerun()

# # ------------------------------
# # Render chat history
# # ------------------------------
# for msg in st.session_state.messages:
#     with st.chat_message(msg["role"]):
#         st.write(msg["content"])

# # ------------------------------
# # Chat input
# # ------------------------------
# user_input = st.chat_input("Enter your message here...")

# if user_input and not st.session_state.is_streaming:
#     # Lock UI
#     st.session_state.is_streaming = True

#     # Append user message
#     st.session_state.messages.append({
#         "role": "user",
#         "content": user_input
#     })

#     with st.chat_message("user"):
#         st.write(user_input)

#     # Prepare request
#     payload = {
#         "email": email,
#         "chat_id": st.session_state.active_chat_id,
#         "message": user_input
#     }

#     assistant_text = ""

#     # Stream assistant response
#     with requests.post(
#         f"{BACKEND}/chat/stream",
#         json=payload,
#         stream=True,
#         timeout=300
#     ) as response:
#         response.raise_for_status()

#         with st.chat_message("assistant"):
#             placeholder = st.empty()
#             for chunk in response.iter_content(chunk_size=None):
#                 if chunk:
#                     token = chunk.decode("utf-8")
#                     assistant_text += token
#                     placeholder.markdown(assistant_text)

#     # Persist assistant message LOCALLY
#     st.session_state.messages.append({
#         "role": "assistant",
#         "content": assistant_text
#     })
    
#     chat_id_from_backend = response.headers.get("X-Chat-Id")

#     if not st.session_state.active_chat_id and chat_id_from_backend:
#         st.session_state.active_chat_id = chat_id_from_backend


#     # Unlock UI
#     st.session_state.is_streaming = False

#     # Rerun safely
#     st.rerun()
#---------------------------------------------------------------------------
import streamlit as st
import requests
import uuid

BACKEND = "http://localhost:8000"

st.set_page_config(
    page_title="ITIKKAR Deal Onboarding",
    layout="wide"
)

st.title("ITIKKAR Deal Onboarding Agent")

# -----------------------------
# User Identity (Email)
# -----------------------------

if "email" not in st.session_state:
    st.session_state.email = ""

if not st.session_state.email:
    st.session_state.email = st.text_input(
        "Enter your email to continue",
        placeholder="you@company.com"
    )
    st.stop()

email = st.session_state.email.lower().strip()

# -----------------------------
# Sidebar – Deal Sessions
# -----------------------------

st.sidebar.title("Your Deals")

resp = requests.get(
    f"{BACKEND}/user_chats",
    params={"email": email}
)
chat_ids = resp.json().get("chats", [])

if "active_chat_id" not in st.session_state:
    st.session_state.active_chat_id = None

if st.sidebar.button("➕ New Deal"):
    st.session_state.active_chat_id = None
    st.session_state.messages = []

for chat_id in chat_ids:
    chat_state = requests.get(
        f"{BACKEND}/chat_state",
        params={"chat_id": chat_id}
    ).json()

    label = chat_state.get("deal_title") or f"Draft Deal {chat_id[:4]}"
    if st.sidebar.button(f"📄 {label}"):
        st.session_state.active_chat_id = chat_id

# -----------------------------
# Load Active Chat
# -----------------------------

if st.session_state.active_chat_id:
    state = requests.get(
        f"{BACKEND}/chat_state",
        params={"chat_id": st.session_state.active_chat_id}
    ).json()
    st.session_state.messages = state.get("messages", [])
else:
    st.session_state.messages = []

# -----------------------------
# Render Chat
# -----------------------------

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# -----------------------------
# Chat Input
# -----------------------------

user_input = st.chat_input("Type your message...")

if user_input:
    # Show user message immediately
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.write(user_input)

    assistant_placeholder = st.empty()
    with assistant_placeholder.container():
        with st.chat_message("assistant"):
            st.write("⏳ Thinking...")

    payload = {
        "email": email,
        "chat_id": st.session_state.active_chat_id,
        "message": user_input
    }

    response = requests.post(
        f"{BACKEND}/chat",
        json=payload,
        timeout=60
    ).json()

    st.session_state.active_chat_id = response["chat_id"]
    reply = response["reply"]

    assistant_placeholder.empty()
    with st.chat_message("assistant"):
        st.write(reply)

    st.session_state.messages.append({
        "role": "assistant",
        "content": reply
    })

