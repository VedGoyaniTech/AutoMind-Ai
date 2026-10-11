import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError, OperationalError
from app.db.session import get_db
from app.schemas.user import (
    UserCreate, UserLogin, UserResponse, Token, 
    RegisterResponse, UserPreferenceUpdate, UserPreferenceResponse
)
from app.repositories.user_repo import UserRepository
from app.core.security import verify_password, get_password_hash, create_access_token, decode_access_token
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Authenticate the current user via JWT bearer token.
    Strictly enforces 401 Unauthorized for missing, malformed, expired,
    unmatched, or inactive user tokens with zero fallback to demo accounts.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is missing.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    clean_token = token.replace("Bearer ", "").strip()
    if not clean_token or clean_token.lower() in ["null", "undefined"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is missing or empty.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(clean_token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Validate subject safely — non-integer or malformed subjects must return 401, not 500
    sub = payload.get("sub")
    try:
        user_id = int(sub)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed token subject identifier.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="User account not found.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive or deactivated.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user

@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    if user_in.confirm_password and user_in.password != user_in.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match.")

    normalized_email = user_in.email.strip().lower()
    full_name = user_in.full_name.strip()

    repo = UserRepository(db)

    try:
        existing = repo.get_by_email(normalized_email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An account with this email address already exists."
            )

        user = repo.create(
            full_name=full_name,
            email=normalized_email,
            password=user_in.password
        )
        access_token = create_access_token(user.id)
        user_resp = UserResponse.model_validate(user)

        return RegisterResponse(
            success=True,
            message="Account created successfully.",
            access_token=access_token,
            token_type="Bearer",
            user=user_resp
        )
    except HTTPException:
        raise
    except IntegrityError as ie:
        db.rollback()
        logger.warning(f"Registration integrity conflict for '{normalized_email}': {ie}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )
    except (OperationalError, SQLAlchemyError) as se:
        db.rollback()
        logger.error(f"Database error during registration for '{normalized_email}': {se}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service is temporarily unavailable. Please try again."
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error during registration for '{normalized_email}': {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to complete registration. Please try again."
        )


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Authenticate registered user credentials. No hardcoded or auto-seeded accounts."""
    repo = UserRepository(db)
    normalized_email = credentials.email.strip().lower()
    user = repo.get_by_email(normalized_email)
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive or deactivated.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(user.id)
    user_resp = UserResponse.model_validate(user)

    return Token(
        access_token=access_token,
        token_type="Bearer",
        user=user_resp
    )

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/preferences", response_model=UserPreferenceResponse)
def update_preferences(
    pref_in: UserPreferenceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    repo = UserRepository(db)
    updated = repo.update_preference(
        user_id=current_user.id,
        answer_detail=pref_in.answer_detail or "Balanced",
        units=pref_in.units or "Metric",
        currency=pref_in.currency or "INR"
    )
    return updated
