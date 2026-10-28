import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import List

app = FastAPI()

# In‑memory store of posted tweets for demonstration
POSTED_TWEETS: List[dict] = []

LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head><title>Login</title></head>
<body>
    <form method=\"post\" action=\"/login\">
        <input id=\"username\" name=\"username\" type=\"text\" placeholder=\"Username\" />
        <input id=\"password\" name=\"password\" type=\"password\" placeholder=\"Password\" />
        <button id=\"login-btn\" type=\"submit\">Login</button>
    </form>
</body>
</html>
"""

COMPOSE_HTML = """
<!DOCTYPE html>
<html>
<head><title>Compose Tweet</title></head>
<body>
    <form method=\"post\" action=\"/api/post_tweet\">
        <textarea id=\"tweet-text\" name=\"tweet\" rows=\"4\" cols=\"50\"></textarea>
        <br/>
        <button id=\"post-btn\" type=\"submit\">Post</button>
    </form>
</body>
</html>
"""

@app.get("/login", response_class=HTMLResponse)
async def get_login():
    return LOGIN_HTML

@app.post("/login")
async def post_login(request: Request):
    # Very simple mock – always succeed and set a cookie
    response = JSONResponse({"status": "ok"})
    response.set_cookie(key="session", value="mock-session", httponly=True)
    return response

@app.get("/compose/tweet", response_class=HTMLResponse)
async def get_compose():
    return COMPOSE_HTML

@app.post("/api/post_tweet")
async def post_tweet(request: Request):
    data = await request.form()
    tweet = data.get("tweet", "")
    POSTED_TWEETS.append({"tweet": tweet, "id": len(POSTED_TWEETS) + 1})
    return {"status": "posted", "tweet": tweet}

@app.post("/api/internal/reset")
async def reset():
    POSTED_TWEETS.clear()
    return {"status": "reset"}
