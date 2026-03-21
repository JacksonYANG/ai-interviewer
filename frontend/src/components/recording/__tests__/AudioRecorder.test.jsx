"""
前端录音组件测试
"""
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import AudioRecorder from '../src/components/recording/AudioRecorder';

// 模拟 MediaRecorder API
const mockMediaRecorder = {
  start: vi.fn(),
  stop: vi.fn(),
  pause: vi.fn(),
  resume: vi.fn(),
  addEventListener: vi.fn(),
  removeEventListener: vi.fn(),
};

global.MediaRecorder = vi.fn(() => mockMediaRecorder);

// 模拟 navigator.mediaDevices
global.navigator.mediaDevices = {
  getUserMedia: vi.fn(() =>
    Promise.resolve({
      getTracks: () => [{ stop: vi.fn() }],
    })
  ),
};

describe('AudioRecorder 组件测试', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('应该渲染录音组件', () => {
    render(<AudioRecorder />);

    expect(screen.getByText('开始录音')).toBeInTheDocument();
    expect(screen.getByText('录音时长: 00:00')).toBeInTheDocument();
  });

  it('应该开始录音', async () => {
    render(<AudioRecorder />);

    const startButton = screen.getByText('开始录音');
    fireEvent.click(startButton);

    await waitFor(() => {
      expect(navigator.mediaDevices.getUserMedia).toHaveBeenCalledWith({ audio: true });
      expect(mockMediaRecorder.start).toHaveBeenCalled();
    });
  });

  it('应该停止录音', async () => {
    render(<AudioRecorder />);

    // 开始录音
    const startButton = screen.getByText('开始录音');
    fireEvent.click(startButton);

    await waitFor(() => {
      expect(screen.getByText('停止录音')).toBeInTheDocument();
    });

    // 停止录音
    const stopButton = screen.getByText('停止录音');
    fireEvent.click(stopButton);

    await waitFor(() => {
      expect(mockMediaRecorder.stop).toHaveBeenCalled();
    });
  });

  it('应该暂停录音', async () => {
    render(<AudioRecorder />);

    // 开始录音
    const startButton = screen.getByText('开始录音');
    fireEvent.click(startButton);

    await waitFor(() => {
      expect(screen.getByText('暂停录音')).toBeInTheDocument();
    });

    // 暂停录音
    const pauseButton = screen.getByText('暂停录音');
    fireEvent.click(pauseButton);

    await waitFor(() => {
      expect(mockMediaRecorder.pause).toHaveBeenCalled();
    });
  });

  it('应该继续录音', async () => {
    render(<AudioRecorder />);

    // 开始录音
    fireEvent.click(screen.getByText('开始录音'));

    await waitFor(() => {
      expect(screen.getByText('暂停录音')).toBeInTheDocument();
    });

    // 暂停录音
    fireEvent.click(screen.getByText('暂停录音'));

    await waitFor(() => {
      expect(screen.getByText('继续录音')).toBeInTheDocument();
    });

    // 继续录音
    fireEvent.click(screen.getByText('继续录音'));

    await waitFor(() => {
      expect(mockMediaRecorder.resume).toHaveBeenCalled();
    });
  });

  it('应该显示录音时长', async () => {
    render(<AudioRecorder />);

    fireEvent.click(screen.getByText('开始录音'));

    // 等待计时器更新
    await waitFor(() => {
      expect(screen.getByText(/录音时长:/)).toBeInTheDocument();
    }, { timeout: 2000 });
  });

  it('应该在达到最大时长时自动停止', async () => {
    const maxDuration = 2; // 2秒用于测试
    render(<AudioRecorder maxDuration={maxDuration} />);

    fireEvent.click(screen.getByText('开始录音'));

    // 等待达到最大时长
    await waitFor(() => {
      expect(mockMediaRecorder.stop).toHaveBeenCalled();
    }, { timeout: (maxDuration + 1) * 1000 });
  });

  it('应该处理录音错误', async () => {
    // 模拟 getUserMedia 抛出错误
    navigator.mediaDevices.getUserMedia = vi.fn(() =>
      Promise.reject(new Error('Permission denied'))
    );

    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    render(<AudioRecorder />);

    fireEvent.click(screen.getByText('开始录音'));

    await waitFor(() => {
      expect(consoleSpy).toHaveBeenCalled();
    });

    consoleSpy.mockRestore();
  });

  it('应该支持自动开始录音', async () => {
    render(<AudioRecorder autoStart={true} />);

    await waitFor(() => {
      expect(navigator.mediaDevices.getUserMedia).toHaveBeenCalledWith({ audio: true });
    });
  });

  it('应该支持录音完成后回放', async () => {
    render(<AudioRecorder />);

    // 模拟录音完成
    fireEvent.click(screen.getByText('开始录音'));

    await waitFor(() => {
      expect(screen.getByText('停止录音')).toBeInTheDocument();
    });

    // 停止录音
    fireEvent.click(screen.getByText('停止录音'));

    await waitFor(() => {
      expect(screen.getByText('播放录音')).toBeInTheDocument();
    });
  });

  it('应该支持重新录音', async () => {
    render(<AudioRecorder />);

    // 模拟录音完成
    fireEvent.click(screen.getByText('开始录音'));

    await waitFor(() => {
      expect(screen.getByText('停止录音')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('停止录音'));

    await waitFor(() => {
      expect(screen.getByText('重新录音')).toBeInTheDocument();
    });

    // 点击重新录音
    fireEvent.click(screen.getByText('重新录音'));

    await waitFor(() => {
      expect(screen.getByText('开始录音')).toBeInTheDocument();
    });
  });
});
