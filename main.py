import requests
import os
import json
from datetime import datetime

# ====================== 你的2个UP主（已填好） ======================
UP_UID_LIST = [
    "3691009626081367",
    "1671203508",
]
# ==================================================================

SENDKEY = os.getenv("SERVERCHAN_SENDKEY")
DATA_FILE = "last.json"

def push_wechat(title, content):
    if not SENDKEY:
        return
    url = f"https://sctapi.ftqq.com/{SENDKEY}.send"
    data = {"title": title, "desp": content}
    try:
        requests.post(url, data=data, timeout=10)
    except:
        pass

def load_last():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {"video": {}, "dynamic": {}, "comment": {}}

def save_last(d):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False)

def get_up_name(uid):
    try:
        url = f"https://api.bilibili.com/x/space/acc/info?mid={uid}"
        res = requests.get(url, timeout=5)
        return res.json()["data"]["name"]
    except:
        return f"UP({uid})"

def check_video(uid, last_bvid):
    try:
        url = f"https://api.bilibili.com/x/space/wbi/arc/search?mid={uid}&pn=1&ps=1"
        res = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=5)
        data = res.json()
        if data["code"] == 0 and data["data"]["list"]["vlist"]:
            v = data["data"]["list"]["vlist"][0]
            bvid = v["bvid"]
            if bvid != last_bvid:
                return bvid, v["title"], v["author"], v["aid"]
    except:
        pass
    return last_bvid, None, None, None

def check_dynamic(uid, last_did):
    try:
        url = f"https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history?host_uid={uid}"
        res = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=5)
        data = res.json()
        if data["code"] == 0 and data["data"]["cards"]:
            card = data["data"]["cards"][0]
            did = str(card["desc"]["dynamic_id"])
            if did != last_did:
                return did, json.loads(card["card"]).get("desc", "动态")
    except:
        pass
    return last_did, None

def check_up_comment(uid, aid, last_cid):
    try:
        url = f"https://api.bilibili.com/x/v2/reply/main?oid={aid}&type=1&mode=3&ps=10"
        res = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=5)
        data = res.json()
        if data["code"] == 0 and data["data"]["replies"]:
            for r in data["data"]["replies"]:
                if str(r["member"]["mid"]) == str(uid):
                    cid = str(r["rpid"])
                    if cid != last_cid:
                        return cid, r["content"]["message"]
    except:
        pass
    return last_cid, None

def main():
    last = load_last()
    up_info_cache = {}
    
    for uid in UP_UID_LIST:
        if uid not in up_info_cache:
            up_info_cache[uid] = get_up_name(uid)
        up_name = up_info_cache[uid]

        old_bvid = last["video"].get(uid, "")
        bvid, title, _, aid = check_video(uid, old_bvid)
        if bvid != old_bvid:
            push_wechat(f"【B站】{up_name} 新视频", f"标题：{title}\nhttps://bilibili.com/video/{bvid}")
            last["video"][uid] = bvid

        old_did = last["dynamic"].get(uid, "")
        did, content = check_dynamic(uid, old_did)
        if did != old_did:
            push_wechat(f"【B站】{up_name} 新动态", f"内容：{content}\nhttps://t.bilibili.com/{did}")
            last["dynamic"][uid] = did

        if aid:
            old_cid = last["comment"].get(uid, "")
            cid, comment_content = check_up_comment(uid, aid, old_cid)
            if cid != old_cid and comment_content:
                push_wechat(f"【B站】{up_name} 发布评论", f"评论：{comment_content}")
                last["comment"][uid] = cid

    save_last(last)

if __name__ == "__main__":
    main()
