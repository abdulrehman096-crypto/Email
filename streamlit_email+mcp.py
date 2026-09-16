import streamlit as st

# Import your tools or FastMCP functions directly from your ai_mcp.py file
# (Make sure ai_mcp.py is in the same GitHub repository folder as app.py)
try:
    import ai_mcp
    # Assuming ai_mcp exposes a list or registry of tools, or we list them manually:
    AVAILABLE_TOOLS = ['add', 'greet', 'send_lead_to_crm', 'send_email']
    server_connected = True
except Exception as e:
    AVAILABLE_TOOLS = []
    server_connected = False

st.set_page_config(page_title="MCP Agent Chatbot with Streamlit", layout="wide")

# ==========================================
# SIDEBAR: Connected Tools Status Box
# ==========================================
with st.sidebar:
    if server_connected:
        st.success(f"Connected to MCP Server! Tools available: {AVAILABLE_TOOLS}")
    else:
        st.error("Could not load local MCP tools.")

# ==========================================
# MAIN CHAT INTERFACE
# ==========================================
st.title("🤖 MCP Agent Chatbot with Streamlit")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input handling
if prompt := st.chat_input("Ask me to send an email or do math..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Multi-turn logic simulation or LLM/Agent tool execution
        if "email" in prompt.lower():
            response = """Sure! I can help with that. Could you please provide the following details for the email?
1. **Recipient's email address** (the "to" field)
2. **Subject line**
3. **Body of the message**

Once I have that information, I'll send the email for you."""
        else:
            response = f"Processed your request using local tools!"

        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
