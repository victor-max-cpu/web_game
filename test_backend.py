import requests

BASE_URL = "http://127.0.0.1:5000"

def test_register():
    print("--- 测试注册新用户 ---")
    data = {
        "username": "player_01",
        "password": "pwd123",
        "action": "register"
    }
    # 注意：如果是表单提交用 data=，如果是 JSON 提交用 json=
    # 根据你之前的代码，使用的是 request.form，所以这里用 data=
    resp = requests.post(f"{BASE_URL}/login", data=data)
    print(f"状态码：{resp.status_code}")
    print(f"返回内容：{resp.text}\n")

def test_login_success():
    print("--- 测试正确登录 ---")
    data = {
        "username": "player_01",
        "password": "pwd123",
        "action": "login"
    }
    resp = requests.post(f"{BASE_URL}/login", data=data, allow_redirects=False)
    print(f"状态码：{resp.status_code}")
    if 'session' in resp.cookies:
        print("✅ 登录成功，获取到 Session Cookie!")
    else:
        print("❌ 登录失败")
    print()

def test_login_fail():
    print("--- 测试密码错误 ---")
    data = {
        "username": "player_01",
        "password": "wrong_pwd",
        "action": "login"
    }
    resp = requests.post(f"{BASE_URL}/login", data=data)
    print(f"返回内容：{resp.text}")
    if "不匹配" in resp.text:
        print("✅ 后端正确返回了错误提示逻辑")
    print()

if __name__ == "__main__":
    # 确保你的 app.py 正在运行
    test_register()
    test_login_success()
    test_login_fail()