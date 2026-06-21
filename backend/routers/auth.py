from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext

from backend.database import get_db
from backend.config import settings
from backend.dependencies import get_current_user
import backend.models as models
import backend.schemas as schemas

router = APIRouter()

# ─────────────────────────────────────────
# PASSWORD HASHING SETUP
# ─────────────────────────────────────────
# bcrypt is the industry standard for hashing passwords
# Never store plain text passwords — always hash them
import bcrypt

def hash_password(password: str) -> str:
    """Convert plain password to hashed version"""
    return bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check if entered password matches stored hash"""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )

# ─────────────────────────────────────────
# JWT TOKEN CREATION
# ─────────────────────────────────────────
def create_access_token(data: dict) -> str:
    """Create a JWT token with expiry time"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

# ─────────────────────────────────────────
# REGISTER ROUTE
# ─────────────────────────────────────────
@router.post("/register", response_model=schemas.UserResponse)
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user
    - Checks if email already exists
    - Hashes the password
    - Saves user to database
    """
    # Check if email already registered
    existing_user = db.query(models.User).filter(
        models.User.email == user_data.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user with hashed password
    new_user = models.User(
        full_name=user_data.full_name,
        email=user_data.email,
        hashed_password=hash_password(user_data.password)
    )

    db.add(new_user)      # add to database session
    db.commit()           # save to database
    db.refresh(new_user)  # refresh to get the generated id

    return new_user

# ─────────────────────────────────────────
# LOGIN ROUTE
# ─────────────────────────────────────────
@router.post("/login", response_model=schemas.Token)
def login(user_data: schemas.UserLogin, db: Session = Depends(get_db)):
    """
    Login with email and password
    - Finds user by email
    - Verifies password
    - Returns JWT token
    """
    # Find user by email
    user = db.query(models.User).filter(
        models.User.email == user_data.email
    ).first()

    # Check user exists and password is correct
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Create and return JWT token
    access_token = create_access_token(data={"sub": user.email})

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

# ─────────────────────────────────────────
# GET CURRENT USER ROUTE
# ─────────────────────────────────────────
@router.get("/me", response_model=schemas.UserResponse)
def get_me(current_user = Depends(get_current_user)):
    """Returns the currently logged in user"""
    return current_user