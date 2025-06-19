import logging

from fastapi import (
    APIRouter,
    status,
    BackgroundTasks,
    Request,
    Depends,
    HTTPException,
    Form,
)
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.users import (
    UserResponse,
    UserCreate,
    TokenModel,
    RequestEmail,
)
from src.database.db import get_db
from src.services.users import UserService
from src.services.auth import auth_service
from src.services.email import send_email

router = APIRouter(prefix="/auth", tags=["Auth"])
logger = logging.getLogger()


@router.post(
    "/signup/", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def signup(
    user: UserCreate,
    background_task: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new user with the given email and password, and send a confirmation email
    to the given email address.

    Args:
        user (UserCreate): The user data to create the new user.
        background_task (BackgroundTasks): To run the email sending task in the background.
        request (Request): To get the request base url.

    Raises:
        HTTPException: If the email or username already exist in the database.

    Returns:
        UserResponse: The newly created user.
    """
    user_service = UserService(db)
    email_user = await user_service.get_user_by_email(user.email)

    if email_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exist",
        )
    name_user = await user_service.get_user_by_name(user.username)

    if name_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this name already exist",
        )

    user.password = auth_service.get_password_hash(user.password)
    new_user = await user_service.create_user(user)
    background_task.add_task(
        send_email, new_user.email, new_user.username, str(request.base_url)
    )
    return new_user


@router.post("/login", response_model=TokenModel)
async def login(
    body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    """
    Login with username and password.

    Args:
        body (OAuth2PasswordRequestForm): The user credentials.

    Raises:
        HTTPException: If the user is not found, the password is wrong or the email is not confirmed.

    Returns:
        TokenModel: The access token and token type.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_name(body.username)
    if user is None or not auth_service.verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid login or password",
        )
    if not user.confirmed_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed"
        )

    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    """
    Confirm the email of a user with the given token.

    Args:
        token (str): The token to confirm the email.

    Raises:
        HTTPException: If the user is not found or the email is already confirmed.

    Returns:
        dict: A message indicating that the email has been confirmed.
    """

    user_service = UserService(db)
    email = auth_service.get_email_from_token(token)
    user = await user_service.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Your email is already confirmed",
        )
    await user_service.confirmed_email(email)
    return {"message": "Email confirmed"}


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_task: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Handles email confirmation requests. If the user's email is already confirmed,
    it returns a message indicating so. If not, it schedules a task to send a
    confirmation email to the user.

    Args:
        body (RequestEmail): Contains the email address to request confirmation for.
        background_task (BackgroundTasks): Used to run the email sending task in the background.
        request (Request): Provides access to the request's base URL.
        db (AsyncSession): Database session dependency.

    Returns:
        dict: A message indicating the email confirmation status.
    """

    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)
    if user:
        if user.confirmed_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Your email is already confirmed",
            )
        background_task.add_task(
            send_email, user.email, user.username, str(request.base_url)
        )
    return {"message": "Check your email for confirmation"}


@router.post("/forgot_password")
async def forgot_password(
    body: RequestEmail,
    background_task: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Handles password reset requests. If the user's email is not confirmed, it raises an
    HTTPException. If the user's email is confirmed, it schedules a task to send an email
    containing a link to reset the password.

    Args:
        body (RequestEmail): Contains the email address to request a password reset for.
        background_task (BackgroundTasks): Used to run the email sending task in the background.
        request (Request): Provides access to the request's base URL.
        db (AsyncSession): Database session dependency.

    Returns:
        dict: A message indicating that an email has been sent to reset the password.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if not user.confirmed_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed"
        )
    background_task.add_task(
        send_email, user.email, user.username, str(request.base_url), True
    )
    return {"message": "Check your email for confirmation"}


@router.get("/reset_password/{token}")
async def reset_password(token: str):
    """
    Redirects the user to the password change page using the provided token.

    Args:
        token (str): The token used to verify and allow the user to change their password.

    Returns:
        RedirectResponse: A response object that redirects to the password change page.
    """

    RedirectResponse(url=f"/change_password/{token}")


@router.post("/reset_password/{token}")
async def post_reset_password(
    token: str, password: str = Form(...), db: AsyncSession = Depends(get_db)
):
    """
    Handles password reset requests. If the user's email is not confirmed, it raises an
    HTTPException. If the user's email is confirmed, it updates the user's password with the
    provided password.

    Args:
        token (str): The token used to verify and allow the user to change their password.
        password (str): The new password to set for the user.
        db (AsyncSession): Database session dependency.

    Returns:
        dict: A message indicating that the password has been successfully changed.
    """
    user_service = UserService(db)
    email = auth_service.get_email_from_token(token)
    user = await user_service.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if not user.confirmed_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed"
        )
    hashed_password = auth_service.get_password_hash(password)
    await user_service.reset_password(hashed_password, email)
    return {"message": "Password successfully changed"}
