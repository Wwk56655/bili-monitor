import requests
import os
import json
from datetime import datetime, timedelta

# ====================== 你的2个UP主（已填好） ======================
UP_UID_LIST = [
    "3691009626081367",
    "1671203508",
]
# ==================================================================

SENDKEY = os.getenv("SERVERCHAN_SENDKEY")
DATA_FILE = "last.json"
# 只监控「最近24小时」的新内容，彻底解决漏检/历史数据问题
CHECK_HOURS = 24

def push_wechat(title, content):
    if not SENDKEY:
        print("❌ 未配置SendKey，跳过推送")
        return
    url = f"https://sctapi.ftqq.com/{SENDKEY}.send"
    data = {"title": title, "desp": content}
    try:
        resp = requests.post(url, data=data, timeout=10)
        result = resp.json()
        if result["code"] == 0:
            print(f"✅ 推送成功：{title}")
        else:
            print(f"❌ 推送失败：{result['message']}")
    except Exception as e:
        print(f"❌ 推送异常：{e}")

def load_last():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, encoding="utf-8") as f:
            return json.load(f)
    # 初始化空数据
    return {"video": {}, "dynamic": {}, "comment": {}}

def save_last(d):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

def get_up_name(uid):
    try:
        url = f"https://api.bilibili.com/x/space/acc/info?mid={uid}"
        res = requests.get(url, timeout=5)
        return res.json()["data"]["name"]
    except Exception as e:
        print(f"⚠️ 获取UP主名称失败：{e}")
        return f"UP({uid})"

def check_new_video(uid, last_bvid):
    try:
        url = f"https://api.bilibili.com/x/space/wbi/arc/search?mid={uid}&pn=1&ps=5"
        res = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=5)
        data = res.json()
        if data["code"] != 0 or not data["data"]["list"]["vlist"]:
            return last_bvid, None, None, None
        
        # 遍历最近5个视频，找「24小时内发布」且「未记录」的新视频
        now = datetime.now().astimezone()
        for v in data["data"]["list"]["vlist"]:
            bvid = v["bvid"]
            # 跳过已记录的视频
            if bvid == last_bvid:
                continue
            # 检查发布时间是否在24小时内
            pub_time = datetime.fromtimestamp(v["created"], datetime.now().astimezone().tzinfo)
            if now - pub_time < timedelta(hours=CHECK_HOURS):
                return bvid, v["title"], v["author"], v["aid"]
        return last_bvid, None, None, None
    except Exception as e:
        print(f"⚠️ 视频监控异常：{e}")
        return last_bvid, None, None, None

def check_new_dynamic(uid, last_did):
    try:
        url = f"https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history?host_uid={uid}&offset_dynamic_id=0&need_top=0"
        res = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=5)
        data = res.json()
        if data["code"] != 0 or not data["data"]["cards"]:
            return last_did, None
        
        # 遍历最近5条动态，找「24小时内发布」且「未记录」的新动态
        now = datetime.now().astimezone()
        for card in data["data"]["cards"]:
            did = str(card["desc"]["dynamic_id"])
            # 跳过已记录的动态
            if did == last_did:
                continue
            # 检查发布时间是否在24小时内
            pub_time = datetime.fromtimestamp(card["desc"]["timestamp"], datetime.now().astimezone().tzinfo)
            if now - pub_time < timedelta(hours=CHECK_HOURS):
                content = json.loads(card["card"]).get("desc", "动态内容")
                return did, content
        return last_did, None
    except Exception as e:
        print(f"⚠️ 动态监控异常：{e}")
        return last_did, None

def check_up_comment(uid, aid, last_cid):
    if not aid:
        return last_cid, None
    try:
        url = f"https://api.bilibili.com/x/v2/reply/main?oid={aid}&type=1&mode=3&ps=20"
        res = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=5)
        data = res.json()
        if data["code"] != 0 or not data["data"]["replies"]:
            return last_cid, None
        
        # 遍历评论，找UP主发的、未记录的新评论
        for r in data["data"]["replies"]:
            if str(r["member"]["mid"]) == str(uid):
                cid = str(r["rpid"])
                if cid != last_cid:
                    return cid, r["content"]["message"]
        return last_cid, None
    except Exception as e:
        print(f"⚠️ 评论监控异常：{e}")
        return last_cid, None

def main():
    print(f"🚀 开始监控{len(UP_UID_LIST)}个UP主，检查最近{CHECK_HOURS}小时的新内容...")
    last = load_last()
    up_info_cache = {}
    
    for uid in UP_UID_LIST:
        print(f"\n🔍 正在监控UP主UID：{uid}")
        if uid not in up_info_cache:
            up_info_cache[uid] = get_up_name(uid)
        up_name = up_info_cache[uid]
        print(f"✅ UP主名称：{up_name}")

        # 1. 检查新视频
        old_bvid = last["video"].get(uid, "")
        bvid, title, _, aid = check_new_video(uid, old_bvid)
        if bvid != old_bvid and title:
            print(f"🎉 发现新视频：{title}")
            push_wechat(f"【B站提醒】{up_name}发新视频啦！", f"📺 标题：{title}\n🔗 链接：https://bilibili.com/video/{bvid}")
            last["video"][uid] = bvid

        # 2. 检查新动态
        old_did = last["dynamic"].get(uid, "")
        did, content = check_new_dynamic(uid, old_did)
        if did != old_did and content:
            print(f"🎉 发现新动态：{content[:20]}...")
            push_wechat(f"【B站提醒】{up_name}发新动态啦！", f"✍️ 内容：{content}\n🔗 链接：https://t.bilibili.com/{did}")
            last["dynamic"][uid] = did

        # 3. 检查UP主新评论
        if aid:
            old_cid = last["comment"].get(uid, "")
            cid, comment_content = check_up_comment(uid, aid, old_cid)
            if cid != old_cid and comment_content:
                print(f"🎉 发现UP主新评论：{comment_content[:20]}...")
                push_wechat(f"【B站提醒】{up_name}在视频下留言了！", f"💬 内容：{comment_content}\n🔗 视频链接：https://bilibili.com/video/av{aid}")
                last["comment"][uid] = cid

    save_last(last)
    print("\n✅ 本次监控完成，等待下一次检查...")

if __name__ == "__main__":
    main()
