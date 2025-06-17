from fastapi import FastAPI, Request, status
from starlette.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from slowapi.errors import RateLimitExceeded
from src.api import contacts, utils, auth, users

app = FastAPI()


# RATE LIMIT
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Handles exceptions raised when the rate limit is exceeded.

    Args:
        request (Request): The incoming HTTP request.
        exc (RateLimitExceeded): The exception instance for rate limit exceeded.

    Returns:
        JSONResponse: A response with a 429 status code and an error message indicating
        that too many requests have been made.
    """
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"error": "Too many requests. Please try again later"},
    )


# CORS
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# REDIRECT TO DOCS
@app.get("/", include_in_schema=False)
async def root():
    """
    Redirects the root URL to the API documentation.

    Returns:
        RedirectResponse: A response object that redirects to the "/docs" URL.
    """

    return RedirectResponse(url="/docs")


# STATIC PAGE
@app.get("/change_password/{token}", response_class=HTMLResponse)
async def change_password_page(request: Request, token: str):
    """
    Generates a static HTML page for changing a user's password.

    Args:
        request (Request): The incoming HTTP request.
        token (str): The token used to verify the user and change their password.

    Returns:
        HTMLResponse: A response containing the HTML page for changing a user's password.
    """
    templates = Jinja2Templates(directory="src/services/templates")
    context = {"request": request, "host": request.base_url, "token": token}
    return templates.TemplateResponse("change_password.html", context)


# ROUTERS
app.include_router(utils.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
