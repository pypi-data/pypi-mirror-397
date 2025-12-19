import threading
import time
import uvicorn
from authlib.integrations.starlette_client import OAuth
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from starlette.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware


# Where the server will be hosted.
HOST = "http://localhost"
PORT = 3000


class CognitoLoginServer:
    def __init__(self, client_id, region, user_pool, *, log_level="error"):
        self.process = None
        self.token = None
        self.client_id = client_id
        self.region = region
        self.user_pool = user_pool
        self._thread = None
        self._server = None
        self._log_level = log_level
        
    def run(self):
        self_ = self  # capture self to use in routes.

        app = FastAPI()
        app.add_middleware(SessionMiddleware, secret_key="pycarta-weblogin-secret-key")
        # Serve static assets (e.g., brand logo) from ./static if present
        try:
            app.mount("/static", StaticFiles(directory="static"), name="static")
        except Exception:
            # If the directory is missing, continue without static mount
            pass

        # Setup OAuth
        oauth = OAuth()
        # Cognito Config
        oauth.register(
            name='oidc',
            authority=f"https://cognito-idp.{self.region}.amazonaws.com/{self.user_pool}",
            client_id=self.client_id,
            server_metadata_url=f"https://cognito-idp.{self.region}.amazonaws.com/{self.user_pool}/.well-known/openid-configuration",
            client_kwargs={'scope': 'aws.cognito.signin.user.admin email openid profile'}
        )

        @app.get("/", response_class=HTMLResponse)
        async def index(request: Request):
            self_.token = await oauth.oidc.authorize_access_token(request)
            userinfo = self_.token["userinfo"]
            given, family = userinfo.get("given_name", ""), userinfo.get("family_name", "")
            html = f"""
            <!doctype html>
            <html lang=\"en\">
              <head>
                <meta charset=\"utf-8\" />
                <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
                <title>Logged In</title>
                <style>
                  :root {{
                    --brand-green: rgb(110, 182, 95);
                    --brand-gray: rgb(83, 83, 83);
                    --bg: #f7f7f7;
                    --card-bg: #ffffff;
                  }}
                  html, body {{ height: 100%; margin: 0; background: var(--bg); font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif; color: var(--brand-gray); }}
                  .wrap {{ min-height: 100%; display: flex; align-items: center; justify-content: center; padding: 24px; }}
                  .card {{ background: var(--card-bg); border-radius: 12px; box-shadow: 0 6px 20px rgba(0,0,0,0.08); padding: 28px 28px 24px; max-width: 520px; width: 100%; text-align: center; }}
                  .brand {{ display: inline-flex; align-items: center; gap: 14px; margin-bottom: 14px; }}
                  .brand img {{ width: 56px; height: 56px; }}
                  .brand-name {{ font-weight: 700; letter-spacing: 0.3px; color: var(--brand-gray); }}
                  h1 {{ margin: 8px 0 6px; font-size: 1.4rem; color: var(--brand-gray); }}
                  .success {{ display: inline-flex; align-items: center; gap: 8px; color: var(--brand-green); font-weight: 600; margin-top: 6px; }}
                  .success .dot {{ width: 10px; height: 10px; border-radius: 50%; background: var(--brand-green); display: inline-block; }}
                  p {{ margin: 10px 0 0; line-height: 1.5; }}
                  .hint {{ margin-top: 14px; font-size: 0.95rem; color: var(--brand-gray); opacity: 0.9; }}
                  .footer {{ margin-top: 16px; font-size: 0.8rem; opacity: 0.8; }}
                </style>
              </head>
              <body>
                <div class=\"wrap\">
                  <div class=\"card\">
                    <div class=\"brand\">
                      <img src=\"/static/brand.png\" alt=\"Brand\" onerror=\"this.style.display='none'\" />
                      <span class=\"brand-name\">Signed in to Carta</span>
                    </div>
                    <h1>Welcome{(', ' + given + ' ' + family) if (given or family) else ''}!</h1>
                    <div class=\"success\"><span class=\"dot\"></span> You are now signed in.</div>
                    <p class=\"hint\">You may safely close this window.</p>
                    <div class=\"footer\">If it doesn’t close automatically, you can close it yourself.</div>
                  </div>
                </div>
                <script>
                  // Optional: try to auto-close after a brief delay when embedded as a popup
                  setTimeout(function() {{ try {{ window.close(); }} catch(e) {{}} }}, 5000);
                </script>
              </body>
            </html>
            """
            return HTMLResponse(content=html)

        @app.get("/login")
        async def login(request: Request):
            return await oauth.oidc.authorize_redirect(request, f"{HOST}:{PORT}")
        
        config = uvicorn.Config(app, host="0.0.0.0", port=PORT, log_level=self._log_level)
        self._server = uvicorn.Server(config=config)
        self._server.run()
        # uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="error")

    def __enter__(self):
        self._thread = threading.Thread(target=self.run, daemon=True)
        self._thread.start()
        # Wait for server to start
        while self._server is None or not self._server.started:
            time.sleep(0.1)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._server:
            self._server.should_exit = True
            # self._server.force_exit = True
            self._server = None
        if self._thread:
            self._thread.join(timeout=3)
            self._thread = None
        return exc_val is None
    
    def is_finished(self) -> bool:
        return self.token is not None
