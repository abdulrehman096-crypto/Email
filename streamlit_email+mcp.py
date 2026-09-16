import streamlit as st
import yagmail

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="MCP Agent Chatbot with Streamlit",
    page_icon="🤖",
    layout="wide"
)

# ==========================================
# TOOL DEFINITIONS (In-Memory MCP Tools)
# ==========================================
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b

def greet(name: str) -> str:
    """Greet a user by name."""
    return f"Hello, {name}!"

def send_lead_to_crm(lead_name: str, email: str) -> str:
    """Simulate sending a lead to a CRM database."""
    return f"Successfully added lead {lead_name} ({email}) to CRM!"

def send_multiple_emails(recipient_list: list, subject: str, body: str) -> str:
    """Sends the same email to multiple recipients in a loop using Streamlit Secrets."""
    results = []
    try:
        # Pull credentials safely from Streamlit Cloud Secrets dashboard
        sender_email = st.secrets["EMAIL_USER"]
        sender_password = st.secrets["EMAIL_PASSWORD"]
        
        yag = yagmail.SMTP(sender_email, sender_password)
        
        for email in recipient_list:
            clean_email = email.strip()
            try:
                yag.send(to=clean_email, subject=subject, contents=body)
                results.append(f"✅ Sent to {clean_email}")
            except Exception as e:
                results.append(f"❌ Failed for {clean_email}: {str(e)}")
                
        return "\n".join(results)
    except Exception as e:
        return f"Failed to initialize email client. Check your Streamlit Secrets. Error: {str(e)}"

# Define available tools for the sidebar status box
AVAILABLE_TOOLS = ['add', 'greet', 'send_lead_to_crm', 'send_email', 'send_multiple_emails']

# ==========================================
# SIDEBAR: Connected Tools Status Box
# ==========================================
with st.sidebar:
    st.success(f"Connected to MCP Server!\n\nTools available: {AVAILABLE_TOOLS}")
    st.markdown("---")
    st.markdown("### Quick Guide")
    st.markdown("Type a message to test single or bulk email dispatch, lead management, or simple math tools.")

# ==========================================
# MAIN CHAT INTERFACE
# ==========================================
st.title("🤖 MCP Agent Chatbot with Streamlit")

# Initialize chat history state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Render prior chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Capture user input
if prompt := st.chat_input("Ask me to send emails, add leads, or do math..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Process intent based on prompt keywords
        query_lower = prompt.lower()
        
        if "email" in query_lower or "send" in query_lower:
            response = """I am ready to send emails for your outreach! 
To proceed, please provide:
1. **Recipient email(s)** (separated by commas if multiple)
2. **Subject line**
3. **Body of the message**"""
        elif "lead" in query_lower or "crm" in query_lower:
            response = "I can manage your leads. Provide the lead's name and email address to store them in the CRM."
        else:
            response = f"Received your command: '{prompt}' via the local MCP tool execution layer."

        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
