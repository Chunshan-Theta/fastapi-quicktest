from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from typing import NamedTuple, List, Dict, Any
import os
import openai
from logger import writeLog
openai.api_key  = os.environ.get('chatgpt_api_key')


class ScoreFilter(NamedTuple):
  title: str
  description: str
def toChatGPTFilter(filters: List[ScoreFilter]) -> str:
  returnContent: str = f"你是一個在職業介紹所的用戶分析專家，請根據該內文來分析內容與以下{len(filters)}個項目的相關強弱程度？\n"
  for f in filters:
        returnContent = returnContent+f"{f.title}: {f.description}\n"
  return returnContent+f"\n逐個項目回答{len(filters)}個項目，以`主題名稱：強/弱`格式回應。\n不說明原因，不解釋內容\n"

roleFilter = [
    # ScoreFilter(title="Bewildered", description="該類型內容著重用戶處於對於未來職涯選擇感到難以抉擇。"),
    # ScoreFilter(title="Seeking-comfort", description="該類型內容帶有受害者心態、感覺委屈或不滿現狀，強調身心問題、情緒感受或人際關係。"),
    # ScoreFilter(title="Inquiry", description="該類型內容不討論身心問題、情緒感受或人際關係，只討論數值資訊且條理清晰，是尋求數值型答案的明確答案。"),
    ScoreFilter(title="Bewildered", description="情緒屬於不知所措，不一定想得到答案，以參考意見為主，問題不明確。"),
    ScoreFilter(title="Seeking-comfort", description="情烈的負面情緒，或出現攻擊或捍衛性字眼（例如被衝康）"),
    ScoreFilter(title="Inquiry", description="情緒平穩，不透露真實感受，有背景資訊、條理清晰，問題明確"),
]
role = toChatGPTFilter(roleFilter)


app = FastAPI()



# 資料模型
class Input(BaseModel):
    content: str = "想請問從系統廠跳外商具備條件和學歷您好，目前系統廠就業中，因近期開放大陸出差，而開始煩惱此職涯問題，本身不喜歡至大陸出差，但因前陣子疫情覺得安穩所以沒有變動。個人喜歡穩定的工作任職專案已經五年，偏好文書處理，與人溝通也不是問題，但學歷不是國立碩是一般私立大學，想找一份穩定且不用去大陸出差，上下班時間自由那時候想到是外商，但外商是否會看學歷這條件，或者需要具備何種技能可以進入外商，因為目前認識到外商的人似乎都還在凍結人事"
class Output(BaseModel):
    input: str =  "content"
    passStatus: bool = True
    result: Dict[str, Any] = f"Input wrong.: ..."
    runCount: int = 0

# 路由
@app.post("/call")
async def read_item(item: Input) -> Output:

    runCount = 0
    while runCount<1:
        try:
            response = openai.ChatCompletion.create(
                model = 'gpt-3.5-turbo',
                messages = [
                    {'role': 'system', 'content': role},
                    {'role': 'user', 'content': item.content}
                ],
                temperature = 0 
            )
            scores = response["choices"][0]["message"]["content"]
            scores = scores.replace("：", ": ")
            scores = [score.split(": ") for score in scores.split("\n")]
            processedResult = {ss[0]: '強' if '強' in ss[1] else '弱'  for ss in scores }
            for rf in roleFilter:
                assert rf.title in processedResult

            writeLog(item.content, processedResult)
            return Output(
                input = item.content,
                passStatus = True,
                result = processedResult,
                runCount = runCount
            )
        except (KeyError, IndexError) as e:
            runCount+=1

        responesLabel = response["choices"][0]["message"]["content"]
        return Output(
            input = item.content,
            passStatus = False,
            result = {ss[0]: ss[1] for ss in scores},
            runCount = runCount
        )



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)