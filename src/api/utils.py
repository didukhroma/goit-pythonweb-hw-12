from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.database.db import get_db

router = APIRouter(tags=["Utils"])


@router.get("/healtchchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    """
    Health check endpoint to verify database connectivity.

    Args:
        db (AsyncSession): The database session dependency.

    Raises:
        HTTPException: If there is an error connecting to the database or if the
        database is not configured correctly.

    Returns:
        dict: A message indicating the API is functioning correctly.
    """

    try:
        result = await db.execute(text("SELECT 1"))
        result = result.scalar_one_or_none()

        if result is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database is not configured correctly",
            )
        return {"message": "Welcome to FastAPI"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error connecting to database",
        )
