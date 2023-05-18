from fastapi import FastAPI,APIRouter
from pydantic import BaseModel
import uvicorn
from typing import NamedTuple, List, Dict, Any
import os
import openai
from logger_reason import writeLog
openai.api_key  = os.environ.get('chatgpt_api_key')


class ScoreFilter(NamedTuple):
  title: str
  description: str
  example: str
def toChatGPTFilter(filters: List[ScoreFilter], moreDetail=False) -> str:
    returnContent: str = f"扮演一個內容分類模型，分類項目有{len(filters)}個。請依照範例樣式輸出，找出最適合的分類，並用繁體中文和第二人稱的方式說明原因\n"
    # for idx, f in enumerate(filters):
    #     returnContent = returnContent+f"{idx+1}. {f.title}: {f.description}\n"
    # returnContent+=f"\n"
    if moreDetail:
        returnContent+="\n回應範例如下:\n\n"
        for f in filters:
            returnContent = returnContent+f"{f.example} => {f.title} ;;;  {f.description}\n"
    return returnContent+"\n\n"

roleFilter = [
    # ScoreFilter(title="Bewildered", description="該類型內容著重用戶處於對於未來職涯選擇感到難以抉擇。"),
    # ScoreFilter(title="Seeking-comfort", description="該類型內容帶有受害者心態、感覺委屈或不滿現狀，強調身心問題、情緒感受或人際關係。"),
    # ScoreFilter(title="Inquiry", description="該類型內容不討論身心問題、情緒感受或人際關係，只討論數值資訊且條理清晰，是尋求數值型答案的明確答案。"),
    ScoreFilter(title="Bewildered", description="因為你的情緒屬於不知所措，並且我們不認為你想得到答案，更像是以參考意見為主，同時問題不明確。", example="我對於未來發展感到徬徨"),
    ScoreFilter(title="Seeking-comfort", description="因為你的情緒是強烈負面，同時也出現攻擊或捍衛性字眼（例如衝康）", example="我的主管實在是太糟糕了，一直衝康"),
    ScoreFilter(title="Inquiry", description="因為這段內容中顯示你的情緒平穩，同時不透露真實感受，有背景資訊、條理清晰，問題明確", example="我該如何準備才能應徵工程師呢"),
]



app = APIRouter()




# 資料模型
class Input(BaseModel):
    content: str = "想請問從系統廠跳外商具備條件和學歷您好，目前系統廠就業中，因近期開放大陸出差，而開始煩惱此職涯問題，本身不喜歡至大陸出差，但因前陣子疫情覺得安穩所以沒有變動。個人喜歡穩定的工作任職專案已經五年，偏好文書處理，與人溝通也不是問題，但學歷不是國立碩是一般私立大學，想找一份穩定且不用去大陸出差，上下班時間自由那時候想到是外商，但外商是否會看學歷這條件，或者需要具備何種技能可以進入外商，因為目前認識到外商的人似乎都還在凍結人事"
class Output(BaseModel):
    input: str =  "content"
    passStatus: bool = True
    result: List[str] = f"Input wrong.: ..."
    runCount: int = 0
    role: Any = None

# 路由
@app.post("/callapi/reasons")
async def read_item(item: Input) -> Output:

    runCount = 0
    while runCount<2:
        role = toChatGPTFilter(roleFilter, False if runCount > 0 else True)
        try:
            response = openai.ChatCompletion.create(
                model = 'gpt-3.5-turbo',
                messages = [
                    {'role': 'system', 'content': role},
                    {'role': 'user', 'content': f"{item.content} => "}
                ],
                temperature = 0 
            )

            apiResult = response["choices"][0]["message"]["content"]
            processedResult = apiResult.split(";;;")
            assert isinstance(processedResult,list)
            assert len(processedResult) == 2

            processedResult = [r.strip() for r in processedResult]
            writeLog(item.content, processedResult)
            return Output(
                input = item.content,
                passStatus = True,
                result = processedResult,
                runCount = runCount
            )
        except (KeyError, IndexError, AssertionError) as e:
            runCount+=1
        except openai.error.AuthenticationError as e:
            return Output(
                input = item.content,
                passStatus = False,
                result = {"systemError": "AuthenticationError: Incorrect API key provided"},
                runCount = runCount
            )


        return Output(
            input = item.content,
            passStatus = False,
            result ={
                "reply": f"{apiResult}"
            },
            runCount = runCount,
            role = role
        )



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)