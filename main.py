from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from typing import List, Tuple
from commendLogger import mycol


# print(stop_words)
app = FastAPI()


# 資料模型
class Input(BaseModel):
    label: str = "topic-面試"
    num: int = 30

# 路由
@app.post("/call")
async def read_item(item: Input):
    # TODO: REMOVED Valueless Giver
    label = item.label
    arr = mycol.find_one({"head": f"GiverTagMap-npy.20230515-zh.TopicTag-001.{label}"})['body']
    arr.sort(key= lambda unit: unit[1],reverse=True)

    # writeLog(
    #     item.content,
    #     output
    # )
    return {
        "input": label,
        "result": arr[:item.num],
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)