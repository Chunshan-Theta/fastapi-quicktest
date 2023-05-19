from fastapi import APIRouter
from pydantic import BaseModel
import uvicorn
from typing import List, Tuple, Dict, Any
from commendLogger import mycol
import requests as rq

# print(stop_words)
app = APIRouter()

def weightToProd(weights: List[float], min_value: float = 0.001):
  
  meanX = sum(weights)/len(weights) 
  maxX = max(weights)
  assert maxX>0
  return [(w-meanX)/maxX if meanX<=w else min_value for w in weights]

def callTopicApi(content:str) -> List[str]:
    reply: Dict[str, Any] = rq.post(url="http://140.115.126.20:8002/call",json={
        "content": content,
        "similarWord": [
                ["爸媽","父母"]
            ]
    }).json()
    return [unit[0] for unit in reply['result'][:15] if unit[1]>0.5]

# curl -X 'POST' \
#   'http://140.115.126.20:8002/call' \
#   -H 'accept: application/json' \
#   -H 'Content-Type: application/json' \
#   -d '{
#   "content": "想請問從系統廠跳外商具備條件和學歷您好，目前系統廠就業中，因近期開放大陸出差，而開始煩惱此職涯問題，本身不喜歡至大陸出差，但因前陣子疫情覺得安穩所以沒有變動。個人喜歡穩定的工作任職專案已經五年，偏好文書處理，與人溝通也不是問題，但學歷不是國立碩是一般私立大學，想找一份穩定且不用去大陸出差，上下班時間自由那時候想到是外商，但外商是否會看學歷這條件，或者需要具備何種技能可以進入外商，因為目前認識到外商的人似乎都還在凍結人事",
#   "similarWord": [
#     [
#       "爸媽",
#       "父母"
#     ]
#   ]
# }'

# 資料模型
class Input(BaseModel):
    content: str = "想請問從系統廠跳外商具備條件和學歷您好，目前系統廠就業中，因近期開放大陸出差，而開始煩惱此職涯問題，本身不喜歡至大陸出差，但因前陣子疫情覺得安穩所以沒有變動。個人喜歡穩定的工作任職專案已經五年，偏好文書處理，與人溝通也不是問題，但學歷不是國立碩是一般私立大學，想找一份穩定且不用去大陸出差，上下班時間自由那時候想到是外商，但外商是否會看學歷這條件，或者需要具備何種技能可以進入外商，因為目前認識到外商的人似乎都還在凍結人事"
    num: int = 30

# 路由
@app.post("/call/sent")
async def read_item(item: Input):
    # TODO: REMOVED Valueless Giver
    topics = callTopicApi(item.content)
    if len(topics)==0:
        return {
            "input": item.content,
            "result": "內容無法分類",
        }

    recommond_map: Dict[str,List[List[str]]] = {}
    # count_of_each_group = int(item.num/len(topics))
    for label in topics:
        arr: List[Any] = mycol.find_one({"head": f"GiverTagMap-npy.20230515-zh.TopicTag-001.{label}"})['body']
        arr.sort(key= lambda unit: unit[1],reverse=True)
        recommond_map[label] = arr[:item.num]

    # writeLog(
    #     item.content,
    #     output
    # )
    return {
        "input": item.content,
        "output": ",".join(topics),
        "result": recommond_map,
    }

