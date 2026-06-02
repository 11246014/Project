from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class ProductCreate(BaseModel):
    name: str
    price: int
    description: str

class ProductResponse(BaseModel):
    id: int
    name: str
    price: int
    description: str

    class Config:
        from_attributes = True