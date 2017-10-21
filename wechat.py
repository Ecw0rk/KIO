#!/usr/bin/python3
import requests
import json

tokenUrl = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"

def get_token():
    values = {'corpid': 'ww1b4984f713aa92ed', 'corpsecret': 'Z4CyZ6_xyXitoEjgGWR_l1SFaME4J7B7D-p3ovo-VbU'}
    req = requests.post(tokenUrl, params=values)
    data = json.loads(req.text)
    return data["access_token"]


sendMsg = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token="

def send_msg(msg):
    # input msg need to change str()
    url = sendMsg + get_token()
    values = """{"touser" : "ChenJiaYu" ,
      "msgtype":"text",
      "agentid":"1000002",
      "text":{
        "content": "%s"
      },
      "safe":"0"
      }""" % msg
    requests.post(url, values)

if __name__ == '__main__':
    test_set = ['Strawberry Nigori', 'Nigori']
    test = ", ".join(test_set)
    send_msg(test)
