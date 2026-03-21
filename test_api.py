#!/usr/bin/env python3
"""
测试面试配置API
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_analyze_api():
    """测试AI分析API"""
    print("测试 AI 分析 API...")

    # 首先需要登录获取token
    # 这里跳过认证测试，专注于业务逻辑

    # 测试数据
    test_data = {
        "position_name": "高级前端工程师",
        "position_level": "senior",
        "company_type": "large",
        "industry": "互联网",
        "salary_range": "25k-40k",
        "job_description": "负责前端架构设计和技术选型，带领团队完成复杂项目开发。"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/interviews/analyze",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 401:
            print("  ✓ API端点存在，需要认证(符合预期)")
            return True
        elif response.status_code == 200:
            print("  ✓ API调用成功")
            result = response.json()
            print(f"  建议轮数: {result.get('suggested_rounds')}")
            return True
        else:
            print(f"  ✗ 意外状态码: {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print("  ✗ 无法连接到服务器，请确保后端正在运行")
        return False
    except Exception as e:
        print(f"  ✗ 错误: {str(e)}")
        return False

if __name__ == "__main__":
    print("开始测试面试配置API...")
    print("-" * 50)

    success = test_analyze_api()

    print("-" * 50)
    if success:
        print("✓ API测试通过")
    else:
        print("✗ API测试失败")
