#!/usr/bin/env python3
"""
测试面试执行功能
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai-interviewer-backend'))

def test_imports():
    """测试导入是否正常"""
    try:
        from app.api.v1.interviews import router
        from app.schemas.interview import (
            InterviewSessionCreate,
            InterviewSessionResponse,
            QuestionResponse,
            AnswerSubmit,
            AnswerResponse,
            SessionCompleteRequest,
            SessionCompleteResponse,
        )
        print("✓ 所有导入成功")
        return True
    except Exception as e:
        print(f"✗ 导入失败: {e}")
        return False

def test_schemas():
    """测试 Schema 定义"""
    try:
        from app.schemas.interview import InterviewSessionCreate

        # 测试创建会话请求
        session_data = InterviewSessionCreate(
            config_id=1,
            round_id=1
        )
        assert session_data.config_id == 1
        assert session_data.round_id == 1
        print("✓ InterviewSessionCreate schema 测试通过")

        # 测试答案提交请求
        from app.schemas.interview import AnswerSubmit
        from datetime import datetime

        answer_data = AnswerSubmit(
            question_id=1,
            text_answer="这是测试答案"
        )
        assert answer_data.question_id == 1
        assert answer_data.text_answer == "这是测试答案"
        print("✓ AnswerSubmit schema 测试通过")

        return True
    except Exception as e:
        print(f"✗ Schema 测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("面试执行功能测试")
    print("=" * 50)

    tests = [
        ("导入测试", test_imports),
        ("Schema 测试", test_schemas),
    ]

    results = []
    for name, test_func in tests:
        print(f"\n{name}:")
        result = test_func()
        results.append(result)

    print("\n" + "=" * 50)
    print(f"测试结果: {sum(results)}/{len(results)} 通过")
    print("=" * 50)

    return all(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
