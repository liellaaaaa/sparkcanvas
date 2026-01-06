"""
测试通义千问 API 连接
用于诊断网络连接问题
"""
import dashscope
from core.config import load_config

def test_dashscope_connection():
    """测试通义千问 API 连接"""
    cfg = load_config()
    
    if not cfg.dashscope_api_key:
        print("❌ 错误: 未配置 DASHSCOPE_API_KEY")
        print("请在 config.yaml 或 .env 文件中配置 dashscope.api_key")
        return
    
    print(f"✓ API Key 已配置: {cfg.dashscope_api_key[:10]}...")
    print(f"✓ 模型: {cfg.dashscope_model}")
    print(f"✓ 温度: {cfg.dashscope_temperature}")
    print()
    
    # 设置 API Key
    dashscope.api_key = cfg.dashscope_api_key
    
    # 测试简单调用
    print("正在测试通义千问 API 连接...")
    print("=" * 60)
    
    try:
        from dashscope import Generation
        
        response = Generation.call(
            model=cfg.dashscope_model,
            messages=[
                {"role": "system", "content": "你是一个测试助手"},
                {"role": "user", "content": "请说'测试成功'"}
            ],
            temperature=0.7,
            result_format="message",
        )
        
        if response.status_code == 200:
            content = response.output.choices[0].message.content
            print("✅ 连接成功!")
            print(f"响应内容: {content}")
            print()
            print("通义千问 API 工作正常 ✨")
        else:
            print(f"❌ API 调用失败")
            print(f"错误码: {response.code}")
            print(f"错误信息: {response.message}")
            
    except ConnectionError as e:
        print(f"❌ 网络连接错误: {e}")
        print()
        print("可能的原因:")
        print("1. 网络不稳定")
        print("2. 防火墙阻止了连接")
        print("3. DNS 解析失败")
        print()
        print("建议:")
        print("- 检查网络连接")
        print("- 尝试使用代理")
        print("- 检查防火墙设置")
        
    except Exception as e:
        print(f"❌ 未知错误: {type(e).__name__}: {e}")
        print()
        print("请检查:")
        print("1. API Key 是否正确")
        print("2. 是否有足够的调用额度")
        print("3. 网络是否正常")

if __name__ == "__main__":
    print("=" * 60)
    print("通义千问 API 连接测试")
    print("=" * 60)
    print()
    
    test_dashscope_connection()

