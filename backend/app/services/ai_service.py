"""
AI服务 - 支持可配置的LLM提供商
"""
import httpx
import json
from typing import List, Dict, Optional
from app.schemas.interview import AIAnalysisRequest, AIAnalysisResponse, LLMConfig
from app.core.logger import get_logger

logger = get_logger(__name__)


class AIService:
    """AI服务类 - 支持多种LLM提供商"""

    # 默认的面试官角色配置
    DEFAULT_ROLES = {
        1: {
            "role": "业务领导1",
            "description": "直属领导，主要考察业务能力和团队匹配度",
            "question_count": 6
        },
        2: {
            "role": "业务领导2",
            "description": "同组或跨组领导，考察技术深度和协作能力",
            "question_count": 6
        },
        3: {
            "role": "部门总监",
            "description": "部门负责人，考察战略思维和领导力",
            "question_count": 6
        },
        4: {
            "role": "CP面试官",
            "description": "Cross-Peer跨部门面试，考察综合素质和文化匹配",
            "question_count": 5
        },
        5: {
            "role": "HR",
            "description": "人力资源，考察价值观、薪资期望和稳定性",
            "question_count": 5
        }
    }

    def __init__(self, config: LLMConfig):
        """
        初始化AI服务

        Args:
            config: LLM配置
        """
        self.config = config
        self.client = httpx.AsyncClient(timeout=60.0)

    async def close(self):
        """关闭HTTP客户端"""
        await self.client.aclose()

    def _build_prompt(self, request: AIAnalysisRequest) -> str:
        """
        构建AI分析Prompt

        Args:
            request: AI分析请求

        Returns:
            构建好的Prompt
        """
        prompt = f"""你是一位资深的面试专家，需要根据职位信息分析需要几轮面试。

职位信息：
- 职位名称: {request.position_name}
- 职位级别: {request.position_level or '未指定'}
- 公司类型: {request.company_type or '未指定'}
- 行业: {request.industry or '未指定'}
- 薪资范围: {request.salary_range or '未指定'}
- 职位描述: {request.job_description or '无'}

请分析这个职位需要几轮面试（2-5轮），并给出详细理由。

面试轮次说明：
1. 第一轮：业务领导1（直属领导）- 考察业务能力和团队匹配度
2. 第二轮：业务领导2（同组/跨组）- 考察技术深度和协作能力
3. 第三轮：部门总监 - 考察战略思维和领导力
4. 第四轮：CP面试官（跨部门）- 考察综合素质和文化匹配
5. 第五轮：HR - 考察价值观、薪资期望和稳定性

典型配置参考：
- 初级岗位：2-3轮
- 中级岗位：3-4轮
- 高级岗位：4-5轮
- 管理/专家：5轮

请以JSON格式返回：
{{
    "suggested_rounds": 数字(2-5),
    "reasoning": "详细的推荐理由",
    "rounds": [
        {{
            "round_number": 1,
            "interviewer_role": "面试官角色名称",
            "role_description": "角色描述",
            "question_count": 问题数量(3-10),
            "reasoning": "为什么需要这一轮"
        }}
    ]
}}

注意：
- suggested_rounds必须是2-5之间的整数
- rounds数组的长度必须等于suggested_rounds
- 每轮的question_count建议为5-7个问题
- reasoning要详细说明为什么推荐这个轮数配置
"""

        return prompt

    async def _call_qwen(self, prompt: str) -> Dict:
        """
        调用通义千问API

        Args:
            prompt: 用户提示词

        Returns:
            API响应
        """
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.config.model_name,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一位资深的面试专家，擅长分析职位需求和设计面试流程。请严格按照JSON格式返回结果。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "result_format": "message"  # 确保返回消息格式
        }

        # 使用用户提供的base_url或默认的通义千问API
        base_url = self.config.base_url or "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"

        logger.info(f"调用通义千问API: {base_url}")

        response = await self.client.post(base_url, headers=headers, json=data)
        response.raise_for_status()

        result = response.json()

        # 解析通义千问的响应格式
        if "output" in result and "choices" in result["output"]:
            content = result["output"]["choices"][0]["message"]["content"]
        else:
            raise ValueError(f"通义千问API响应格式异常: {result}")

        return {"content": content}

    async def _call_openai(self, prompt: str) -> Dict:
        """
        调用OpenAI API

        Args:
            prompt: 用户提示词

        Returns:
            API响应
        """
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.config.model_name,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一位资深的面试专家，擅长分析职位需求和设计面试流程。请严格按照JSON格式返回结果。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens
        }

        # 使用用户提供的base_url或默认的OpenAI API
        base_url = self.config.base_url or "https://api.openai.com/v1/chat/completions"

        logger.info(f"调用OpenAI API: {base_url}")

        response = await self.client.post(base_url, headers=headers, json=data)
        response.raise_for_status()

        result = response.json()

        # 解析OpenAI的响应格式
        if "choices" in result and len(result["choices"]) > 0:
            content = result["choices"][0]["message"]["content"]
        else:
            raise ValueError(f"OpenAI API响应格式异常: {result}")

        return {"content": content}

    async def _call_anthropic(self, prompt: str) -> Dict:
        """
        调用Anthropic Claude API

        Args:
            prompt: 用户提示词

        Returns:
            API响应
        """
        headers = {
            "x-api-key": self.config.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }

        data = {
            "model": self.config.model_name,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "system": "你是一位资深的面试专家，擅长分析职位需求和设计面试流程。请严格按照JSON格式返回结果。"
        }

        # 使用用户提供的base_url或默认的Anthropic API
        base_url = self.config.base_url or "https://api.anthropic.com/v1/messages"

        logger.info(f"调用Anthropic API: {base_url}")

        response = await self.client.post(base_url, headers=headers, json=data)
        response.raise_for_status()

        result = response.json()

        # 解析Anthropic的响应格式
        if "content" in result and len(result["content"]) > 0:
            content = result["content"][0]["text"]
        else:
            raise ValueError(f"Anthropic API响应格式异常: {result}")

        return {"content": content}

    async def _parse_ai_response(self, content: str) -> Dict:
        """
        解析AI响应，提取JSON

        Args:
            content: AI返回的内容

        Returns:
            解析后的字典
        """
        # 尝试直接解析JSON
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass

        # 尝试提取JSON代码块
        if "```json" in content:
            start = content.find("```json") + 7
            end = content.find("```", start)
            if end > start:
                try:
                    return json.loads(content[start:end].strip())
                except json.JSONDecodeError:
                    pass

        if "```" in content:
            start = content.find("```") + 3
            end = content.find("```", start)
            if end > start:
                try:
                    return json.loads(content[start:end].strip())
                except json.JSONDecodeError:
                    pass

        # 如果都失败，返回默认配置
        logger.warning(f"无法解析AI响应，使用默认配置: {content[:200]}")
        return self._get_default_config()

    def _get_default_config(self) -> Dict:
        """
        获取默认配置（当AI分析失败时使用）

        Returns:
            默认配置字典
        """
        return {
            "suggested_rounds": 3,
            "reasoning": "基于职位信息，建议进行3轮面试：业务领导1、业务领导2和HR面试。这是大多数中级岗位的标准配置。",
            "rounds": [
                {
                    "round_number": 1,
                    "interviewer_role": self.DEFAULT_ROLES[1]["role"],
                    "role_description": self.DEFAULT_ROLES[1]["description"],
                    "question_count": 6,
                    "reasoning": "考察基本业务能力和团队匹配度"
                },
                {
                    "round_number": 2,
                    "interviewer_role": self.DEFAULT_ROLES[2]["role"],
                    "role_description": self.DEFAULT_ROLES[2]["description"],
                    "question_count": 6,
                    "reasoning": "深入考察技术能力和协作能力"
                },
                {
                    "round_number": 3,
                    "interviewer_role": self.DEFAULT_ROLES[5]["role"],
                    "role_description": self.DEFAULT_ROLES[5]["description"],
                    "question_count": 5,
                    "reasoning": "确认价值观和薪资期望"
                }
            ]
        }

    async def analyze_rounds(self, request: AIAnalysisRequest) -> AIAnalysisResponse:
        """
        分析面试轮数

        Args:
            request: AI分析请求

        Returns:
            AI分析响应
        """
        try:
            # 构建Prompt
            prompt = self._build_prompt(request)

            # 根据提供商调用相应的API
            if self.config.provider == "qwen":
                response = await self._call_qwen(prompt)
            elif self.config.provider == "openai":
                response = await self._call_openai(prompt)
            elif self.config.provider == "anthropic":
                response = await self._call_anthropic(prompt)
            else:
                raise ValueError(f"不支持的LLM提供商: {self.config.provider}")

            # 解析响应
            result = await self._parse_ai_response(response["content"])

            # 验证和修正数据
            suggested_rounds = max(2, min(5, result.get("suggested_rounds", 3)))
            rounds_data = result.get("rounds", [])

            # 如果AI返回的轮数不匹配，修正它
            if len(rounds_data) != suggested_rounds:
                rounds_data = []
                for i in range(suggested_rounds):
                    round_num = i + 1
                    if round_num in self.DEFAULT_ROLES:
                        role_info = self.DEFAULT_ROLES[round_num]
                        rounds_data.append({
                            "round_number": round_num,
                            "interviewer_role": role_info["role"],
                            "role_description": role_info["description"],
                            "question_count": role_info["question_count"],
                            "reasoning": f"标准的第{round_num}轮面试"
                        })

            return AIAnalysisResponse(
                suggested_rounds=suggested_rounds,
                reasoning=result.get("reasoning", "基于职位信息综合分析"),
                rounds=[
                    {
                        "round_number": r["round_number"],
                        "interviewer_role": r["interviewer_role"],
                        "role_description": r["role_description"],
                        "question_count": r["question_count"],
                        "reasoning": r.get("reasoning", "")
                    }
                    for r in rounds_data
                ]
            )

        except Exception as e:
            logger.error(f"AI分析失败: {str(e)}")
            # 返回默认配置
            default_config = self._get_default_config()
            return AIAnalysisResponse(
                suggested_rounds=default_config["suggested_rounds"],
                reasoning=default_config["reasoning"],
                rounds=default_config["rounds"]
            )
