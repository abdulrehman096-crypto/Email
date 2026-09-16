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
        return f"Failed to initialize email client. Error: {str(e)}"

# Available tools list for the sidebar
AVAILABLE_TOOLS = ['add', 'greet', 'send_lead_to_crm', 'send_email', 'send_multiple_emails']

# ==========================================
# SIDEBAR: Connected Tools Status Box
# ==========================================
with st.sidebar:
    st.success(f"Connected to MCP Server!\n\nTools available: {AVAILABLE_TOOLS}")
    st.markdown("---")
    st.markdown("### Quick Guide")
    st.markdown("Type **'send an email'** to start a single email flow, or provide comma-separated addresses for bulk outreach.")

# ==========================================
# MAIN CHAT INTERFACE
# ==========================================
st.title("🤖 MCP Agent Chatbot with Streamlit")

# Initialize chat history state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize email flow state variables if they don't exist
if "email_flow_active" not in st.session_state:
    st.session_state.email_flow_active = False
    st.session_state.email_step = 0  # 0: idle, 1: waiting for subject, 2: waiting for body
    st.session_state.temp_recipients = []
    st.session_state.temp_subject = ""

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
        query_lower = prompt.lower()
        
        # Check if user wants to start an email flow
        if not st.session_state.email_flow_active and ("email" in query_lower or "send" in query_lower):
            st.session_state.email_flow_active = True
            st.session_state.email_step = 1
            response = """Sure! I can help with that. Could you please provide the recipient's email address(es)? 
*(You can provide a single email or separate multiple emails with commas for bulk sending).*"""

        # Step 1: Handling recipients
        elif st.session_state.email_flow_active and st.session_state.email_step == 1:
            # Parse recipients (split by comma if multiple)
            raw_recipients = [e.strip() for e in prompt.split(",") if "@" in e]
            if not raw_recipients:
                # Fallback if no '@' found, treat whole prompt as single email
                raw_recipients = [prompt.strip()]
            
            st.session_state.temp_recipients = raw_recipients
            st.session_state.email_step = 2
            
            if len(raw_recipients) > 1:
                response = f"Got it—we have **{len(raw_recipients)} recipients** queued up (`{', '.join(raw_recipients)}`).\n\nCould you also let me know the **Subject** of the email?"
            else:
                response = f"Got it—the recipient is `{raw_recipients[0]}`.\n\nCould you also let me know the **Subject** of the email?"

        # Step 2: Handling subject
        elif st.session_state.email_flow_active and st.session_state.email_step == 2:
            st.session_state.temp_subject = prompt.strip()
            st.session_state.email_step = 3
            response = f"Thanks for the subject line **\"{st.session_state.temp_subject}\"**. What would you like the email's **body** to say?"

        # Step 3: Handling body and executing email send
        elif st.session_state.email_flow_active and st.session_state.email_step == 3:
            body_text = prompt.strip()
            recipients = st.session_state.temp_recipients
            subject = st.session_state.temp_subject
            
            # Execute email transmission (single or multiple)
            if len(recipients) > 1:
                send_result = send_multiple_emails(recipients, subject, body_text)
            else:
                try:
                    sender_email = st.secrets["EMAIL_USER"]
                    sender_password = st.secrets["EMAIL_PASSWORD"]
                    yag = yagmail.SMTP(sender_email, sender_password)
                    yag.send(to=recipients[0], subject=subject, contents=body_text)
                    send_result = f"✅ Sent successfully to {recipients[0]}"
                except Exception as e:
                    send_result = f"❌ Failed to send: {str(e)}"
            
            # Reset flow state
            st.session_state.email_flow_active = False
            st.session_state.email_step = 0
            
            response = f"""The email transmission has finished:
{send_result}

* **Recipients:** {', '.join(recipients)}
* **Subject:** {subject}
* **Body:** {body_text}

Let me know if there's anything else you'd like to do!"""

        else:
            response = f"Received your command: '{prompt}'. Let me know if you want to send emails or run tools!"

        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
