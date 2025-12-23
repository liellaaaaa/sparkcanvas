"""
历史记录API测试脚本

使用方法:
1. 确保Redis服务已启动
2. 确保后端服务已启动 (python main.py)
3. 运行此脚本: python test_history_api.py
"""
import requests
import json
import sys
from typing import Optional
from datetime import datetime
from pathlib import Path

# 配置
BASE_URL = "http://localhost:8000"
TEST_EMAIL = "1337706441@qq.com"
TEST_PASSWORD = "111111"
TEST_USERNAME = "xcxcr"

# 日志文件路径
LOG_FILE = Path(__file__).parent / "test_history_api_output.log"


class TeeOutput:
    """同时输出到终端和文件的类"""
    
    def __init__(self, log_file: Path):
        self.terminal = sys.stdout
        self.log_file = open(log_file, 'a', encoding='utf-8')
        # 写入测试开始标记
        self.log_file.write(f"\n{'='*80}\n")
        self.log_file.write(f"测试开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        self.log_file.write(f"{'='*80}\n")
        self.log_file.flush()
    
    def write(self, message):
        """写入消息到终端和文件"""
        self.terminal.write(message)
        self.log_file.write(message)
        self.log_file.flush()
    
    def flush(self):
        """刷新缓冲区"""
        self.terminal.flush()
        self.log_file.flush()
    
    def close(self):
        """关闭文件"""
        if self.log_file:
            self.log_file.write(f"\n{'='*80}\n")
            self.log_file.write(f"测试结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            self.log_file.write(f"{'='*80}\n\n")
            self.log_file.close()

class HistoryAPITester:
    """历史记录API测试类"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.token: Optional[str] = None
        self.user_id: Optional[int] = None
        self.session_id: Optional[str] = None
    
    def print_response(self, title: str, response: requests.Response):
        """打印响应结果"""
        print(f"\n{'='*60}")
        print(f"{title}")
        print(f"{'='*60}")
        print(f"状态码: {response.status_code}")
        try:
            data = response.json()
            print(f"响应内容:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        except:
            print(f"响应文本: {response.text}")
        print(f"{'='*60}\n")
    
    def test_health(self) -> bool:
        """测试健康检查"""
        print("🔍 测试健康检查...")
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            self.print_response("健康检查", response)
            return response.status_code == 200
        except Exception as e:
            print(f"❌ 健康检查失败: {e}")
            print("请确保后端服务已启动 (python main.py)")
            return False
    
    def login(self) -> bool:
        """登录获取Token"""
        print("🔐 尝试登录...")
        
        # 先尝试登录
        login_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json=login_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                # 登录接口返回格式: {"user": {...}, "token": "..."}
                if "token" in data:
                    self.token = data["token"]
                    self.user_id = data["user"]["id"]
                    print(f"✅ 登录成功! User ID: {self.user_id}")
                    return True
                else:
                    print(f"⚠️ 登录失败: {data}")
            else:
                print(f"⚠️ 登录失败，状态码: {response.status_code}")
                print(f"响应: {response.text}")
        except Exception as e:
            print(f"❌ 登录请求异常: {e}")
        
        # 如果登录失败，尝试注册
        print("\n📝 登录失败，尝试注册新用户...")
        return self.register()
    
    def register(self) -> bool:
        """注册新用户"""
        print("📝 注册新用户...")
        
        # 1. 发送验证码
        print("  1. 发送验证码...")
        try:
            code_response = requests.get(
                f"{self.base_url}/auth/code",
                params={"email": TEST_EMAIL},
                timeout=10
            )
            if code_response.status_code != 200:
                print(f"   ⚠️ 发送验证码失败: {code_response.text}")
                print("   💡 提示: 如果邮箱服务未配置，可以手动查看数据库中的验证码")
        except Exception as e:
            print(f"   ⚠️ 发送验证码异常: {e}")
        
        # 2. 注册（使用默认验证码，实际应该从邮箱或数据库获取）
        print("  2. 注册用户...")
        register_data = {
            "email": TEST_EMAIL,
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD,
            "confirm_password": TEST_PASSWORD,
            "code": "1234"  # 默认验证码，实际应从邮箱获取
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/auth/register",
                json=register_data,
                timeout=10
            )
            
            if response.status_code == 200:
                # 注册成功，尝试登录
                print("   ✅ 注册成功，尝试登录...")
                return self.login()  # 注册后自动登录
            else:
                print(f"   ⚠️ 注册失败，状态码: {response.status_code}")
                print(f"   响应: {response.text}")
                # 如果是因为验证码错误，提示用户
                if "验证码" in response.text:
                    print("   💡 提示: 验证码错误，请检查邮箱或数据库中的验证码")
                    print("   💡 可以手动从数据库查询验证码，或使用已存在的用户登录")
        except Exception as e:
            print(f"   ❌ 注册请求异常: {e}")
        
        return False
    
    def create_session(self) -> bool:
        """创建工作会话"""
        print("📋 创建工作会话...")
        
        if not self.token:
            print("❌ 未登录，无法创建会话")
            return False
        
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/workspace/create-session",
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=10
            )
            
            self.print_response("创建会话", response)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 200:
                    self.session_id = data["data"]["session_id"]
                    print(f"✅ 会话创建成功! Session ID: {self.session_id}")
                    return True
        except Exception as e:
            print(f"❌ 创建会话异常: {e}")
        
        return False
    
    def send_message(self, message: str = "帮我写一篇关于旅行的文章") -> bool:
        """发送消息（会自动保存历史记录）"""
        print(f"💬 发送消息: {message}")
        
        if not self.token or not self.session_id:
            print("❌ 未登录或未创建会话")
            return False
        
        try:
            payload = {
                "session_id": self.session_id,
                "message": message,
                "material_source": "online",
                "platform": "xiaohongshu"
            }
            
            response = requests.post(
                f"{self.base_url}/api/v1/workspace/send-message",
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=30
            )
            
            self.print_response("发送消息", response)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 200:
                    print("✅ 消息发送成功，历史记录已自动保存")
                    return True
        except Exception as e:
            print(f"❌ 发送消息异常: {e}")
        
        return False
    
    def get_conversation_history(self, session_id: Optional[str] = None, page: int = 1, page_size: int = 20):
        """查询对话历史记录"""
        print(f"📚 查询对话历史记录 (session_id={session_id}, page={page}, page_size={page_size})...")
        
        if not self.token:
            print("❌ 未登录")
            return False
        
        try:
            params = {
                "page": page,
                "page_size": page_size
            }
            if session_id:
                params["session_id"] = session_id
            
            response = requests.get(
                f"{self.base_url}/api/v1/history/conversations",
                headers={"Authorization": f"Bearer {self.token}"},
                params=params,
                timeout=10
            )
            
            self.print_response("查询对话历史记录", response)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 200:
                    history_data = data["data"]
                    print(f"✅ 查询成功! 共 {history_data.get('total', 0)} 条记录")
                    return True
        except Exception as e:
            print(f"❌ 查询历史记录异常: {e}")
        
        return False
    
    def search_history(self, keyword: str, page: int = 1, page_size: int = 20):
        """搜索历史记录"""
        print(f"🔍 搜索历史记录 (keyword={keyword}, page={page}, page_size={page_size})...")
        
        if not self.token:
            print("❌ 未登录")
            return False
        
        try:
            params = {
                "keyword": keyword,
                "page": page,
                "page_size": page_size
            }
            
            response = requests.get(
                f"{self.base_url}/api/v1/history/search",
                headers={"Authorization": f"Bearer {self.token}"},
                params=params,
                timeout=10
            )
            
            self.print_response("搜索历史记录", response)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 200:
                    history_data = data["data"]
                    print(f"✅ 搜索成功! 共找到 {history_data.get('total', 0)} 条匹配记录")
                    return True
        except Exception as e:
            print(f"❌ 搜索历史记录异常: {e}")
        
        return False
    
    def run_full_test(self):
        """运行完整测试流程"""
        print("\n" + "="*60)
        print("🚀 开始历史记录API完整测试")
        print("="*60 + "\n")
        
        # 1. 健康检查
        if not self.test_health():
            print("❌ 后端服务未启动，请先运行: python main.py")
            return
        
        # 2. 登录
        if not self.login():
            print("❌ 登录失败，无法继续测试")
            print("💡 提示: 请检查数据库连接和用户数据")
            return
        
        # 3. 创建会话
        if not self.create_session():
            print("❌ 创建会话失败")
            return
        
        # 4. 发送第一条消息
        print("\n" + "-"*60)
        print("测试步骤 1: 发送第一条消息")
        print("-"*60)
        if not self.send_message("帮我写一篇关于Python编程的文章"):
            print("⚠️ 发送消息失败，但继续测试...")
        
        # 等待一下，确保数据已保存
        import time
        time.sleep(1)
        
        # 5. 发送第二条消息
        print("\n" + "-"*60)
        print("测试步骤 2: 发送第二条消息")
        print("-"*60)
        if not self.send_message("帮我写一篇关于旅行的文章"):
            print("⚠️ 发送消息失败，但继续测试...")
        
        time.sleep(1)
        
        # 6. 查询所有历史记录
        print("\n" + "-"*60)
        print("测试步骤 3: 查询所有历史记录")
        print("-"*60)
        self.get_conversation_history()
        
        # 7. 按会话ID查询
        print("\n" + "-"*60)
        print("测试步骤 4: 按会话ID查询历史记录")
        print("-"*60)
        if self.session_id:
            self.get_conversation_history(session_id=self.session_id)
        
        # 8. 搜索历史记录
        print("\n" + "-"*60)
        print("测试步骤 5: 搜索历史记录（关键词：旅行）")
        print("-"*60)
        self.search_history("旅行")
        
        # 9. 搜索历史记录（关键词：Python）
        print("\n" + "-"*60)
        print("测试步骤 6: 搜索历史记录（关键词：Python）")
        print("-"*60)
        self.search_history("Python")
        
        # 10. 测试分页
        print("\n" + "-"*60)
        print("测试步骤 7: 测试分页功能（第1页，每页1条）")
        print("-"*60)
        self.get_conversation_history(page=1, page_size=1)
        
        print("\n" + "="*60)
        print("✅ 测试完成!")
        print("="*60 + "\n")


if __name__ == "__main__":
    # 设置输出重定向，同时输出到终端和日志文件
    tee = TeeOutput(LOG_FILE)
    sys.stdout = tee
    
    try:
        tester = HistoryAPITester()
        tester.run_full_test()
    except KeyboardInterrupt:
        print("\n\n⚠️ 测试被用户中断")
    except Exception as e:
        print(f"\n\n❌ 测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 恢复标准输出
        sys.stdout = tee.terminal
        tee.close()
        print(f"\n📝 测试日志已保存到: {LOG_FILE}")

