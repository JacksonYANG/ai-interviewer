/**
 * 面试配置相关 API
 */
import apiClient from './api'

/**
 * AI 分析面试轮数
 * @param {Object} data - 职位信息
 * @returns {Promise<Object>} AI 分析结果
 */
export const analyzeInterviewRounds = async (data) => {
  return await apiClient.post('/interviews/analyze', data)
}

/**
 * 创建面试配置
 * @param {Object} data - 面试配置数据
 * @returns {Promise<Object>} 创建的面试配置
 */
export const createInterviewConfig = async (data) => {
  return await apiClient.post('/interviews/configs', data)
}

/**
 * 获取面试配置列表
 * @param {Object} params - 查询参数
 * @returns {Promise<Array>} 面试配置列表
 */
export const getInterviewConfigs = async (params = {}) => {
  return await apiClient.get('/interviews/configs', { params })
}

/**
 * 获取面试配置详情
 * @param {number} configId - 配置 ID
 * @returns {Promise<Object>} 面试配置详情
 */
export const getInterviewConfigDetail = async (configId) => {
  return await apiClient.get(`/interviews/configs/${configId}`)
}

/**
 * 更新面试配置
 * @param {number} configId - 配置 ID
 * @param {Object} data - 更新数据
 * @returns {Promise<Object>} 更新后的面试配置
 */
export const updateInterviewConfig = async (configId, data) => {
  return await apiClient.put(`/interviews/configs/${configId}`, data)
}

/**
 * 删除面试配置
 * @param {number} configId - 配置 ID
 * @returns {Promise<void>}
 */
export const deleteInterviewConfig = async (configId) => {
  return await apiClient.delete(`/interviews/configs/${configId}`)
}

/**
 * 添加面试轮次
 * @param {number} configId - 配置 ID
 * @param {Object} data - 轮次数据
 * @returns {Promise<Object>} 创建的轮次
 */
export const createInterviewRound = async (configId, data) => {
  return await apiClient.post(`/interviews/configs/${configId}/rounds`, data)
}

/**
 * 更新面试轮次
 * @param {number} configId - 配置 ID
 * @param {number} roundId - 轮次 ID
 * @param {Object} data - 更新数据
 * @returns {Promise<Object>} 更新后的轮次
 */
export const updateInterviewRound = async (configId, roundId, data) => {
  return await apiClient.put(`/interviews/configs/${configId}/rounds/${roundId}`, data)
}

/**
 * 删除面试轮次
 * @param {number} configId - 配置 ID
 * @param {number} roundId - 轮次 ID
 * @returns {Promise<void>}
 */
export const deleteInterviewRound = async (configId, roundId) => {
  return await apiClient.delete(`/interviews/configs/${configId}/rounds/${roundId}`)
}

// ==================== 面试会话相关 ====================

/**
 * 创建面试会话
 * @param {Object} data - 会话数据 { config_id, round_id }
 * @returns {Promise<Object>} 创建的会话
 */
export const createInterviewSession = async (data) => {
  return await apiClient.post('/interviews/sessions', data)
}

/**
 * 获取面试会话详情
 * @param {number} sessionId - 会话 ID
 * @returns {Promise<Object>} 会话详情
 */
export const getInterviewSession = async (sessionId) => {
  return await apiClient.get(`/interviews/sessions/${sessionId}`)
}

/**
 * 获取会话的所有问题
 * @param {number} sessionId - 会话 ID
 * @returns {Promise<Array>} 问题列表
 */
export const getSessionQuestions = async (sessionId) => {
  return await apiClient.get(`/interviews/sessions/${sessionId}/questions`)
}

/**
 * 获取当前问题
 * @param {number} sessionId - 会话 ID
 * @returns {Promise<Object>} 当前问题
 */
export const getCurrentQuestion = async (sessionId) => {
  return await apiClient.get(`/interviews/sessions/${sessionId}/current-question`)
}

/**
 * 提交答案
 * @param {number} sessionId - 会话 ID
 * @param {Object} data - 答案数据
 * @returns {Promise<Object>} 提交的答案
 */
export const submitAnswer = async (sessionId, data) => {
  return await apiClient.post(`/interviews/sessions/${sessionId}/answers`, data)
}

/**
 * 完成面试会话
 * @param {number} sessionId - 会话 ID
 * @param {Object} data - 完成数据 { notes }
 * @returns {Promise<Object>} 完成结果
 */
export const completeSession = async (sessionId, data = {}) => {
  return await apiClient.post(`/interviews/sessions/${sessionId}/complete`, data)
}

/**
 * 获取会话报告
 * @param {number} sessionId - 会话 ID
 * @returns {Promise<Object>} 报告数据
 */
export const getSessionReport = async (sessionId) => {
  return await apiClient.get(`/interviews/sessions/${sessionId}/report`)
}

// ==================== 用户统计相关 ====================

/**
 * 获取用户面试统计
 * @returns {Promise<Object>} 统计数据
 */
export const getUserStats = async () => {
  return await apiClient.get('/interviews/users/me/stats')
}