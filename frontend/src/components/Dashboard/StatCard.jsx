import React from 'react'
import { Card, Typography } from 'antd'
import {
  CalendarOutlined,
  CheckCircleOutlined,
  TrophyOutlined,
  ScheduleOutlined,
} from '@ant-design/icons'
import '../../styles/theme.css'

const { Text } = Typography

/**
 * 统计卡片组件
 * @param {string} label - 标签文字
 * @param {string|number} value - 数值
 * @param {string} unit - 单位（可选）
 * @param {string} variant - 颜色变体：primary | success | warning | info
 * @param {ReactNode} icon - 图标（可选）
 * @param {boolean} loading - 加载状态
 */
function StatCard({
  label,
  value,
  unit = '',
  variant = 'primary',
  icon = null,
  loading = false,
}) {
  // 根据variant定义样式 - 使用CSS变量
  const variantStyles = {
    primary: {
      borderColor: 'var(--color-primary)',
      iconColor: 'var(--color-primary)',
      bgColor: 'var(--color-primary-light)',
    },
    success: {
      borderColor: 'var(--color-success)',
      iconColor: 'var(--color-success)',
      bgColor: '#ECFDF5',
    },
    warning: {
      borderColor: 'var(--color-warning)',
      iconColor: 'var(--color-warning)',
      bgColor: '#FEF3C7',
    },
    info: {
      borderColor: 'var(--color-secondary)',
      iconColor: 'var(--color-secondary)',
      bgColor: 'var(--color-bg-secondary)',
    },
  }

  // 默认图标映射
  const defaultIcons = {
    primary: <CalendarOutlined />,
    success: <TrophyOutlined />,
    warning: <ScheduleOutlined />,
    info: <CheckCircleOutlined />,
  }

  const currentStyle = variantStyles[variant] || variantStyles.primary
  const defaultIcon = defaultIcons[variant] || null

  return (
    <Card
      bordered
      loading={loading}
      style={{
        height: '100%',
        borderLeft: `4px solid ${currentStyle.borderColor}`,
        borderRadius: 'var(--radius-lg)',
        boxShadow: 'var(--shadow-sm)',
        transition: 'var(--transition-base)',
        position: 'relative',
        overflow: 'hidden',
      }}
      bodyStyle={{
        padding: 24,
      }}
      hoverable={!loading}
      onMouseEnter={(e) => {
        if (loading) return
        e.currentTarget.style.boxShadow = 'var(--shadow-lg)'
        e.currentTarget.style.transform = 'translateY(-2px)'
      }}
      onMouseLeave={(e) => {
        if (loading) return
        e.currentTarget.style.boxShadow = 'var(--shadow-sm)'
        e.currentTarget.style.transform = 'translateY(0)'
      }}
    >
      {/* 背景图标装饰 */}
      <div
        style={{
          position: 'absolute',
          top: -20,
          right: -20,
          fontSize: 120,
          color: currentStyle.iconColor,
          opacity: 0.05,
          pointerEvents: 'none',
        }}
      >
        {icon || defaultIcon}
      </div>

      {/* 内容 */}
      <div style={{ position: 'relative', zIndex: 1 }}>
        {/* 标签 */}
        <Text
          style={{
            fontSize: 14,
            color: 'var(--color-text-secondary)',
            display: 'block',
            marginBottom: 12,
          }}
        >
          {label}
        </Text>

        {/* 数值 */}
        <div style={{ display: 'flex', alignItems: 'baseline', gap: 4 }}>
          <span
            style={{
              fontSize: 32,
              fontWeight: 700,
              color: 'var(--color-text-primary)',
              lineHeight: 1,
            }}
          >
            {value}
          </span>
          {unit && (
            <span
              style={{
                fontSize: 16,
                fontWeight: 500,
                color: 'var(--color-text-secondary)',
              }}
            >
              {unit}
            </span>
          )}
        </div>

        {/* 小图标 */}
        {(icon || defaultIcon) && (
          <div
            style={{
              position: 'absolute',
              top: 0,
              right: 0,
              width: 40,
              height: 40,
              borderRadius: 8,
              background: currentStyle.bgColor,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: currentStyle.iconColor,
              fontSize: 18,
            }}
          >
            {icon || defaultIcon}
          </div>
        )}
      </div>
    </Card>
  )
}

export default StatCard
