import yagmail
import streamlit as st

def send_multiple_emails(recipient_list, subject, body):
    """Sends the same email to multiple recipients in a loop."""
    results = []
    try:
        sender_email = st.secrets["EMAIL_USER"]
        sender_password = st.secrets["EMAIL_PASSWORD"]
        
        # Initialize yagmail client once
        yag = yagmail.SMTP(sender_email, sender_password)
        
        for email in recipient_list:
            try:
                yag.send(to=email.strip(), subject=subject, contents=body)
                results.append(f"✅ Sent to {email}")
            except Exception as e:
                results.append(f"❌ Failed for {email}: {str(e)}")
                
        return "\n".join(results)
    except Exception as e:
        return f"Failed to initialize email client: {str(e)}"
