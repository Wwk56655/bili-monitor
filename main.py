import requests
import time
import os
import json
from datetime import datetime

# 配置
UID = os.getenv("BILIBILI_UP_UID")
SENDKEY = os.getenv("SERVERCHAN_SENDKEY")
DATA_FILE = "last_update.json"  # 存储最后更新记录
BEIJING_TIME = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# B站API
VIDEO_API = f"https://api.bilibili.com/x/space/wbi/arc/search?mid={UID}&pn=1&ps=1"
DYNAMIC_API = f"https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history?host_uid={UID}&offset_dynamic_id=0&need_top=0"
COMMENT_API = "https://api.bilibili.com/x/v2/reply/main"

# 加载/保存记录
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"last_video_bvid": "", "last_dynamic_id": "", "last_up_comment_id": ""}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 微信推送
def send_wechat(title, content):
    if not SENDKEY:
        return
    url = f"https://sctapi.ftqq.com/{SENDKEY}.send"
    data = {"title": title, "desp": content}
    try:
        requests.post(url, data=data, timeout=10)
        print(f"[{BEIJING_TIME}] 推送成功：{title}")
    except Exception as e:
        print(f"[{BEIJING_TIME}] 推送失败：{e}")

# 1. 监控新视频
def check_new_video(last_bvid):
    try:
        resp = requests.get(VIDEO_API, timeout=10)
        data = resp.json()
        if data["code"] != 0 or not data["data"]["list"]["vlist"]:
            return None, last_bvid
        video = data["data"]["list"]["vlist"][0]
        bvid = video["bvid"]
        if bvid != last_bvid:
            return {
                "title": video["title"],
                "url": f"https://www.bilibili.com/video/{bvid}",
                "aid": video["aid"],
                "author": video["author"]
            }, bvid
        return None, last_bvid
    except Exception as e:
        print(f"[{BEIJING_TIME}] 视频监控异常：{e}")
        return None, last_bvid

# 2. 监控UP主动态
def check_new_dynamic(last_did):
    try:
        resp = requests.get(DYNAMIC_API, timeout=10)
        data = resp.json()
        if data["code"] != 0 or not data["data"]["cards"]:
            return None, last_did
        dynamic = data["data"]["cards"][0]
        did = dynamic["desc"]["dynamic_id"]
        if str(did) != str(last_did):
            card = json.loads(dynamic["card"])
            return {
                "content": card.get("content", "动态内容"),
                "url": f"https://t.bilibili.com/{did}",
                "author": dynamic["desc"]["user_profile"]["info"]["uname"]
            }, did
        return None, last_did
    except Exception as e:
        print(f"[{BEIJING_TIME}] 动态监控异常：{e}")
        return None, last_did

# 3. 监控UP主自己发的评论
def check_up_comment(aid, last_cid):
    if not aid:
        return None, last_cid
    try:
        url = f"{COMMENT_API}?oid={aid}&type=1&mode=3&ps=20"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if data["code"] != 0 or not data["data"]["replies"]:
            return None, last_cid
        # 遍历评论，找UP主发的
        for reply in data["data"]["replies"]:
            if reply["member"]["mid"] == UID:
                cid = reply["rpid"]
                if str(cid) != str(last_cid):
                    return {
                        "content": reply["content"]["message"],
                        "time": datetime.fromtimestamp(reply["ctime"]).strftime("%Y-%m-%d %H:%M:%S"),
                        "video_url": f"https://www.bilibili.com/video/av{aid}"
                    }, cid
        return None, last_cid
    except Exception as e:
        print(f"[{BEIJING_TIME}] 评论监控异常：{e}")
        return None, last_cid

def main():
    print(f"[{BEIJING_TIME}] 开始监控UP主（UID：{UID}）...")
    data = load_data()
    
    # 1. 检查新视频
    new_video, new_bvid = check_new_video(data["last_video_bvid"])
    if new_video:
        title = f"【B站提醒】{new_video['author']}发新视频啦！"
        content = f"📺 标题：{new_video['title']}\n🔗 链接：{new_video['url']}\n⏰ 时间：{BEIJING_TIME}"
        send_wechat(title, content)
        data["last_video_bvid"] = new_bvid
        # 新视频发布后，更新最新UP主评论记录
        _, new_cid = check_up_comment(new_video["aid"], data["last_up_comment_id"])
        data["last_up_comment_id"] = new_cid

    # 2. 检查新动态
    new_dynamic, new_did = check_new_dynamic(data["last_dynamic_id"])
    if new_dynamic:
        title = f"【B站提醒】{new_dynamic['author']}发新动态啦！"
        content = f"✍️ 内容：{new_dynamic['content']}\n🔗 链接：{new_dynamic['url']}\n⏰ 时间：{BEIJING_TIME}"
        send_wechat(title, content)
        data["last_dynamic_id"] = new_did

    # 3. 检查UP主新评论（只监控最新视频的评论区）
    if data["last_video_bvid"]:
        # 先获取最新视频的aid
        try:
            resp = requests.get(VIDEO_API, timeout=10)
            aid = resp.json()["data"]["list"]["vlist"][0]["aid"]
            new_comment, new_cid = check_up_comment(aid, data["last_up_comment_id"])
            if new_comment:
                title = f"【B站提醒】{new_video['author']}在视频下留言了！"
                content = f"💬 内容：{new_comment['content']}\n🔗 视频链接：{new_comment['video_url']}\n⏰ 时间：{new_comment['time']}"
                send_wechat(title, content)
                data["last_up_comment_id"] = new_cid
        except:
            pass

    save_data(data)
    print(f"[{BEIJING_TIME}] 监控完成，等待下一次检查...")

if __name__ == "__main__":
    main()
