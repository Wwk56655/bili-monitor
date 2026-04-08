import requests
import os

# 你要监控的UP主
UID_LIST = [
    "3691009626081367",
    "1671203508"
]
SENDKEY = os.getenv("SERVERCHAN_SENDKEY")

# 微信推送
def push(title, msg):
    url = f"https://sctapi.ftqq.com/{SENDKEY}.send"
    data = {"title": title, "desp": msg}
    try:
        requests.post(url, data=data, timeout=10)
        print("✅ 推送成功")
    except:
        print("❌ 推送失败")

# 获取UP主名字
def get_up_name(uid):
    try:
        res = requests.get(f"https://api.bilibili.com/x/space/acc/info?mid={uid}", timeout=5)
        return res.json()["data"]["name"]
    except:
        return f"UP({uid})"

# 检查最新动态
def check_new_dynamic(uid):
    try:
        url = f"https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history?host_uid={uid}"
        res = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=5)
        data = res.json()
        card = data["data"]["cards"][0]
        did = str(card["desc"]["dynamic_id"])
        content = str(card["desc"]["dynamic_id"])
        return did, f"https://t.bilibili.com/{did}"
    except:
        return None, None

def main():
    for uid in UID_LIST:
        name = get_up_name(uid)
        did, link = check_new_dynamic(uid)
        if did:
            push(f"【B站】{name} 有新动态", f"链接：{link}")
            print(f"🔔 {name} 动态已推送")

if __name__ == "__main__":
    main()
