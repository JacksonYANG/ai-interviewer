# backend/tests/test_models.py
import pytest
from sqlalchemy import inspect
from app.database import Base, engine


def test_question_model_has_required_columns():
    """验证 Question 模型包含所有必要字段"""
    from app.models.question import Question
    mapper = inspect(Question)
    column_names = [c.key for c in mapper.mapper.column_attrs]

    required = [
        "id", "session_id", "round_number", "question_text",
        "question_type", "category", "difficulty",
        "expected_key_points", "display_order", "ai_generated", "created_at"
    ]
    for col in required:
        assert col in column_names, f"Question 模型缺少字段: {col}"
