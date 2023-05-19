from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from typing import TypedDict, Dict, Any
import os


uri = os.environ.get('mongo_host')

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
client.admin.command('ping')
print("Pinged your deployment. You successfully connected to MongoDB!")

# 指定數據庫和集合對象 
mydb = client["model"] 
mycol = mydb["executelog"]


class ExecuteLogUnit(TypedDict):
  head: str
  input: Dict[str, Any]
  output: Dict[str, Any]
  approach: Dict[str, str]

def createExecuteLogUnit(
    modelType: str, 
    baseModel: str, 
    lang: str, 
    version: str, 
    modelNumber: str,
    logTag: str,
    inputContent: Any, 
    output: Dict[str, Any],
    approachAccount: str, 
    approachActionTag: str, 
    approachExecuter: str
  ):
  modelTag: str = f"{modelType}-{baseModel}-{lang}"
  versionTag: str = f"{version}-{modelNumber}"
  return ExecuteLogUnit(
      head=f"{modelTag}.{versionTag}.{logTag}",
      input = {
          "content": inputContent,
      },
      output = output,
      approach = {
          "account": approachAccount,
          "actionTag": approachActionTag,
          "executer": approachExecuter
      }
  )

def writeLog(input: Any, output: Any):
    body = createExecuteLogUnit(
        modelType = "intentClassification", 
        logTag = "topics_20230519_1",
        baseModel = "keywords", 
        lang = "zh", 
        version = "normal", 
        modelNumber = "001",
        inputContent = input, 
        output = output,
        approachAccount = "voiss", 
        approachActionTag = "callAPI", 
        approachExecuter = "NCU.API.140.115.126.20"
    )

    return mycol.insert_one(body)