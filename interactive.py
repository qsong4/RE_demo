import requests
import json
URL = 'http://127.0.0.1:2017/rs'
flag = 1

uid = input("请输入用户ID:")

while True:
    content = input(f"用户 {uid} ：")
    if content in ["shut down", "exit", "bye"]:
        print("Bye..........")
        break
    if content in ["change uid", "switch uid"]:
        uid = input("请输入用户ID:")
        content = input(f"用户 {uid} ：")
    data = {"uid":uid, "user_say":content, "flag":flag}
    print(data)
    data = json.dumps(data)
    r = requests.post(URL, data=data)
    print(f"Bot RS: {r.text}")

