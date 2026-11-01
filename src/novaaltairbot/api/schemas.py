from pydantic import BaseModel, ConfigDict

class UserIn(BaseModel):
    username: str
    password: str
    telegram_id: int = None

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    telegram_id: int | None
    is_new: bool = True