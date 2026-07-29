from backend.database import SessionLocal
from backend.models import User


db = SessionLocal()

try:
    user = db.query(User).filter(
        User.email == "prasad@test.com"
    ).first()

    if user is None:
        print("User not found")
    else:
        user.is_admin = True
        db.commit()
        db.refresh(user)

        print("Admin created:")
        print(user.email)
        print(user.is_admin)

finally:
    db.close()