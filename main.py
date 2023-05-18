from fastapi import FastAPI, APIRouter, HTTPException
# 將route1、2資料夾內的router1、2 python檔引入
from main_app_reason import app as ap1
from main_app_scores import app as ap2

app = FastAPI()            # 以app作為FastAPI實例
api_router = APIRouter()   # 以api_router作為APIRouter實例，本次重點!

api_router.include_router(ap1) # 把router1檔案裡的路由結合進api_router
api_router.include_router(ap2) # 把router2檔案裡的路由結合進api_router

# @api_router.get("/")
# def root() -> dict:
#     """
#     Root Get
#     """
#     return {"msg":"Hello root"}

# app.include_router(api_router)            # app實例將api_router的路由結合進去

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)