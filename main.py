from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from typing import List, Tuple
import spacy
import requests
from logger import writeLog


stop_words = requests.get("https://raw.githubusercontent.com/Chunshan-Theta/stopwords_zh/main/career-consultant-field.txt").text.split("\n")
# print(stop_words)
app = FastAPI()


# 載入中文語言模型
nlp = spacy.load("zh_core_web_trf")

# 輸入要解析的中文句子
# text = "目前是派遣人員待在外商一年半了，當初會進來也是想說可以學習到會計類（非本科出生）又加上是外商，幸運的話可以轉成正職，而且離我家很近（騎車5分鐘）無奈現在我待的部門正職飽和狀態，但我很喜歡工作的環境，主管不會刁難同事們又很好，簡單來說辦公室文化很棒，其實就是舒適圈…派遣跟正職差在的就是福利，我沒有年終跟三節，雖然不是所有公司都會有這些，但感覺還是有差，老實說我不知道我現在該怎麼做，我要繼續熬還是該脫離舒適圈？"
# text = "請問談薪水有沒有什麼技巧？很多面試官都會問你期待薪資，但因為不知道他們的核薪制度，又怕自己開的太低或太高，有什麼建議嗎？謝謝"
# text = "20年的pcb製程經驗無用 求轉職建議 退伍後 入pcb大夜班工作20年 擔任主管職 學習到稼動率 人員分配 排班 目前40多歲 全製程全學習過 除了工程cam部分.但遇到了縮編夜班資遣 ~ 另謀出路到了間pcb代工廠擔任生管  以接受降薪6千 大夜班沒3萬 能接觸到中壢以北需要代工的大小廠 其中不乏上市上櫃大廠 約50間左右  發現每間都在加班管制 縮編夜班 連自己的公司生管職位每周開會都聽到老闆說想收掉 ~~心冷 目前有興起個念頭~轉職  但回頭 我已經20年在板廠了 如果從事其他廠的作業員開始?是否還有機會? 可能對pcb絕望了 甚至考慮保全 7-11 因為得生活 希望前輩能多提點指教 謝謝  目前待業中"
# doc = nlp(text)

def doc2sent(doc: spacy.tokens.doc.Doc) -> Tuple[List[str], int]:
    docMap= {str(token.i):"".join([t.text for t in token.lefts]+[token.text]+[t.text for t in token.rights]) for token in doc }
    # print(docMap)
    return_list:List[str] = []
    return_list_len = 0

    for token in doc:
        if token.dep_ == "ROOT":
            # print([t.text for t in token.lefts]+[token.text]+[t.text for t in token.rights])
            label = ""
            for t in [t for t in token.lefts]:
                label += docMap[str(t.i)]
            label+=token.text
            for t in [t for t in token.rights]:
                label+= docMap[str(t.i)]
            return_list.append(label)
            return_list_len+=len(label)
    return return_list, return_list_len


# 資料模型
class Input(BaseModel):
    content: str = "想請問從系統廠跳外商具備條件和學歷您好，目前系統廠就業中，因近期開放大陸出差，而開始煩惱此職涯問題，本身不喜歡至大陸出差，但因前陣子疫情覺得安穩所以沒有變動。個人喜歡穩定的工作任職專案已經五年，偏好文書處理，與人溝通也不是問題，但學歷不是國立碩是一般私立大學，想找一份穩定且不用去大陸出差，上下班時間自由那時候想到是外商，但外商是否會看學歷這條件，或者需要具備何種技能可以進入外商，因為目前認識到外商的人似乎都還在凍結人事"
    enable_stop_words: bool = False
    customized_stop_words: List[str] = []

# 路由
@app.post("/call")
async def read_item(item: Input):
    content = item.content
    if item.enable_stop_words:
        for stw in stop_words+item.customized_stop_words:
            content = content.replace(stw, " ")
    
    result: Tuple[List[str], int] = doc2sent(nlp(content))

    writeLog(
        item.content,
        result[0]
    )
    return {
        "input": item.content ,
        "input_len": len(item.content) , 
        "result": result[0],
        "result_len": result[1]
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)