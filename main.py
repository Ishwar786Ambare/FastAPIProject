from fastapi import FastAPI
from model import Stock, Portfolio, User
from pydantic import ValidationError

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    
)


from database import DATABASE_URL
print('------------------------------------------')
print("DATABASE_URL", DATABASE_URL)
print('------------------------------------------')

@app.get("/image")
def get_image():
    url = "https://m.media-amazon.com/images/W/MEDIAX_1215821-T2/images/I/61vynIQfhIL._SX679_.jpg"
    r = requests.get(url)
    return Response(content=r.content, media_type="image/jpeg")


@app.get("/health")
def root():
    user = None
    print('------------------User Model------------------')
    try:
        user_data = {
            "id": 1,
            "name": "John Doe",
            "signup_ts": "2023-10-27T10:00:00",
            "friends": [2, 3, 4]
        }
        user = User(**user_data)
        print(user.json(), type(user.json()))
        print(user.dict(), type(user.dict()))
    except ValidationError as e:
        print(e)
    print('------------------User Model------------------')


    return user

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
    # print(portfolio_dict)

    portfolio_json = portfolio.model_dump_json()
    # print(portfolio_json)

    return portfolio, portfolio_dict, portfolio_json


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.get("/test")
async def test(name: str = "World"):
    return {"message": f"Hello {name}"}
