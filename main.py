from fastapi import FastAPI
from model import Stock, Portfolio

app = FastAPI()


@app.get("/")
async def root():
    # model = MyModel(name="ishwarya", age=22, is_active=True, price=22.22, quantity=1, list_data=[1,2,3,4,5], dict_data={"name": "ishwarya", "age": 22}).dict()
    # stock = Stock(name="apple", price=150.0, quantity=10)
    # portfolio = Portfolio(stocks=[stock], total_value=1500.0, is_complete=True)

    s1 = Stock(name="AAPL", price=200.5, quantity=10)
    s2 = Stock(name="GOOG", price=1500.0, quantity=2)

    portfolio = Portfolio(
        stocks=[s1, s2],
        total_value=200.5 * 10 + 1500.0 * 2,
        is_complete=True
    )
    portfolio_dict = portfolio.model_dump()
    print(portfolio_dict)
    return portfolio, portfolio_dict


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

