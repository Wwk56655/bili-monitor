import requests
import time
import os

# 配置
UID = os.getenv("BILIBILI_UP_UID")
SENDKEY = os.getenv("SERVERCHAN_SENDKEY")
API_URL = f"https://api.bilibili.com/x/space/wbi/arc/search?mid={UID}&pn=1&ps=1"
LAST_VIDEOS = set()

def get_new_video():
    try:
        resp = requests.get(API_URL, timeout=10)
        data = resp.json()
        if data["code"] != 0:
            return None
        vlist = data["data"]["list"]["vlist"]
        if not vlist:
            return None
        return vlist[0]
    except:
        return None

def send_wechat(title, content):
    url = f"https://sctapi.ftqq.com/{SENDKEY}.send"
    data = {"title": title, "desp": content}
    try:
        requests.post(url, data=data, timeout=10)
    except:
        pass

def main():
    global LAST_VIDEOS
    video = get_new_video()
    if not video:
        return
    bvid = video["bvid"]
    if bvid not in LAST_VIDEOS:
        title = video["title"]
        url = f"https://www.bilibili.com/video/{bvid}"
        desc = f"UP主更新了！\n标题：{title}\n链接：{url}"
        send_wechat("B站UP主更新提醒", desc)
        LAST_VIDEOS.add(bvid)

if __name__ == "__main__":
    main()
