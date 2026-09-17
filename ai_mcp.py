from fastmcp import FastMCP

mcp = FastMCP("My MATH MCP Server")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Return sum."""
    return a + b

@mcp.tool()
def greet(name: str) -> str:
    """Return greeting."""
    return f"Hello, {name}!"

@mcp.tool()
def send_lead_to_crm(name: str, email: str) -> str:
    """Send lead to CRM."""
    return f"Lead for {name} with email {email} sent to CRM!"

@mcp.tool()
def send_email(to: str, subject: str, body: str) -> str:
    """Send a email."""
    
    import yagmail
    yag = yagmail.SMTP("kingabdulrehman096@gmail.com", "phay igui vrwy novy")
    
    yag.send(
        "abdulrehmannaveed096@gmail.com",
        subject="Python Email Test",
        contents="This is a test email sent from Python using yagmail."
    )
    print("Email sent successfully!")

    return f"Email sent to {to} with subject '{subject}' and body '{body}'!"

if __name__ == "__main__":
    mcp.run(transport="http", port=8000)