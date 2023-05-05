from pydantic import BaseModel, EmailStr
import datetime


class UserBase(BaseModel):
    email: EmailStr


class UserLogin(UserBase):
    password: str
    remember: bool = True

    @property
    def expires_time(cls):
        if not cls.remember:
            return datetime.timedelta(days=1)
        return False


class UserSignup(UserBase):
    first_name: str
    last_name: str
    password: str


class UserResponse(UserBase):
    id: str
    first_name: str
    last_name: str
    verified: bool = True
    created_at: datetime.datetime
    updated_at: datetime.datetime


class UserUpdate(UserBase):
    first_name: str
    last_name: str


class UpdatedUserResponse(BaseModel):
    access_token: str
    user: UserResponse


class UserUpdatePassword(UserBase):
    previous_password: str
    new_password: str


class UserRemove(UserBase):
    password: str


class UserResendVerification(UserBase):
    pass
