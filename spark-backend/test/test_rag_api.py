"""
RAG知识库API测试脚本

使用方法:
1. 确保Redis服务已启动
2. 确保后端服务已启动 (python main.py)
3. 确保DashScope API Key已配置
4. 运行此脚本: python test_rag_api.py
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
TEST_USERNAME = "xcxc"

# 日志文件路径
LOG_FILE = Path(__file__).parent / "test_rag_api_output.log"


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


class RAGAPITester:
    """RAG知识库API测试类"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.token: Optional[str] = None
        self.user_id: Optional[int] = None
        self.uploaded_document_ids: list = []
    
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
    
    def upload_document(self, file_path: str) -> Optional[str]:
        """上传文档"""
        print(f"📤 上传文档: {file_path}")
        
        if not self.token:
            print("❌ 未登录")
            return None
        
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (Path(file_path).name, f, 'application/octet-stream')}
                response = requests.post(
                    f"{self.base_url}/api/v1/rag/upload",
                    headers={"Authorization": f"Bearer {self.token}"},
                    files=files,
                    timeout=60  # 上传可能需要较长时间
                )
            
            self.print_response("上传文档", response)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 200:
                    document_id = data["data"]["document_id"]
                    self.uploaded_document_ids.append(document_id)
                    print(f"✅ 文档上传成功! Document ID: {document_id}")
                    return document_id
        except FileNotFoundError:
            print(f"❌ 文件不存在: {file_path}")
        except Exception as e:
            print(f"❌ 上传文档异常: {e}")
        
        return None
    
    def create_test_file(self, content: str = "这是一个测试文档。\n\n用于测试RAG知识库的文档上传和检索功能。\n\n包含一些测试内容，用于验证语义检索是否正常工作。") -> str:
        """创建测试文件"""
        test_file = Path(__file__).parent / "test_document.txt"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(content)
        return str(test_file)
    
    def list_documents(self, page: int = 1, page_size: int = 20):
        """查询文档列表"""
        print(f"📋 查询文档列表 (page={page}, page_size={page_size})...")
        
        if not self.token:
            print("❌ 未登录")
            return False
        
        try:
            params = {
                "page": page,
                "page_size": page_size
            }
            
            response = requests.get(
                f"{self.base_url}/api/v1/rag/list",
                headers={"Authorization": f"Bearer {self.token}"},
                params=params,
                timeout=10
            )
            
            self.print_response("查询文档列表", response)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 200:
                    list_data = data["data"]
                    print(f"✅ 查询成功! 共 {list_data.get('total', 0)} 个文档")
                    return True
        except Exception as e:
            print(f"❌ 查询文档列表异常: {e}")
        
        return False
    
    def search_documents(self, query: str, top_k: int = 5):
        """语义检索"""
        print(f"🔍 语义检索 (query={query}, top_k={top_k})...")
        
        if not self.token:
            print("❌ 未登录")
            return False
        
        try:
            payload = {
                "query": query,
                "top_k": top_k
            }
            
            response = requests.post(
                f"{self.base_url}/api/v1/rag/search",
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=30
            )
            
            self.print_response("语义检索", response)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 200:
                    search_data = data["data"]
                    print(f"✅ 检索成功! 找到 {len(search_data.get('results', []))} 条结果")
                    return True
        except Exception as e:
            print(f"❌ 语义检索异常: {e}")
        
        return False
    
    def delete_document(self, document_id: str):
        """删除文档"""
        print(f"🗑️ 删除文档: {document_id}")
        
        if not self.token:
            print("❌ 未登录")
            return False
        
        try:
            payload = {
                "document_id": document_id
            }
            
            response = requests.delete(
                f"{self.base_url}/api/v1/rag/delete",
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=10
            )
            
            self.print_response("删除文档", response)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 200:
                    print(f"✅ 文档删除成功!")
                    return True
        except Exception as e:
            print(f"❌ 删除文档异常: {e}")
        
        return False
    
    def run_full_test(self):
        """运行完整测试流程"""
        print("\n" + "="*60)
        print("🚀 开始RAG知识库API完整测试")
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
        
        # 3. 创建测试文件
        print("\n" + "-"*60)
        print("测试步骤 1: 创建测试文档")
        print("-"*60)
        test_file = self.create_test_file()
        print(f"✅ 测试文件已创建: {test_file}")
        
        # 4. 上传文档
        print("\n" + "-"*60)
        print("测试步骤 2: 上传文档")
        print("-"*60)
        document_id = self.upload_document(test_file)
        if not document_id:
            print("⚠️ 上传文档失败，但继续测试...")
        
        # 等待一下，确保数据已保存
        import time
        time.sleep(2)
        
        # 5. 查询文档列表
        print("\n" + "-"*60)
        print("测试步骤 3: 查询文档列表")
        print("-"*60)
        self.list_documents()
        
        # 6. 语义检索
        print("\n" + "-"*60)
        print("测试步骤 4: 语义检索（关键词：测试）")
        print("-"*60)
        self.search_documents("测试", top_k=5)
        
        # 7. 语义检索（其他关键词）
        print("\n" + "-"*60)
        print("测试步骤 5: 语义检索（关键词：RAG）")
        print("-"*60)
        self.search_documents("RAG", top_k=5)
        
        # 8. 测试分页
        print("\n" + "-"*60)
        print("测试步骤 6: 测试分页功能（第1页，每页1条）")
        print("-"*60)
        self.list_documents(page=1, page_size=1)
        
        # 9. 删除文档（如果上传成功）
        if document_id:
            print("\n" + "-"*60)
            print("测试步骤 7: 删除文档")
            print("-"*60)
            self.delete_document(document_id)
            
            # 等待一下，确保数据已删除
            time.sleep(1)
            
            # 再次查询列表，确认已删除
            print("\n" + "-"*60)
            print("测试步骤 8: 验证文档已删除")
            print("-"*60)
            self.list_documents()
        
        # 清理测试文件
        try:
            if Path(test_file).exists():
                Path(test_file).unlink()
                print(f"\n🧹 已清理测试文件: {test_file}")
        except:
            pass
        
        print("\n" + "="*60)
        print("✅ 测试完成!")
        print("="*60 + "\n")


if __name__ == "__main__":
    # 设置输出重定向，同时输出到终端和日志文件
    tee = TeeOutput(LOG_FILE)
    sys.stdout = tee
    
    try:
        tester = RAGAPITester()
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

