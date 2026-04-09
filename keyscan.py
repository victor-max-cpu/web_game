"""
按键扫描模块 (keyscan.py)
模拟单片机按键输入逻辑，支持字符输入和确认按键（K1登录，K2注册）
"""

import threading
import time

class KeyScanner:
    def __init__(self):
        self.input_buffer = ""
        self.lock = threading.Lock()
        self.last_action = None  # 记录最后一次操作：'login', 'register', 或 None
        self.running = False
        self.thread = None

    def add_char(self, char):
        """添加字符到输入缓冲区"""
        with self.lock:
            self.input_buffer += char
            print(f"[KeyScan] 输入字符: {char}, 当前缓冲区: {self.input_buffer}")

    def clear_buffer(self):
        """清空输入缓冲区"""
        with self.lock:
            self.input_buffer = ""
            self.last_action = None
            print("[KeyScan] 缓冲区已清空")

    def get_input(self):
        """获取当前输入内容"""
        with self.lock:
            return self.input_buffer

    def press_k1_login(self):
        """模拟按下 K1 键执行登录"""
        with self.lock:
            self.last_action = 'login'
            print(f"[KeyScan] K1 按下 - 准备登录，用户名/密码: {self.input_buffer}")
            return self.input_buffer

    def press_k2_register(self):
        """模拟按下 K2 键执行注册"""
        with self.lock:
            self.last_action = 'register'
            print(f"[KeyScan] K2 按下 - 准备注册，用户名/密码: {self.input_buffer}")
            return self.input_buffer

    def get_last_action(self):
        """获取并清除最后一次操作"""
        with self.lock:
            action = self.last_action
            # 获取后不立即清除，由主程序处理完后调用 clear_buffer
            return action

# 全局实例
scanner = KeyScanner()

def simulate_key_input(char_sequence, action_key=None):
    """
    测试辅助函数：模拟一系列按键输入
    :param char_sequence: 字符序列字符串
    :param action_key: 'k1' 或 'k2'
    """
    for char in char_sequence:
        scanner.add_char(char)
        time.sleep(0.1)
    
    if action_key == 'k1':
        return scanner.press_k1_login()
    elif action_key == 'k2':
        return scanner.press_k2_register()
    return scanner.get_input()

if __name__ == "__main__":
    # 简单测试
    print("=== 按键模块测试 ===")
    simulate_key_input("victor", "k1")
    print(f"最后操作: {scanner.get_last_action()}")
    scanner.clear_buffer()
