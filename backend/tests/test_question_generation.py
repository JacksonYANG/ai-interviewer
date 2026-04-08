import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.question_generation_service import QuestionGenerationService, FALLBACK_QUESTIONS
from app.schemas.interview import LLMConfig


@pytest.fixture
def llm_config():
    return LLMConfig(
        provider="openai",
        api_key="test-key-1234567890",
        model_name="qwen3.5-plus",
        base_url="https://www.dmxapi.cn/v1/chat/completions",
        temperature=0.8,
        max_tokens=3000
    )


@pytest.fixture
def service(llm_config):
    return QuestionGenerationService(llm_config)


def test_fallback_questions_defined():
    """验证后备问题池已定义"""
    assert "业务领导1" in FALLBACK_QUESTIONS
    assert "HR" in FALLBACK_QUESTIONS
    for role, questions in FALLBACK_QUESTIONS.items():
        assert len(questions) >= 2
        for q in questions:
            assert "question_text" in q
            assert "category" in q


def test_build_prompt_contains_position(service):
    """验证 Prompt 包含职位信息"""
    prompt = service._build_prompt(
        position_name="后端工程师",
        job_description="熟悉 Python、FastAPI",
        interviewer_role="业务领导1",
        role_description="直属领导",
        question_count=6,
        round_number=1,
        previous_questions=[]
    )
    assert "后端工程师" in prompt
    assert "Python" in prompt
    assert "6" in prompt


def test_build_prompt_includes_previous_questions(service):
    """验证 Prompt 包含已问问题（避免重复）"""
    prompt = service._build_prompt(
        position_name="后端工程师",
        job_description="熟悉 Python",
        interviewer_role="业务领导2",
        role_description="同组领导",
        question_count=5,
        round_number=2,
        previous_questions=["请介绍一下你自己", "你的优势是什么"]
    )
    assert "请介绍一下你自己" in prompt
    assert "你的优势是什么" in prompt


def test_parse_response_valid_json(service):
    """验证解析合法 JSON 响应"""
    content = json.dumps([
        {"question_text": "问题1", "category": "技术", "difficulty": "中等", "expected_key_points": ["要点1"]},
        {"question_text": "问题2", "category": "行为", "difficulty": "简单", "expected_key_points": []}
    ])
    result = service._parse_response(content)
    assert len(result) == 2
    assert result[0]["question_text"] == "问题1"


def test_parse_response_json_in_code_block(service):
    """验证解析代码块中的 JSON"""
    content = '```json\n[{"question_text": "问题1", "category": "技术", "difficulty": "中等"}]\n```'
    result = service._parse_response(content)
    assert len(result) == 1
    assert result[0]["question_text"] == "问题1"


def test_parse_response_invalid_returns_empty(service):
    """验证无效响应返回空列表"""
    result = service._parse_response("这不是JSON")
    assert result == []


def test_validate_questions_filters_invalid(service):
    """验证问题验证过滤无效条目"""
    raw = [
        {"question_text": "有效问题", "category": "技术"},
        {"no_text": "缺少 question_text"},
        {"question_text": "另一有效问题", "category": "行为", "difficulty": "困难"}
    ]
    result = service._validate_questions(raw)
    assert len(result) == 2
    assert result[0]["question_text"] == "有效问题"


@pytest.mark.asyncio
async def test_generate_questions_success(service):
    """测试正常生成问题"""
    mock_llm_response = json.dumps([
        {"question_text": "请介绍你负责的项目", "category": "技术", "difficulty": "简单", "expected_key_points": ["项目背景", "技术栈"]},
        {"question_text": "最大的技术挑战是什么", "category": "技术", "difficulty": "中等", "expected_key_points": ["问题描述", "解决方案"]}
    ])

    with patch.object(service, '_call_llm', new_callable=AsyncMock, return_value=mock_llm_response):
        questions = await service.generate_questions(
            position_name="后端工程师",
            job_description="熟悉 Python",
            interviewer_role="业务领导1",
            role_description="直属领导",
            question_count=2,
            round_number=1,
            previous_questions=[]
        )

    assert len(questions) == 2
    assert questions[0]["question_text"] == "请介绍你负责的项目"


@pytest.mark.asyncio
async def test_generate_questions_llm_failure_uses_fallback(service):
    """测试 LLM 失败时使用后备问题"""
    with patch.object(service, '_call_llm', new_callable=AsyncMock, side_effect=Exception("API Error")):
        questions = await service.generate_questions(
            position_name="后端工程师",
            job_description="熟悉 Python",
            interviewer_role="业务领导1",
            role_description="直属领导",
            question_count=3,
            round_number=1,
            previous_questions=[]
        )

    assert len(questions) >= 3
    assert questions[0]["question_text"]


@pytest.mark.asyncio
async def test_generate_questions_insufficient_fills_from_fallback(service):
    """测试 LLM 返回数量不足时用后备问题补充"""
    mock_response = json.dumps([
        {"question_text": "只有一个问题", "category": "技术", "difficulty": "简单"}
    ])

    with patch.object(service, '_call_llm', new_callable=AsyncMock, return_value=mock_response):
        questions = await service.generate_questions(
            position_name="后端工程师",
            job_description="熟悉 Python",
            interviewer_role="业务领导1",
            role_description="直属领导",
            question_count=5,
            round_number=1,
            previous_questions=[]
        )

    assert len(questions) == 5
