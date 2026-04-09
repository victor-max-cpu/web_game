from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # 用于会话管理和闪存消息，生产环境请更换为复杂随机字符串

DB_NAME = 'database.db'

# --- 数据库辅助函数 ---
def get_db_connection():
    """建立数据库连接"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # 让结果可以通过列名访问
    return conn

def init_db():
    """初始化数据库表"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 创建玩家表
    # username: 用户名 (唯一索引，防止重复)
    # password: 密码 (实际项目中应存储哈希值，这里为了演示简单直接存储明文，建议后续加密)
    # progress: 游戏进度 (预留字段，默认空字符串或 JSON 字符串)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            progress TEXT DEFAULT '{}'
        )
    ''')
    
    conn.commit()
    conn.close()
    print("数据库初始化完成。")

# --- 路由逻辑 ---


@app.route('/')
def index():
    """首页：如果已登录去游戏页，否则去登录页"""
    if 'username' in session:
        return redirect(url_for('game'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    
    if request.method == 'POST':
        action = request.form.get('action')
        username = request.form.get('username')
        password = request.form.get('password')
        
        db = get_db_connection()
        
        if action == 'register':
            # 注册逻辑
            try:
                db.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
                db.commit()
                return render_template('login.html', error=None, success_msg="注册成功，请登录")
            except sqlite3.IntegrityError:
                error = "用户名已存在，请换一个"
                
        elif action == 'login':
            # 登录逻辑
            user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
            
            if user is None:
                error = "用户不存在"  # <--- 这个字符串会传到 HTML 的 {{ error }}
            elif user['password'] != password:
                error = "密码错误"
            else:
                session['username'] = user['username']
                return redirect(url_for('game'))
        
        db.close()

    # 如果是 GET 请求，或者 POST 但出错了，渲染页面并传入 error
    return render_template('login.html', error=error)

@app.route('/game')
def game():
    """游戏主界面（需要登录验证）"""
    if 'username' not in session:
        flash('请先登录！', 'warning')
        return redirect(url_for('login'))
    
    # 这里将来会加载玩家进度并渲染游戏页面
    return f"<h1>欢迎回来，{session['username']}!</h1><p>游戏加载中... (进度缓存功能待开发)</p><a href='/logout'>退出登录</a>"

@app.route('/logout')
def logout():
    """退出登录"""
    session.clear()
    flash('已安全退出。', 'info')
    return redirect(url_for('login'))

@app.route('/api/k1_login', methods=['POST'])
def k1_login():
    """K1 按键：执行登录操作（从表单获取用户名密码）"""
    username = request.form.get('username')
    password = request.form.get('password')
    
    if not username or not password:
        return jsonify({'status': 'error', 'message': '请输入用户名和密码'})
    
    db = get_db_connection()
    user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    db.close()
    
    if user is None:
        return jsonify({'status': 'error', 'message': '用户不存在'})
    elif user['password'] != password:
        return jsonify({'status': 'error', 'message': '密码错误'})
    else:
        session['username'] = user['username']
        return jsonify({'status': 'success', 'message': '登录成功', 'redirect': '/game'})

@app.route('/api/k2_register', methods=['POST'])
def k2_register():
    """K2 按键：执行注册操作（从表单获取用户名密码）"""
    username = request.form.get('username')
    password = request.form.get('password')
    
    if not username or not password:
        return jsonify({'status': 'error', 'message': '请输入用户名和密码'})
    
    db = get_db_connection()
    try:
        db.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        db.commit()
        db.close()
        return jsonify({'status': 'success', 'message': '注册成功'})
    except sqlite3.IntegrityError:
        db.close()
        return jsonify({'status': 'error', 'message': '用户名已存在'})

if __name__ == '__main__':
    # 启动前初始化数据库
    if not os.path.exists(DB_NAME):
        init_db()
    else:
        # 即使数据库存在，也确保表结构正确（可选）
        init_db()
        
    app.run(debug=True, port=5000)