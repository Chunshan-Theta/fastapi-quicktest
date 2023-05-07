from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from typing import List, Tuple
from logger import writeLog
from keywords import keywords_s

# print(stop_words)
app = FastAPI()

def calNumKeywords(document: str, keywords: List[str], sameWords: List[str]) -> int:
  for old, new in sameWords:
    document = document.replace(old, new)
  count = 0
  for word in keywords:
    count += document.count(word)
  return count

def genFeatures(features: List[int]):
  f_mean = sum(features)/len(features)
  f_max = max(features)
  f_max = 1 if f_max == 0 else f_max 
  features = [n-f_mean for n in features]
  features = [n/f_max if n > 0 else 0 for n in features]
  return features

# 資料模型
class Input(BaseModel):
    content: str = "想請問從系統廠跳外商具備條件和學歷您好，目前系統廠就業中，因近期開放大陸出差，而開始煩惱此職涯問題，本身不喜歡至大陸出差，但因前陣子疫情覺得安穩所以沒有變動。個人喜歡穩定的工作任職專案已經五年，偏好文書處理，與人溝通也不是問題，但學歷不是國立碩是一般私立大學，想找一份穩定且不用去大陸出差，上下班時間自由那時候想到是外商，但外商是否會看學歷這條件，或者需要具備何種技能可以進入外商，因為目前認識到外商的人似乎都還在凍結人事"
    similarWord: List[List[str]] = [['爸媽', '父母']]

# 路由
@app.post("/call")
async def read_item(item: Input):
    content = item.content
    scores = {title: calNumKeywords(content, keywords, item.similarWord) for title, keywords in keywords_s.items()}
    output = [ (t,s) for t,s in zip(scores.keys(), genFeatures(scores.values()))]
    output = sorted(output, key=lambda x: x[1], reverse=True)

    writeLog(
        item.content,
        output
    )
    return {
        "input": item.content ,
        "result": output,
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)