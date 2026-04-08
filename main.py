import requests
import os
import json

# 这是你配置的两个UP主
UID_LIST = ["3691009626081367", "1671203508"]
SENDKEY = os.getenv("SERVERCHAN_SENDKEY")

# 微信推送
def push(title, msg):
    if not SENDKEY:
        return
    url = f"https://sctapi.ftqq.com/{SENDKEY}.send"
    data = {"title": title, "desp": msg}
    try:
        requests.post(url, data=data, timeout=10)
        print("✅ 推送成功")
    except:
        print("❌ 推送失败")

# 获取UP主名字
def get_name(uid):
    try:
        res = requests.get(f"https://api.bilibili.com/x/space/acc/info?mid={uid}", timeout=5)
        return res.json()["data"]["name"]
    except:
        return f"UP({uid})"

# 检查视频
def check_video(uid):
    try:
        url = f"https://api.bilibili.com/x/space/wbi/arc/search?mid={uid}&pn=1&ps=1"
        res = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=5)
        v = res.json()["data"]["list"]["vlist"][0]
        return v["bvid"], v["title"], v["author"]
    except:
        return None, None, None

# 检查动态
def check_dynamic(uid):
    try:
        url = f"https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history?host_uid={uid}"
        res = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=5)
        card = res.json()["data"]["cards"][0]
        did = str(card["desc"]["dynamic_id"])
        content = json.loads(card["card"]).get("desc", "动态")
        return did, content
    except:
        return None, None

def main():
    print("🚀 开始监控...")
    print(f"📤 SendKey 是否存在: {'是' if SENDKEY else '否'}")

    for uid in UID_LIST:
        print(f"\n🔍 检查UID: {uid}")
        name = get_name(uid)
        print(f"✅ UP主: {name}")

        bvid, title, author = check_video(uid)
        if bvid:
            push(f"【B站】{name} 发布新视频", f"标题：{title}\nhttps://bilibili.com/video/{bvid}")
            print("🎬 视频已推送")

        did, content = check_dynamic(uid)
        if did:
            push(f"【B站】{name} 发布新动态", f"内容：{content}\nhttps://t.bilibili.com/{did}")
            print("📝 动态已推送")

    print("\n✅ 本次运行完成")

if __name__ == "__main__":
    main()
