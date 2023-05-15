import numpy as np
from typing import List, Any
import requests as rq
from commendLogger import writeLog


def checkUserExist(userId: str) -> bool:
    if 15>len(userId)>8:
        return True
    return False
    # TODO: 人類驗證失敗
    token = rq.get(f"https://giver.104.com.tw/profile/{userId}").status_code
    if token == 200:
        return True
    return False

def weightToProd(weights: List[float], min_value: float = 0.001):
  
  meanX = sum(weights)/len(weights) 
  maxX = max(weights)
  assert maxX>0
  return [(w-meanX)/maxX if meanX<=w else min_value for w in weights]

# weightToProd([1,1,2,4,10,0])

GiverMap= np.load("GiverTagMap.20230515.npy", allow_pickle=True).tolist()
# print(GiverMap)


###
topicMap = {}
for userId, tags in GiverMap.items():
  if checkUserExist(userId) is False:
    continue
  print(userId, tags.keys())
  topics = tags.keys()
  scores = tags.values()
  try:   
    scores = weightToProd(scores)
  except AssertionError as e: 
    continue
  tags = sorted([(topic, score, userId) for topic, score in zip(topics,scores)], key= lambda tag: tag[1], reverse=True)
  for unit in tags:
    if unit[0] not in topicMap:
      topicMap[unit[0]] = []
    topicMap[unit[0]].append((unit[2], unit[1]))

for tag in topicMap.keys():
    print(tag)
    writeLog(topicMap[tag],tag)



