from fastapi import FastAPI, Request, status
from starlette.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from slowapi.errors import RateLimitExceeded
from src.api import contacts, utils, auth, users

app = FastAPI()


# RATE LIMIT
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
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
    return RedirectResponse(url="/docs")


# ROUTERS
app.include_router(utils.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
