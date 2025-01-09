from models.User import User
from pymongo import MongoClient
from core.config import ENV_CONFIG
from typing import Optional

# User database crud logic here
class UserDB:
    def __init__(self):
        self.client = MongoClient(ENV_CONFIG.database_uri)
        self.db = self.client["traffic_monitor"]
        self.collection = self.db["users"]

    async def get_user(self, username: str) -> Optional[User]:
        """get user model by username"""
        user_data = self.collection.find_one({"username": username})
        if user_data:
            return User(**user_data)
        return None

    async def create_user(self, user: User) -> User:
        """create user from model"""
        user_dict = user.model_dump()
        self.collection.insert_one(user_dict)
        return user

    async def update_user(self, username: str, update_data: dict) -> bool:
        """update user data"""
        result = self.collection.update_one(
            {"username": username},
            {"$set": update_data}
        )
        return result.modified_count > 0

    async def delete_user(self, username: str) -> bool:
        """rm user from db"""
        result = self.collection.delete_one({"username": username})
        return result.deleted_count > 0
