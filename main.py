from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI()

# 資料模型
class Item(BaseModel):
    name: str
    price: float
    is_offer: bool = False

# 路由
@app.post("/call")
async def read_item(item: Item):
    return {"item_id": "item_id", "q": "q", "item": item}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)