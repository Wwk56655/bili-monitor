import os
import requests

def push_online():
    SENDKEY = os.getenv("SERVERCHAN_SENDKEY")
    title = "✅ B站监控正在运行"
    msg = "监控服务正常在线中\n每5分钟自动检查一次\n关注UP：3691009626081367、1671203508"

    url = f"https://sct.ftqq.com/{SENDKEY}.send"
    data = {"title": title, "desp": msg}
    try:
        requests.post(url, data=data, timeout=10)
        print("推送成功")
    except:
        print("推送失败")

if __name__ == "__main__":
    push_online()
