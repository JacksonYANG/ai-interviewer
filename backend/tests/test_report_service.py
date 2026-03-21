"""
报告生成服务单元测试
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from app.services.report_service import ReportGenerationService
from app.schemas.interview import InterviewReportResponse


@pytest.fixture
def db_session():
    """模拟数据库会话"""
    return Mock()


@pytest.fixture
def report_service(db_session):
    """创建报告生成服务实例"""
    return ReportGenerationService(db_session)


@pytest.fixture
def mock_session():
    """模拟面试会话"""
    session = Mock()
    session.id = 1
    session.config_id = 1
    session.user_id = 1
    session.status = "completed"
    session.total_questions = 5
    return session


@pytest.fixture
def mock_config():
    """模拟面试配置"""
    config = Mock()
    config.id = 1
    config.position_name = "Python工程师"
    config.company_name = "测试公司"
    return config


@pytest.fixture
def mock_user():
    """模拟用户"""
    user = Mock()
    user.id = 1
    user.username = "testuser"
    return user


@pytest.fixture
def mock_questions():
    """模拟问题列表"""
    questions = [Mock(id=i) for i in range(1, 6)]
    return questions


@pytest.fixture
def mock_scores():
    """模拟评分列表"""
    scores = []
    for i in range(1, 6):
        score = Mock()
        score.id = i
        score.question_id = i
        score.professional_score = 75.0 + i
        score.communication_score = 70.0 + i
        score.confidence_score = 80.0 + i
        score.time_score = 85.0 + i
        score.total_score = 77.5 + i
        score.ai_feedback = "测试反馈"
        score.improvement_suggestions = "测试建议"
        score.scored_at = datetime.now()
        scores.append(score)
    return scores


class TestReportGenerationService:
    """报告生成服务测试类"""

    @pytest.mark.asyncio
    async def test_generate_report_success(
        self,
        report_service,
        mock_session,
        mock_config,
        mock_user,
        mock_questions,
        mock_scores
    ):
        """测试成功生成报告"""
        with patch.object(report_service.db, 'query') as mock_query:
            # 模拟数据库查询
            def query_side_effect(model):
                if hasattr(model, '__name__') and model.__name__ == 'InterviewSession':
                    result = Mock()
                    result.filter.return_value.first.return_value = mock_session
                    return result
                elif hasattr(model, '__name__') and model.__name__ == 'InterviewConfig':
                    result = Mock()
                    result.filter.return_value.first.return_value = mock_config
                    return result
                elif hasattr(model, '__name__') and model.__name__ == 'User':
                    result = Mock()
                    result.filter.return_value.first.return_value = mock_user
                    return result
                elif hasattr(model, '__name__') and model.__name__ == 'Question':
                    result = Mock()
                    result.filter.return_value.all.return_value = mock_questions
                    return result
                elif hasattr(model, '__name__') and model.__name__ == 'Score':
                    result = Mock()
                    result.filter.return_value.all.return_value = mock_scores
                    return result
                return Mock()

            mock_query.side_effect = query_side_effect

            # 生成报告
            report = await report_service.generate_report(session_id=1)

            # 验证结果
            assert isinstance(report, InterviewReportResponse)
            assert report.session_id == 1
            assert report.candidate_name == "testuser"
            assert report.position_name == "Python工程师"
            assert report.total_questions == 5
            assert report.answered_questions == 5
            assert 0 <= report.overall_score <= 100
            assert len(report.strengths) > 0
            assert len(report.improvements) > 0
            assert len(report.summary) > 0

    def test_calculate_average_scores(self, report_service, mock_scores):
        """测试计算平均分"""
        avg_scores = report_service._calculate_average_scores(mock_scores)

        assert "professional" in avg_scores
        assert "communication" in avg_scores
        assert "confidence" in avg_scores
        assert "time" in avg_scores
        assert "total" in avg_scores

        # 验证计算正确性
        expected_professional = sum(s.professional_score for s in mock_scores) / len(mock_scores)
        assert abs(avg_scores["professional"] - round(expected_professional, 2)) < 0.01

    @pytest.mark.asyncio
    async def test_generate_summary_excellent(self, report_service, mock_session, mock_config):
        """测试生成优秀总结"""
        avg_scores = {
            "professional": 95.0,
            "communication": 90.0,
            "confidence": 92.0,
            "time": 95.0,
            "total": 93.0
        }

        summary = await report_service._generate_summary(mock_session, mock_config, avg_scores)

        assert len(summary) > 0
        assert "优秀" in summary

    @pytest.mark.asyncio
    async def test_generate_summary_good(self, report_service, mock_session, mock_config):
        """测试生成良好总结"""
        avg_scores = {
            "professional": 85.0,
            "communication": 80.0,
            "confidence": 82.0,
            "time": 85.0,
            "total": 83.0
        }

        summary = await report_service._generate_summary(mock_session, mock_config, avg_scores)

        assert len(summary) > 0
        assert "良好" in summary

    @pytest.mark.asyncio
    async def test_generate_summary_average(self, report_service, mock_session, mock_config):
        """测试生成中等总结"""
        avg_scores = {
            "professional": 75.0,
            "communication": 70.0,
            "confidence": 72.0,
            "time": 75.0,
            "total": 73.0
        }

        summary = await report_service._generate_summary(mock_session, mock_config, avg_scores)

        assert len(summary) > 0
        assert "中等" in summary

    @pytest.mark.asyncio
    async def test_generate_summary_poor(self, report_service, mock_session, mock_config):
        """测试生成较差总结"""
        avg_scores = {
            "professional": 60.0,
            "communication": 55.0,
            "confidence": 58.0,
            "time": 62.0,
            "total": 58.75
        }

        summary = await report_service._generate_summary(mock_session, mock_config, avg_scores)

        assert len(summary) > 0
        assert "需要提升" in summary

    @pytest.mark.asyncio
    async def test_generate_strengths(self, report_service, mock_scores):
        """测试生成亮点"""
        avg_scores = {
            "professional": 85.0,
            "communication": 80.0,
            "confidence": 75.0,
            "time": 90.0
        }

        strengths = await report_service._generate_strengths(avg_scores, mock_scores)

        assert len(strengths) > 0
        assert len(strengths) <= 2  # 应该最多返回2个亮点

    @pytest.mark.asyncio
    async def test_generate_improvements(self, report_service, mock_scores):
        """测试生成改进建议"""
        avg_scores = {
            "professional": 65.0,
            "communication": 60.0,
            "confidence": 70.0,
            "time": 75.0
        }

        improvements = await report_service._generate_improvements(avg_scores, mock_scores)

        assert len(improvements) > 0
        assert len(improvements) <= 2  # 应该最多返回2个改进建议

        # 验证优先级
        for improvement in improvements:
            assert improvement.priority in ["high", "medium", "low"]

    def test_get_strongest_aspect(self, report_service):
        """测试获取最强维度"""
        avg_scores = {
            "professional": 85.0,
            "communication": 80.0,
            "confidence": 75.0,
            "time": 90.0,
            "total": 82.5
        }

        strongest = report_service._get_strongest_aspect(avg_scores)

        assert strongest == "时间控制"

    def test_get_weakest_aspect(self, report_service):
        """测试获取最弱维度"""
        avg_scores = {
            "professional": 65.0,
            "communication": 60.0,
            "confidence": 70.0,
            "time": 75.0,
            "total": 67.5
        }

        weakest = report_service._get_weakest_aspect(avg_scores)

        assert weakest == "沟通表达"
