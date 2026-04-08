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


def test_build_prompt_empty_job_description(service):
    """测试空职位描述的处理"""
    prompt = service._build_prompt(
        position_name="工程师",
        job_description="",
        interviewer_role="业务领导1",
        role_description="直属领导",
        question_count=3,
        round_number=1,
        previous_questions=[]
    )
    assert "工程师" in prompt
    assert prompt  # 确保 prompt 不为空


def test_build_prompt_with_empty_role_description(service):
    """测试空角色描述的处理"""
    prompt = service._build_prompt(
        position_name="后端工程师",
        job_description="熟悉 Python",
        interviewer_role="HR",
        role_description="",
        question_count=3,
        round_number=1,
        previous_questions=[]
    )
    assert "后端工程师" in prompt
    assert "HR" in prompt
    assert "面试官" in prompt  # 默认使用 "面试官" 当 role_description 为空


def test_validate_questions_with_invalid_category(service):
    """测试无效的 category 被纠正为默认值"""
    raw = [
        {"question_text": "测试问题", "category": "无效分类", "difficulty": "中等"},
        {"question_text": "测试问题2", "category": "技术", "difficulty": "简单"}
    ]
    result = service._validate_questions(raw)
    assert len(result) == 2
    assert result[0]["category"] == "技术"  # 无效分类被纠正为默认


def test_validate_questions_with_invalid_difficulty(service):
    """测试无效的 difficulty 被纠正为默认值"""
    raw = [
        {"question_text": "测试问题", "category": "技术", "difficulty": "超难"},
    ]
    result = service._validate_questions(raw)
    assert len(result) == 1
    assert result[0]["difficulty"] == "中等"  # 无效难度被纠正为默认


def test_validate_questions_with_non_list_key_points(service):
    """测试 expected_key_points 不是列表时的处理"""
    raw = [
        {"question_text": "测试问题", "category": "技术", "expected_key_points": "应该是数组"},
    ]
    result = service._validate_questions(raw)
    assert len(result) == 1
    assert result[0]["expected_key_points"] == []  # 转换为空数组


def test_parse_response_with_markdown_code_block(service):
    """测试解析带 markdown 代码块的响应"""
    content = '''
    以下是生成的问题：
    ```json
    [{"question_text": "问题1", "category": "技术", "difficulty": "中等"}]
    ```
    请确认
    '''
    result = service._parse_response(content)
    assert len(result) == 1
    assert result[0]["question_text"] == "问题1"


def test_parse_response_with_multiple_json_blocks(service):
    """测试解析多个 JSON 块时的处理（应取第一个）"""
    content = '''[{"question_text": "第一个"}, {"question_text": "第二个"}]'''
    result = service._parse_response(content)
    assert len(result) == 2


def test_get_fallback_questions_unknown_role(service):
    """测试未知角色使用默认问题池"""
    questions = service._get_fallback_questions("未知角色", 3)
    assert len(questions) == 3
    # 应使用默认的"业务领导1"问题池
    assert questions[0]["question_text"]


def test_get_fallback_questions_count_less_than_pool(service):
    """测试请求数量少于问题池大小"""
    questions = service._get_fallback_questions("HR", 2)
    assert len(questions) == 2


@pytest.mark.asyncio
async def test_generate_questions_with_timeout(service):
    """测试 LLM 超时时的降级处理"""
    import httpx
    with patch.object(service, '_call_llm', new_callable=AsyncMock, side_effect=httpx.TimeoutException("Request timeout")):
        questions = await service.generate_questions(
            position_name="工程师",
            job_description="Python",
            interviewer_role="业务领导1",
            role_description="领导",
            question_count=3,
            round_number=1,
            previous_questions=[]
        )
    assert len(questions) >= 3
    assert questions[0]["question_text"]  # 确保有内容


@pytest.mark.asyncio
async def test_generate_questions_with_empty_response(service):
    """测试 LLM 返回空数组时的降级处理"""
    with patch.object(service, '_call_llm', new_callable=AsyncMock, return_value="[]"):
        questions = await service.generate_questions(
            position_name="工程师",
            job_description="Python",
            interviewer_role="业务领导1",
            role_description="领导",
            question_count=3,
            round_number=1,
            previous_questions=[]
        )
    assert len(questions) >= 3  # 应该用后备问题补充


def test_build_prompt_with_long_previous_questions(service):
    """测试大量历史问题时的处理"""
    previous = [f"问题{i}" for i in range(20)]
    prompt = service._build_prompt(
        position_name="工程师",
        job_description="Python",
        interviewer_role="业务领导1",
        role_description="领导",
        question_count=3,
        round_number=1,
        previous_questions=previous
    )
    assert "问题0" in prompt
    assert "问题19" in prompt
