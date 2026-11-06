from datetime import datetime

from pydantic import BaseModel, ConfigDict

class UserIn(BaseModel):
    username: str
    password: str
    telegram_id: int | None = None
    referred_by_id: int | None =  None
    is_referral_rewarded: bool = False


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    telegram_id: int | None
    is_new: bool = True


class NewKeyIn(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str
    email: str
    day_expiry: int
    payment_id: str | None = None


class Key(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_username: str
    email: str
    sub_id: str
    sub_link: str
    expiry_time: datetime
    payment_id: str | None = None


class UserInUsername(BaseModel):
    username: str