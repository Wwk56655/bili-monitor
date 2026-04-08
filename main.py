import requests
import os

# 强制测试：直接发微信
def test_push():
    SENDKEY = os.getenv("SERVERCHAN_SENDKEY")
    print("✅ 读取到 SendKey")
    
    url = f"https://sctapi.ftqq.com/{SENDKEY}.send"
    data = {
        "title": "【测试】GitHub 监控正常！",
        "desp": "你的B站提醒脚本已经修好啦！接下来会自动监控UP主动态～"
    }
    
    try:
        res = requests.post(url, data=data, timeout=10)
        print("📤 推送结果：", res.text)
        print("✅ 测试消息已发送到微信！")
    except Exception as e:
        print("❌ 错误：", e)

if __name__ == "__main__":
    test_push()
