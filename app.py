from flask import Flask, request, jsonify, send_from_directory, session, redirect, url_for
import os
import json
import functools

app = Flask(__name__, static_folder='static')
app.secret_key = 'web_game_secret_key'  # 用于会话加密

# 数据文件路径
DATA_FILE = 'users.json'

def load_users():
    """加载用户数据"""
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}

def save_users(users):
    """保存用户数据"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

def login_required(f):
    """装饰器：检查是否已登录"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    """主页：登录/注册界面"""
    if 'username' in session:
        return redirect(url_for('game'))
    return send_from_directory('.', 'index.html')

@app.route('/game')
@login_required
def game():
    """游戏界面"""
    return send_from_directory('.', 'game.html')

@app.route('/api/register', methods=['POST'])
def register():
    """注册接口"""
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return jsonify({'success': False, 'message': '用户名和密码不能为空'}), 400

    users = load_users()
    
    if username in users:
        return jsonify({'success': False, 'message': '用户名已存在，请更换'}), 400

    # 保存新用户
    users[username] = {'password': password} # 实际项目中密码应加密存储
    save_users(users)
    
    # 自动登录
    session['username'] = username
    return jsonify({'success': True, 'message': '注册并登录成功'})

@app.route('/api/login', methods=['POST'])
def login():
    """登录接口"""
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return jsonify({'success': False, 'message': '用户名和密码不能为空'}), 400

    users = load_users()
    
    if username not in users or users[username]['password'] != password:
        return jsonify({'success': False, 'message': '用户名或密码错误'}), 401

    session['username'] = username
    return jsonify({'success': True, 'message': '登录成功'})

@app.route('/api/logout', methods=['POST'])
def logout():
    """登出接口"""
    session.pop('username', None)
    return jsonify({'success': True})

@app.route('/api/me')
def get_current_user():
    """获取当前登录用户"""
    if 'username' in session:
        return jsonify({'username': session['username'], 'logged_in': True})
    return jsonify({'logged_in': False})

if __name__ == '__main__':
    # 确保数据文件存在
    if not os.path.exists(DATA_FILE):
        save_users({})
    
    print("服务器启动中...")
    print("请访问: http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True)