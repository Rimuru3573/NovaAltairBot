from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

class UserIn(BaseModel):
    username: str
    password: str
    referred_by_user: str | None =  None
    is_referral_rewarded: bool = False


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    is_new: bool = True


class NewKeyIn(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str
    email: str
    day_expiry: int = Field(gt=0, le=365)
    limit_hwid: int = 0
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