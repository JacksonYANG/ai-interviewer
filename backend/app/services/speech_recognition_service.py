"""
语音识别服务 - 集成阿里云和腾讯云语音识别
"""
import httpx
import json
import base64
from typing import Optional, Dict
from app.core.logger import get_logger

logger = get_logger(__name__)


class SpeechRecognitionService:
    """语音识别服务类 - 支持多种语音识别提供商"""

    def __init__(
        self,
        provider: str = "aliyun",
        api_key: Optional[str] = None,
        app_id: Optional[str] = None,
        secret_key: Optional[str] = None
    ):
        """
        初始化语音识别服务

        Args:
            provider: 提供商 (aliyun, tencent)
            api_key: API密钥
            app_id: 应用ID
            secret_key: 密钥
        """
        self.provider = provider
        self.api_key = api_key
        self.app_id = app_id
        self.secret_key = secret_key
        self.client = httpx.AsyncClient(timeout=60.0)

    async def close(self):
        """关闭HTTP客户端"""
        await self.client.aclose()

    async def transcribe_audio(
        self,
        audio_data: bytes,
        format: str = "wav"
    ) -> str:
        """
        转录音频为文字

        Args:
            audio_data: 音频数据（bytes）
            format: 音频格式 (wav, mp3, m4a)

        Returns:
            转录文本
        """
        try:
            if self.provider == "aliyun":
                return await self._transcribe_with_aliyun(audio_data, format)
            elif self.provider == "tencent":
                return await self._transcribe_with_tencent(audio_data, format)
            else:
                raise ValueError(f"不支持的语音识别提供商: {self.provider}")

        except Exception as e:
            logger.error(f"语音识别失败: {str(e)}")
            raise

    async def _transcribe_with_aliyun(
        self,
        audio_data: bytes,
        format: str
    ) -> str:
        """
        使用阿里云语音识别

        Args:
            audio_data: 音频数据
            format: 音频格式

        Returns:
            转录文本
        """
        try:
            # 阿里云文件转写API
            url = "https://filetrans.cn-shanghai.aliyuncs.com/"

            # 准备请求数据
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')

            payload = {
                "format": format,
                "sample_rate": 16000,
                "audio": audio_base64
            }

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }

            # 发送请求
            response = await self.client.post(url, json=payload, headers=headers)
            response.raise_for_status()

            result = response.json()

            # 解析结果
            if "output" in result and "sentences" in result["output"]:
                sentences = result["output"]["sentences"]
                text = " ".join([s["text"] for s in sentences])
                return text
            else:
                logger.warning(f"阿里云语音识别返回格式异常: {result}")
                return ""

        except Exception as e:
            logger.error(f"阿里云语音识别失败: {str(e)}")
            # 返回占位文本
            return "[语音识别失败，请重试或使用文字输入]"

    async def _transcribe_with_tencent(
        self,
        audio_data: bytes,
        format: str
    ) -> str:
        """
        使用腾讯云语音识别

        Args:
            audio_data: 音频数据
            format: 音频格式

        Returns:
            转录文本
        """
        try:
            # 腾讯云语音识别API
            url = "https://asr.tencentcloudapi.com/"

            # 准备请求数据
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')

            payload = {
                "EngineModelType": "16k_zh",
                "ChannelNum": 1,
                "Data": audio_base64,
                "Format": format,
                "SampleRate": 16000
            }

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "X-TC-Action": "SentenceRecognition"
            }

            # 发送请求
            response = await self.client.post(url, json=payload, headers=headers)
            response.raise_for_status()

            result = response.json()

            # 解析结果
            if "Result" in result:
                return result["Result"]
            else:
                logger.warning(f"腾讯云语音识别返回格式异常: {result}")
                return ""

        except Exception as e:
            logger.error(f"腾讯云语音识别失败: {str(e)}")
            # 返回占位文本
            return "[语音识别失败，请重试或使用文字输入]"

    async def transcribe_audio_file(
        self,
        file_path: str,
        format: str = "wav"
    ) -> str:
        """
        转录音频文件为文字

        Args:
            file_path: 音频文件路径
            format: 音频格式

        Returns:
            转录文本
        """
        try:
            # 读取音频文件
            with open(file_path, 'rb') as f:
                audio_data = f.read()

            # 转录
            return await self.transcribe_audio(audio_data, format)

        except Exception as e:
            logger.error(f"转录音频文件失败: {str(e)}")
            raise
