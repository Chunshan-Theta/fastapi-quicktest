from fastapi import APIRouter
from pydantic import BaseModel
import uvicorn
from typing import List, Tuple, Dict, Any
from commendLogger import mycol
import requests as rq

# print(stop_words)
app = APIRouter()





# 資料模型
class Input(BaseModel):
    label: str = "topic-轉職"
    num: int = 30

# 路由
@app.post("/call/label")
async def read_item(item: Input):
    # TODO: REMOVED Valueless Giver


    label= item.label
    arr: List[Any] = mycol.find_one({"head": f"GiverTagMap-npy.20230515-zh.TopicTag-001.{label}"})['body']
    arr.sort(key= lambda unit: unit[1],reverse=True)


    # writeLog(
    #     item.content,
    #     output
    # )
    return {
        "input": item.label,
        "result": arr[:item.num]
    }
