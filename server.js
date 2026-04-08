const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 3000;

// 中间件
app.use(cors());
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, 'public')));

// 用户数据文件路径
const USERS_FILE = path.join(__dirname, 'data', 'users.json');

// 确保数据目录存在
if (!fs.existsSync(path.join(__dirname, 'data'))) {
    fs.mkdirSync(path.join(__dirname, 'data'), { recursive: true });
}

// 初始化用户文件
if (!fs.existsSync(USERS_FILE)) {
    fs.writeFileSync(USERS_FILE, JSON.stringify([]));
}

// 读取用户数据
function readUsers() {
    const data = fs.readFileSync(USERS_FILE, 'utf8');
    return JSON.parse(data);
}

// 写入用户数据
function writeUsers(users) {
    fs.writeFileSync(USERS_FILE, JSON.stringify(users, null, 2));
}

// 注册接口
app.post('/api/register', (req, res) => {
    const { username, password } = req.body;

    if (!username || !password) {
        return res.status(400).json({ success: false, message: '用户名和密码不能为空' });
    }

    const users = readUsers();
    
    // 检查用户名是否已存在
    const userExists = users.find(u => u.username === username);
    if (userExists) {
        return res.status(400).json({ success: false, message: '用户名已存在，请选择其他用户名' });
    }

    // 创建新用户
    const newUser = {
        id: Date.now(),
        username,
        password, // 实际项目中应该加密存储
        createdAt: new Date().toISOString()
    };

    users.push(newUser);
    writeUsers(users);

    res.json({ success: true, message: '注册成功', user: { username: newUser.username } });
});

// 登录接口
app.post('/api/login', (req, res) => {
    const { username, password } = req.body;

    if (!username || !password) {
        return res.status(400).json({ success: false, message: '用户名和密码不能为空' });
    }

    const users = readUsers();
    const user = users.find(u => u.username === username && u.password === password);

    if (!user) {
        return res.status(401).json({ success: false, message: '用户名或密码错误' });
    }

    res.json({ 
        success: true, 
        message: '登录成功', 
        user: { username: user.username },
        token: 'mock-token-' + user.id // 模拟token
    });
});

// 获取当前用户信息
app.get('/api/user', (req, res) => {
    const token = req.headers.authorization;
    
    if (!token) {
        return res.status(401).json({ success: false, message: '未登录' });
    }

    const userId = parseInt(token.replace('mock-token-', ''));
    const users = readUsers();
    const user = users.find(u => u.id === userId);

    if (!user) {
        return res.status(404).json({ success: false, message: '用户不存在' });
    }

    res.json({ success: true, user: { username: user.username } });
});

app.listen(PORT, () => {
    console.log(`服务器运行在 http://localhost:${PORT}`);
});
