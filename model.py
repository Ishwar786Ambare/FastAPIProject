from pydantic import BaseModel, Field


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



