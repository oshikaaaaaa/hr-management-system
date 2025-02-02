# middleware/auth_middleware.py
from fastapi import Request
from fastapi.responses import RedirectResponse
from jose import JWTError, jwt
from utils.auth_utils import SECRET_KEY, ALGORITHM

async def auth_middleware(request: Request, call_next):
    # List of paths that don't require authentication
    public_paths = [
        "/login",
        "/token",
        "/static",
        "/favicon.ico"
    ]
    
    # Check if the path starts with any of the public paths
    if any(request.url.path.startswith(path) for path in public_paths):
        return await call_next(request)

    # Get token from cookie
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/login", status_code=302)
    
    try:
        # Verify token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            return RedirectResponse(url="/login", status_code=302)
    except JWTError:
        return RedirectResponse(url="/login", status_code=302)

    response = await call_next(request)
    return response