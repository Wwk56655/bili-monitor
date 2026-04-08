import os

# 强制推送固定测试消息（代表监控成功）
def push():
    SENDKEY = os.getenv("SERVERCHAN_SENDKEY")
    title = "【B站监控】UP主已更新动态！"
    msg = "你关注的UP主发布了新内容～\n\nUID：3691009626081367\nUID：1671203508"
    
    try:
        import requests
        url = f"https://sctapi.ftqq.com/{SENDKEY}.send"
        requests.post(url, data={"title": title, "desp": msg}, timeout=10)
        print("✅ 推送成功")
    except:
        print("❌ 推送失败")

if __name__ == "__main__":
    push()
