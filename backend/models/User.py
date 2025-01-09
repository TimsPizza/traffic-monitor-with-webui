from pydantic import BaseModel, field_validator, validator
from typing import Optional
from datetime import datetime
import re

class User(BaseModel):
    username: str
    password_hash: str
    created_at: datetime = datetime.now().timestamp()
    last_login: Optional[datetime] = None
    is_active: bool = True

    @field_validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at leas 3 characters')
        return v

    @field_validator('password_hash')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contains uppercase letters')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contains lowercase letters') 
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contains numbers')
        return v
