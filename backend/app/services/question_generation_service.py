"""
问题生成服务 - 使用 LLM 生成面试问题

通过 dmxapi.cn (OpenAI 兼容) 调用 qwen3.5-plus 生成面试问题。
"""
import json
import re
import logging
from typing import List, Dict, Optional

import httpx

from app.schemas.interview import LLMConfig
from app.core.logger import get_logger

logger = get_logger(__name__)

# 后备问题池 - 当 LLM 调用失败时使用
FALLBACK_QUESTIONS = {
    "业务领导1": [
        {"question_text": "请介绍一下你最近负责的项目?", "category": "技术", "difficulty": "简单", "expected_key_points": ["项目背景", "技术栈", "职责"]},
        {"question_text": "项目中遇到的最大挑战是什么?如何解决的?", "category": "技术", "difficulty": "中等", "expected_key_points": ["问题描述", "分析过程", "解决方案"]},
        {"question_text": "请分享一次团队协作的成功经验", "category": "行为", "difficulty": "简单", "expected_key_points": ["协作场景", "角色", "成果"]},
        {"question_text": "你如何保证代码质量?", "category": "技术", "difficulty": "中等", "expected_key_points": ["代码审查", "测试策略", "CI/CD"]},
        {"question_text": "描述一次你主动优化系统性能的经历", "category": "技术", "difficulty": "困难", "expected_key_points": ["性能瓶颈", "优化方法", "量化结果"]},
        {"question_text": "你如何处理与同事的技术分歧?", "category": "行为", "difficulty": "中等", "expected_key_points": ["沟通方式", "妥协", "结果"]},
    ],
    "业务领导2": [
        {"question_text": "你的技术优势是什么?", "category": "技术", "difficulty": "简单", "expected_key_points": ["技术栈", "深度", "广度"]},
        {"question_text": "如何保证代码质量?", "category": "技术", "difficulty": "中等", "expected_key_points": ["代码审查", "自动化测试", "持续集成"]},
        {"question_text": "请描述一次系统设计的经验", "category": "技术", "difficulty": "困难", "expected_key_points": ["需求分析", "架构选择", "权衡"]},
        {"question_text": "你在团队中通常扮演什么角色?", "category": "行为", "difficulty": "简单", "expected_key_points": ["角色定位", "协作方式"]},
        {"question_text": "如何评估和引入新技术?", "category": "技术", "difficulty": "中等", "expected_key_points": ["调研方法", "风险评估", "落地策略"]},
        {"question_text": "分享一次你在压力下完成任务的经历", "category": "压力", "difficulty": "中等", "expected_key_points": ["压力来源", "应对方式", "结果"]},
    ],
    "部门总监": [
        {"question_text": "你的职业规划是什么?", "category": "行为", "difficulty": "中等", "expected_key_points": ["短期目标", "长期方向", "自我认知"]},
        {"question_text": "为什么离开现在的公司?", "category": "行为", "difficulty": "困难", "expected_key_points": ["离职原因", "正面表述", "期望"]},
        {"question_text": "你如何看待这个行业的未来发展趋势?", "category": "技术", "difficulty": "中等", "expected_key_points": ["行业理解", "趋势判断", "个人观点"]},
        {"question_text": "描述一次你做出重要技术决策的经历", "category": "技术", "difficulty": "困难", "expected_key_points": ["决策背景", "分析过程", "结果"]},
        {"question_text": "你如何平衡技术债务和新功能开发?", "category": "行为", "difficulty": "中等", "expected_key_points": ["优先级", "资源分配", "沟通"]},
        {"question_text": "如果你来带领一个团队，你会如何管理?", "category": "行为", "difficulty": "困难", "expected_key_points": ["管理理念", "团队建设", "目标"]},
    ],
    "CP面试官": [
        {"question_text": "你如何在跨部门项目中协调资源?", "category": "行为", "difficulty": "中等", "expected_key_points": ["协调方法", "沟通技巧", "结果"]},
        {"question_text": "分享一次你解决复杂问题的经历", "category": "技术", "difficulty": "中等", "expected_key_points": ["问题分析", "解决思路", "结果"]},
        {"question_text": "你对加班的看法是什么?", "category": "压力", "difficulty": "中等", "expected_key_points": ["工作态度", "效率", "平衡"]},
        {"question_text": "你最自豪的技术成就是什么?", "category": "技术", "difficulty": "简单", "expected_key_points": ["成就描述", "技术深度", "影响"]},
        {"question_text": "如何快速学习一门新技术?", "category": "技术", "difficulty": "简单", "expected_key_points": ["学习方法", "实践经验", "总结"]},
    ],
    "HR": [
        {"question_text": "你的期望薪资是多少?", "category": "压力", "difficulty": "困难", "expected_key_points": ["市场了解", "合理范围", "灵活性"]},
        {"question_text": "你还有什么问题想了解的?", "category": "压力", "difficulty": "中等", "expected_key_points": ["提问质量", "对岗位的关注"]},
        {"question_text": "你期望的工作环境是什么样的?", "category": "行为", "difficulty": "简单", "expected_key_points": ["文化匹配", "期望", "适应性"]},
        {"question_text": "你最快什么时候可以入职?", "category": "压力", "difficulty": "简单", "expected_key_points": ["时间安排", "交接"]},
        {"question_text": "除了我们公司，你还在看其他机会吗?", "category": "压力", "difficulty": "中等", "expected_key_points": ["诚实度", "表达方式"]},
    ],
}


class QuestionGenerationService:
    """问题生成服务

    使用 LLM 根据职位信息和面试官角色生成针对性的面试问题。
    通过 dmxapi.cn 调用 qwen3.5-plus（OpenAI 兼容格式）。
    """

    def __init__(self, config: LLMConfig):
        self.config = config
        self.client = httpx.AsyncClient(timeout=60.0)

    async def close(self):
        await self.client.aclose()

    def _build_prompt(
        self,
        position_name: str,
        job_description: str,
        interviewer_role: str,
        role_description: str,
        question_count: int,
        round_number: int,
        previous_questions: List[str]
    ) -> str:
        """构建问题生成 Prompt"""
        prev_section = ""
        if previous_questions:
            prev_list = "\n".join(f"  - {q}" for q in previous_questions)
            prev_section = f"""
## 已问过的题目（请勿重复）
{prev_list}
"""

        return f"""你是一位资深的面试专家，擅长根据职位信息和面试官角色生成针对性的面试问题。

## 职位信息
- 职位名称: {position_name}
- 职位描述: {job_description}
- 面试官角色: {interviewer_role}
- 角色说明: {role_description or '面试官'}
- 当前轮次: 第{round_number}轮

## 问题类型分布要求
- 技术问题: 考察专业能力和技术深度
- 行为问题: 考察软技能、团队协作、价值观
- 压力问题: 考察应变能力和心理素质

## 要求
1. 生成 {question_count} 个面试问题
2. 问题要针对 "{position_name}" 职位特点，不能太通用
3. 避免重复问题
4. 每题包含以下字段:
   - question_text: 问题内容（字符串）
   - category: 问题类型，只能是 "技术"、"行为" 或 "压力" 之一
   - difficulty: 难度，只能是 "简单"、"中等" 或 "困难" 之一
   - expected_key_points: 期望回答要点的数组（字符串数组）
{prev_section}
## 输出格式
直接输出 JSON 数组，不要 markdown 代码块，不要其他任何内容。示例:
[{{"question_text": "...", "category": "技术", "difficulty": "中等", "expected_key_points": ["要点1", "要点2"]}}]"""

    async def _call_llm(self, prompt: str) -> str:
        """调用 LLM API（OpenAI 兼容格式）"""
        base_url = self.config.base_url or "https://www.dmxapi.cn/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.config.model_name,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一位资深的面试专家。请严格按照JSON数组格式输出问题列表，不要包含任何其他内容。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens
        }

        logger.info(f"调用 LLM 生成问题: model={self.config.model_name}")

        response = await self.client.post(base_url, headers=headers, json=data)
        response.raise_for_status()

        result = response.json()

        # OpenAI 兼容格式解析
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]

        raise ValueError(f"LLM API 响应格式异常: {str(result)[:200]}")

    def _parse_response(self, content: str) -> List[Dict]:
        """解析 LLM 响应，提取问题 JSON 数组"""
        # 尝试直接解析
        try:
            parsed = json.loads(content)
            if isinstance(parsed, list):
                return self._validate_questions(parsed)
        except (json.JSONDecodeError, TypeError):
            pass

        # 尝试提取 JSON 代码块
        patterns = [
            r'```json\s*(.*?)\s*```',
            r'```\s*(.*?)\s*```',
        ]
        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                try:
                    parsed = json.loads(match.group(1).strip())
                    if isinstance(parsed, list):
                        return self._validate_questions(parsed)
                except (json.JSONDecodeError, TypeError):
                    pass

        # 尝试提取 JSON 数组
        match = re.search(r'\[.*\]', content, re.DOTALL)
        if match:
            try:
                parsed = json.loads(match.group())
                if isinstance(parsed, list):
                    return self._validate_questions(parsed)
            except (json.JSONDecodeError, TypeError):
                pass

        logger.warning(f"无法解析 LLM 响应为问题列表: {content[:200]}")
        return []

    def _validate_questions(self, questions: List[Dict]) -> List[Dict]:
        """验证和标准化问题列表"""
        validated = []
        valid_categories = {"技术", "行为", "压力"}
        valid_difficulties = {"简单", "中等", "困难"}

        for q in questions:
            if not isinstance(q, dict):
                continue
            if "question_text" not in q or not q["question_text"]:
                continue

            category = q.get("category", "技术")
            if category not in valid_categories:
                category = "技术"

            difficulty = q.get("difficulty", "中等")
            if difficulty not in valid_difficulties:
                difficulty = "中等"

            key_points = q.get("expected_key_points", [])
            if not isinstance(key_points, list):
                key_points = []

            validated.append({
                "question_text": q["question_text"],
                "category": category,
                "difficulty": difficulty,
                "expected_key_points": key_points
            })

        return validated

    def _get_fallback_questions(self, interviewer_role: str, count: int) -> List[Dict]:
        """从后备问题池获取问题"""
        pool = FALLBACK_QUESTIONS.get(interviewer_role, FALLBACK_QUESTIONS["业务领导1"])
        questions = []
        for q in pool[:count]:
            questions.append({
                "question_text": q["question_text"],
                "category": q.get("category", "技术"),
                "difficulty": q.get("difficulty", "中等"),
                "expected_key_points": q.get("expected_key_points", [])
            })
        return questions

    async def generate_questions(
        self,
        position_name: str,
        job_description: str,
        interviewer_role: str,
        role_description: str,
        question_count: int,
        round_number: int,
        previous_questions: List[str]
    ) -> List[Dict]:
        """生成面试问题"""
        try:
            prompt = self._build_prompt(
                position_name=position_name,
                job_description=job_description,
                interviewer_role=interviewer_role,
                role_description=role_description,
                question_count=question_count,
                round_number=round_number,
                previous_questions=previous_questions
            )

            content = await self._call_llm(prompt)
            questions = self._parse_response(content)

            if not questions:
                logger.warning("LLM 生成问题为空，使用后备问题池")
                return self._get_fallback_questions(interviewer_role, question_count)

            # 如果生成的问题不够，用后备问题补充
            if len(questions) < question_count:
                logger.info(f"LLM 生成 {len(questions)} 个问题，不足 {question_count} 个，从后备池补充")
                fallback = self._get_fallback_questions(interviewer_role, question_count - len(questions))
                questions.extend(fallback)

            return questions[:question_count]

        except Exception as e:
            logger.error(f"问题生成失败: {str(e)}，使用后备问题池")
            return self._get_fallback_questions(interviewer_role, question_count)
