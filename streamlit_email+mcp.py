import streamlit as st
import yagmail # Make sure yagmail is in your requirements.txt

st.set_page_config(page_title="MCP Email Agent Chatbot", layout="centered")
st.title("🤖 AI Email Assistant")

# ==========================================
# 1. DEFINE YOUR EMAIL SENDING TOOL
# ==========================================
def send_email(recipient: str, subject: str, body: str) -> str:
    """Sends an email using stored secrets credentials."""
    try:
        # You can store your email and app password safely in Streamlit Secrets (.streamlit/secrets.toml)
        sender_email = st.secrets["EMAIL_USER"]
        sender_password = st.secrets["EMAIL_PASSWORD"]
        
        yag = yagmail.SMTP(sender_email, sender_password)
        yag.send(to=recipient, subject=subject, contents=body)
        return f"Successfully sent email to {recipient}!"
    except Exception as e:
        return f"Failed to send email: {str(e)}"

# ==========================================
# 2. STREAMLIT CHAT UI & AGENT HANDLING
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Tell me who to email and what to say..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # 👉 Here is where your LLM/Agent logic goes. 
        # If the user says "I wanna send an email", your agent can extract the details 
        # and trigger the `send_email` function above!
        
        # Temporary handling logic for demonstration:
        response = "I'm ready to send emails! Configure your LLM client and email tool bindings here to start sending."
        
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
