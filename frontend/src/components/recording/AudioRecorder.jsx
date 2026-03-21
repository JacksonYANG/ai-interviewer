import { useState, useEffect, useRef } from 'react'
import { Button, Space, Progress, Typography, Alert } from 'antd'
import {
  AudioOutlined,
  StopOutlined,
  PauseCircleOutlined,
  PlayCircleOutlined,
  DeleteOutlined,
} from '@ant-design/icons'

const { Text } = Typography

/**
 * 录音组件
 * 使用 MediaRecorder API 实现浏览器录音功能
 */
function AudioRecorder({
  onRecordingComplete,
  maxDuration = 300, // 最大录音时长（秒）
  autoStart = false,
}) {
  // 录音状态
  const [recordingState, setRecordingState] = useState('idle') // idle, recording, paused, stopped
  const [recordingTime, setRecordingTime] = useState(0)
  const [audioBlob, setAudioBlob] = useState(null)
  const [audioUrl, setAudioUrl] = useState(null)
  const [error, setError] = useState(null)

  // MediaRecorder 和相关引用
  const mediaRecorderRef = useRef(null)
  const audioChunksRef = useRef([])
  const timerRef = useRef(null)
  const streamRef = useRef(null)

  /**
   * 初始化录音设备
   */
  const initRecorder = async () => {
    try {
      setError(null)
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      streamRef.current = stream

      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: MediaRecorder.isTypeSupported('audio/webm')
          ? 'audio/webm'
          : 'audio/mp4',
      })

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
        }
      }

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, {
          type: mediaRecorder.mimeType,
        })
        const url = URL.createObjectURL(audioBlob)
        setAudioBlob(audioBlob)
        setAudioUrl(url)
        audioChunksRef.current = []

        if (onRecordingComplete) {
          onRecordingComplete(audioBlob, url)
        }
      }

      mediaRecorderRef.current = mediaRecorder
      return true
    } catch (err) {
      console.error('初始化录音失败:', err)
      setError('无法访问麦克风，请检查权限设置')
      return false
    }
  }

  /**
   * 开始录音
   */
  const startRecording = async () => {
    if (!mediaRecorderRef.current) {
      const initialized = await initRecorder()
      if (!initialized) return
    }

    try {
      audioChunksRef.current = []
      mediaRecorderRef.current.start()
      setRecordingState('recording')
      setError(null)

      // 开始计时
      timerRef.current = setInterval(() => {
        setRecordingTime((prev) => {
          const newTime = prev + 1
          if (newTime >= maxDuration) {
            stopRecording()
            return maxDuration
          }
          return newTime
        })
      }, 1000)
    } catch (err) {
      console.error('开始录音失败:', err)
      setError('开始录音失败，请重试')
    }
  }

  /**
   * 暂停录音
   */
  const pauseRecording = () => {
    if (
      mediaRecorderRef.current &&
      mediaRecorderRef.current.state === 'recording'
    ) {
      mediaRecorderRef.current.pause()
      setRecordingState('paused')
      clearInterval(timerRef.current)
    }
  }

  /**
   * 恢复录音
   */
  const resumeRecording = () => {
    if (
      mediaRecorderRef.current &&
      mediaRecorderRef.current.state === 'paused'
    ) {
      mediaRecorderRef.current.resume()
      setRecordingState('recording')

      timerRef.current = setInterval(() => {
        setRecordingTime((prev) => {
          const newTime = prev + 1
          if (newTime >= maxDuration) {
            stopRecording()
            return maxDuration
          }
          return newTime
        })
      }, 1000)
    }
  }

  /**
   * 停止录音
   */
  const stopRecording = () => {
    if (
      mediaRecorderRef.current &&
      mediaRecorderRef.current.state !== 'inactive'
    ) {
      mediaRecorderRef.current.stop()
      setRecordingState('stopped')
      clearInterval(timerRef.current)

      // 停止所有音频轨道
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop())
      }
    }
  }

  /**
   * 重新录音
   */
  const resetRecording = () => {
    if (audioUrl) {
      URL.revokeObjectURL(audioUrl)
    }
    setAudioBlob(null)
    setAudioUrl(null)
    setRecordingTime(0)
    setRecordingState('idle')
    setError(null)
    mediaRecorderRef.current = null
  }

  /**
   * 格式化时间显示
   */
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, '0')}:${secs
      .toString()
      .padStart(2, '0')}`
  }

  // 自动开始录音
  useEffect(() => {
    if (autoStart && recordingState === 'idle') {
      startRecording()
    }

    return () => {
      // 清理定时器
      if (timerRef.current) {
        clearInterval(timerRef.current)
      }
      // 清理音频 URL
      if (audioUrl) {
        URL.revokeObjectURL(audioUrl)
      }
      // 清理媒体流
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop())
      }
    }
  }, [])

  // 计算进度百分比
  const progressPercent = (recordingTime / maxDuration) * 100

  return (
    <div style={{ width: '100%' }}>
      {error && (
        <Alert
          message="错误"
          description={error}
          type="error"
          showIcon
          style={{ marginBottom: '16px' }}
        />
      )}

      {/* 录音时间和进度 */}
      <div style={{ marginBottom: '16px' }}>
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            marginBottom: '8px',
          }}
        >
          <Text strong>
            {recordingState === 'recording' ? '录音中' : '录音时长'}
          </Text>
          <Text type={recordingTime >= maxDuration ? 'danger' : 'secondary'}>
            {formatTime(recordingTime)} / {formatTime(maxDuration)}
          </Text>
        </div>
        <Progress
          percent={progressPercent}
          status={
            recordingState === 'recording'
              ? 'active'
              : recordingTime >= maxDuration
              ? 'exception'
              : 'normal'
          }
          showInfo={false}
        />
      </div>

      {/* 控制按钮 */}
      <Space>
        {recordingState === 'idle' && (
          <Button
            type="primary"
            icon={<AudioOutlined />}
            onClick={startRecording}
            size="large"
          >
            开始录音
          </Button>
        )}

        {recordingState === 'recording' && (
          <>
            <Button
              icon={<PauseCircleOutlined />}
              onClick={pauseRecording}
              size="large"
            >
              暂停
            </Button>
            <Button
              type="primary"
              danger
              icon={<StopOutlined />}
              onClick={stopRecording}
              size="large"
            >
              停止
            </Button>
          </>
        )}

        {recordingState === 'paused' && (
          <>
            <Button
              type="primary"
              icon={<PlayCircleOutlined />}
              onClick={resumeRecording}
              size="large"
            >
              继续
            </Button>
            <Button
              danger
              icon={<StopOutlined />}
              onClick={stopRecording}
              size="large"
            >
              停止
            </Button>
          </>
        )}

        {recordingState === 'stopped' && audioUrl && (
          <>
            <audio src={audioUrl} controls style={{ marginRight: '16px' }} />
            <Button
              icon={<DeleteOutlined />}
              onClick={resetRecording}
              size="large"
            >
              重新录音
            </Button>
          </>
        )}
      </Space>
    </div>
  )
}

export default AudioRecorder
