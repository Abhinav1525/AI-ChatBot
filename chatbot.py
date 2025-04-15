import streamlit as st
from openai import OpenAI
from serpapi import GoogleSearch

# ----------- Streamlit Title -------------
st.title("Talk AI! 🤖🗣️")

# ----------- Session State for Chat History -------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ----------- Display Chat History -------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ----------- OpenAI Client for Ollama -------------
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="random-text"  # Ollama doesn't check this, required by the SDK
)

# ----------- SerpAPI Web Search Function -------------
def search_web(query):
    params = {
        "engine": "google",
        "q": query,
        "api_key": "d41731d398593c552aaa5d82b0b198002b3fd7d4ef78614ddcf7d9c3324dd4a7", 
        "num": 3,
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    snippets = [r["snippet"] for r in results.get("organic_results", []) if "snippet" in r]
    return "\n".join(snippets)

# ----------- Chat Input from User -------------
prompt = st.chat_input("What's up?")

if prompt:
    # Show user message
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 🔍 Check if web context is needed
    web_context = ""
    if any(word in prompt.lower() for word in ["news", "today", "2025", "latest", "happening", "update"]):
        web_result = search_web(prompt)
        if web_result:
            web_context = f"The following information was retrieved from the web:\n{web_result}\n"

    # Build message history + optional web context
    full_messages = [{"role": message["role"], "content": message["content"]}
                     for message in st.session_state.messages]

    if web_context:
        full_messages.insert(0, {"role": "system", "content": web_context})

    # Generate and stream response from Ollama
    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model="mistral", 
            messages=full_messages,
            stream=True
        )
        response = st.write_stream(stream)

    # Save assistant response
    st.session_state.messages.append({"role": "assistant", "content": response})
