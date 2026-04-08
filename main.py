import requests
import os
import json
from datetime import datetime, timedelta

# ====================== 你的2个UP主 ======================
UP_UID_LIST = [
    "3691009626081367",
    "1671203508",
]
# ========================================================

# 强制打印环境变量，看看有没有读到
print("🔍 检查环境变量：")
print(f"BILIBILI_UID: {os.getenv('BILIBILI_UID')}")
print(f"SENDKEY配置: {'已配置' if os.getenv('SERVERCHAN_SENDKEY') else '❌ 未配置！'}")

SENDKEY = os.getenv("SERVERCHAN_SENDKEY")
DATA_FILE = "last.json"
CHECK_HOURS = 24

def push_wechat(title, content):
    if not SENDKEY:
        print("❌ 错误：SendKey 为空，无法推送！")
        return
    url = f"https://sctapi.ftqq.com/{SENDKEY}.send"
    data = {"title": title, "desp": content}
    try:
        resp = requests.post(url, data=data, timeout=15)
        result = resp.json()
        print(f"📤 推送请求发送，结果: {result}")
        if result["code"] == 0:
            print("✅ 微信推送成功！")
        else:
            print(f"❌ 推送失败: {result['message']}")
    except Exception as e:
        print(f"❌ 推送异常: {e}")

# ... 下面的代码省略，因为主要看第一步的报错 ...
# 你只需要确认：运行日志里有没有显示「SENDKEY配置: 已配置」
