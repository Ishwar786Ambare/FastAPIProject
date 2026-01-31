from pydantic import BaseModel, Field, validator, field_validator


class MyModel(BaseModel):
    name: str = "ishwarya"
    age: int = 22   
    is_active: bool = True
    price: float = Field(default=22.22)
    quantity: int = Field(default=0)

    
class Stock(BaseModel):
    name: str
    price: float
    quantity: int
    is_active: bool = True
    tags: list[str] = []


class Portfolio(BaseModel):
    stocks: list[Stock] = []
    total_value: float = 0.0
    is_complete: bool = False

from datetime import datetime
class User(BaseModel):
    id: int = Field(gt=0)
    name: str = Field(min_length=3)
    age: int | None = None
    signup_ts: datetime | None = None
    friends: list[int] = []

    @field_validator('age')
    @classmethod
    def age_must_be_positive(cls, value):
        if value is not None and value <= 0:
            raise ValueError('Age must be positive')
        return value

    @field_validator('name')
    @classmethod
    def name_must_start_with_capital(cls, value):
        if not value[0].isupper():
            raise ValueError('Name must start with a capital letter')
        return value
    
    