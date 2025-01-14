from db.Client import MongoConnectionSingleton
from models.User import User
from pymongo import MongoClient
from core.config import ENV_CONFIG
from typing import Optional


# User database crud logic here
class UserService:

    _client = MongoConnectionSingleton.get_instance()
    _user_collection = _client.get_database(ENV_CONFIG.database_name).get_collection(
        ENV_CONFIG.user_collection_name
    )

    @classmethod
    async def get_user(self, username: str) -> Optional[User]:
        """get user model by username"""
        user_data = self._user_collection.find_one({"username": username})
        if user_data:
            return User(**user_data)
        return None

    @classmethod
    async def create_user(self, user: User) -> User:
        """create user from model"""
        user_dict = user.model_dump()
        self._user_collection.insert_one(user_dict)
        return user

    @classmethod
    async def update_user(self, username: str, update_data: dict) -> bool:
        """update user data"""
        result = self._user_collection.update_one(
            {"username": username}, {"$set": update_data}
        )
        return result.modified_count > 0

    @classmethod
    async def delete_user(self, username: str) -> bool:
        """rm user from db"""
        result = self._user_collection.delete_one({"username": username})
        return result.deleted_count > 0
