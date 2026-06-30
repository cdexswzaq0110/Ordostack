from fastapi import APIRouter, Depends, Request, status

from app.dependencies import get_current_user
from app.schemas.auth import AuthToken, UserCreate, UserLogin, UserRead
from app.services import auth as auth_service

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=AuthToken, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate) -> AuthToken:
    return auth_service.register_user(payload)


@router.post("/login", response_model=AuthToken)
def login(payload: UserLogin, request: Request) -> AuthToken:
    client_identifier = request.client.host if request.client is not None else "unknown"
    return auth_service.login_user(payload, client_identifier=client_identifier)


@router.get("/me", response_model=UserRead)
def me(current_user: UserRead = Depends(get_current_user)) -> UserRead:
    return current_user
