"""
评分服务单元测试
"""
import pytest
from unittest.mock import Mock, patch
from app.services.scoring_service import ScoringService
from app.schemas.interview import ScoreResponse


@pytest.fixture
def db_session():
    """模拟数据库会话"""
    return Mock()


@pytest.fixture
def scoring_service(db_session):
    """创建评分服务实例"""
    return ScoringService(db_session)


class TestScoringService:
    """评分服务测试类"""

    @pytest.mark.asyncio
    async def test_calculate_score_basic(self, scoring_service):
        """测试基本评分计算"""
        # 模拟问题
        with patch.object(scoring_service, 'db') as mock_db:
            from app.models.question import Question
            mock_question = Mock(spec=Question)
            mock_question.id = 1
            mock_question.question_text = "请介绍一下你的项目经验"
            mock_question.round_number = 1

            mock_db.query.return_value.filter.return_value.first.return_value = mock_question

            # 测试数据
            question_id = 1
            answer_text = "我有丰富的项目经验，首先参与了架构设计，其次负责了核心模块开发，最后进行了性能优化。使用了很多先进的技术，比如微服务、容器化等。我认为我的经验很匹配这个职位。"

            # 计算评分
            result = await scoring_service.calculate_score(
                question_id=question_id,
                answer_text=answer_text,
                audio_duration=120,
                expected_duration=120
            )

            # 验证结果
            assert isinstance(result, ScoreResponse)
            assert result.question_id == question_id
            assert 0 <= result.professional_score <= 100
            assert 0 <= result.communication_score <= 100
            assert 0 <= result.confidence_score <= 100
            assert 0 <= result.time_score <= 100
            assert 0 <= result.total_score <= 100
            assert len(result.ai_feedback) > 0
            assert len(result.improvement_suggestions) > 0

    @pytest.mark.asyncio
    async def test_score_professional_ability(self, scoring_service):
        """测试专业能力评分"""
        question_text = "请介绍一下你的技术栈"
        answer_text = "我使用Python、Java进行开发，熟悉微服务架构，有丰富的系统设计和性能优化经验。"

        score = await scoring_service._score_professional_ability(
            question_text,
            answer_text,
            1
        )

        assert 0 <= score <= 100
        assert score > 60  # 应该包含关键词，分数应该较高

    @pytest.mark.asyncio
    async def test_score_communication(self, scoring_service):
        """测试沟通表达评分"""
        answer_text = "首先，我分析了问题，然后设计了解决方案，最后实施了改进。因此，项目获得了成功。"

        score = await scoring_service._score_communication(answer_text)

        assert 0 <= score <= 100
        assert score > 60  # 应该有逻辑连接词，分数应该较高

    @pytest.mark.asyncio
    async def test_score_confidence(self, scoring_service):
        """测试面试状态评分"""
        answer_text = "我认为这个方案是可行的。我相信我的经验能够胜任这个职位。我建议采用微服务架构。"

        score = await scoring_service._score_confidence(answer_text)

        assert 0 <= score <= 100
        assert score > 60  # 应该有自信表达，分数应该较高

    @pytest.mark.asyncio
    async def test_score_time_control_perfect(self, scoring_service):
        """测试时间控制评分 - 完美时间"""
        score = await scoring_service._score_time_control(
            audio_duration=120,
            expected_duration=120
        )

        assert score >= 90  # 完美时间应该得到高分

    @pytest.mark.asyncio
    async def test_score_time_control_good(self, scoring_service):
        """测试时间控制评分 - 良好时间"""
        score = await scoring_service._score_time_control(
            audio_duration=100,
            expected_duration=120
        )

        assert score >= 80  # 在合理范围内应该得到良好分数

    @pytest.mark.asyncio
    async def test_score_time_control_poor(self, scoring_service):
        """测试时间控制评分 - 较差时间"""
        score = await scoring_service._score_time_control(
            audio_duration=30,
            expected_duration=120
        )

        assert score < 70  # 时间太短应该得到较低分数

    @pytest.mark.asyncio
    async def test_generate_feedback(self, scoring_service):
        """测试生成反馈"""
        feedback = await scoring_service._generate_feedback(
            question_text="请介绍你自己",
            answer_text="我有丰富的经验",
            professional_score=85,
            communication_score=80,
            confidence_score=75
        )

        assert len(feedback) > 0
        assert "✓" in feedback or "△" in feedback

    @pytest.mark.asyncio
    async def test_generate_improvement_suggestions(self, scoring_service):
        """测试生成改进建议"""
        suggestions = await scoring_service._generate_improvement_suggestions(
            professional_score=60,
            communication_score=65,
            confidence_score=70,
            time_score=75
        )

        assert len(suggestions) > 0
        assert "•" in suggestions

    def test_save_score(self, scoring_service):
        """测试保存评分"""
        score_data = ScoreResponse(
            question_id=1,
            professional_score=80.0,
            communication_score=75.0,
            confidence_score=85.0,
            time_score=90.0,
            total_score=82.5,
            ai_feedback="测试反馈",
            improvement_suggestions="测试建议"
        )

        with patch.object(scoring_service.db, 'add'), \
             patch.object(scoring_service.db, 'commit'), \
             patch.object(scoring_service.db, 'refresh'):

            from app.models.score import Score
            mock_score = Mock(spec=Score)
            mock_score.id = 1

            with patch('app.services.scoring_service.Score', return_value=mock_score):
                result = scoring_service.save_score(score_data)

                assert result is not None

    def test_get_question_score(self, scoring_service):
        """测试获取问题评分"""
        from app.models.score import Score

        mock_score = Mock(spec=Score)
        mock_score.id = 1
        mock_score.question_id = 1

        with patch.object(scoring_service.db, 'query') as mock_query:
            mock_query.return_value.filter.return_value.first.return_value = mock_score

            result = scoring_service.get_question_score(1)

            assert result is not None
            assert result.id == 1
