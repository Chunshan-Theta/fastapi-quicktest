from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from typing import TypedDict, Dict, Any, Tuple, List
import os


uri = os.environ.get('mongo_host')
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
client.admin.command('ping')
print("Pinged your deployment. You successfully connected to MongoDB!")

# 指定數據庫和集合對象 
mydb = client["recommend"] 
mycol = mydb["topic104"]


class ExecuteLogUnit(TypedDict):
  head: str
  body: List[Tuple[str,float]]
  approach: Dict[str, str]

def createExecuteLogUnit(
    modelType: str, 
    baseModel: str, 
    lang: str, 
    version: str, 
    modelNumber: str,
    logTag: str,
    body: Any, 
    approachAccount: str, 
    approachActionTag: str, 
    approachExecuter: str
  ):
  modelTag: str = f"{modelType}-{baseModel}-{lang}"
  versionTag: str = f"{version}-{modelNumber}"
  return ExecuteLogUnit(
      head=f"{modelTag}.{versionTag}.{logTag}",
      body=body,
      approach = {
          "account": approachAccount,
          "actionTag": approachActionTag,
          "executer": approachExecuter
      }
  )

def writeLog(body: List[Tuple[str,float]], topicName: str):
    body = createExecuteLogUnit(
        modelType = "GiverTagMap", 
        logTag = topicName,
        baseModel = "npy.20230515", 
        lang = "zh", 
        version = "TopicTag", 
        modelNumber = "001",
        body = body,
        approachAccount = "voiss", 
        approachActionTag = "weight2prop", 
        approachExecuter = "repo-script"
    )

    return mycol.insert_one(body)

