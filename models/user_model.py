from bson.objectid import ObjectId
from datetime import datetime
from typing import Optional, Dict
import pytz
from bson.codec_options import CodecOptions
from werkzeug.security import generate_password_hash, check_password_hash

# Timezone for Asia/Kolkata
IST = pytz.timezone("Asia/Kolkata")

class UserModel:
    def __init__(self, mongo):
        # Timezone-aware users collection
        self.users = mongo.db.users.with_options(
            codec_options=CodecOptions(tz_aware=True, tzinfo=IST)
        )

    def _localize_datetime(self, dt):
        if dt.tzinfo is None:
            return IST.localize(dt)
        return dt.astimezone(IST)

    def create_user(self, username: str, email: str, password: str) -> None:
        """Creates a new user with hashed password and timestamp."""
        created_at = self._localize_datetime(datetime.now())
        hashed_password = generate_password_hash(password)
        self.users.insert_one({
            "username": username,
            "email": email,
            "password": hashed_password,
            "created_at": created_at
        })

    def find_by_username(self, username: str) -> Optional[Dict]:
        """Finds a user by username."""
        return self.users.find_one({"username": username})

    def find_by_email(self, email: str) -> Optional[Dict]:
        """Finds a user by email."""
        return self.users.find_one({"email": email})

    def find_by_identifier(self, identifier: str) -> Optional[Dict]:
        """Finds a user by username or email."""
        if "@" in identifier:
            return self.find_by_email(identifier)
        return self.find_by_username(identifier)

    def verify_user(self, identifier: str, password: str) -> bool:
        """Verifies user credentials."""
        user = self.find_by_identifier(identifier)
        if user and check_password_hash(user["password"], password):
            return True
        return False

    def get_email_by_username(self, username: str) -> Optional[str]:
        """Gets email address for a given username."""
        user = self.find_by_username(username)
        return user.get("email") if user else None

    def update_user_email(self, user_id: str, new_email: str) -> None:
        """Updates a user's email by user ID."""
        self.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"email": new_email}}
        )

    def delete_user(self, user_id: str) -> None:
        """Deletes a user by ID."""
        self.users.delete_one({"_id": ObjectId(user_id)})
