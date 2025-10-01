/**
 * WebSocket工具类
 */

import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { io } from 'socket.io-client'

// WebSocket连接状态
const isConnected = ref(false)
const socket = ref(null)
const reconnectAttempts = ref(0)
const maxReconnectAttempts = 5
const reconnectInterval = ref(5000)

// 事件监听器
const listeners = reactive({})

export function useWebSocket() {
  
  /**
   * 连接WebSocket
   */
  const connect = () => {
    try {
      const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'
      socket.value = io(baseUrl, {
        path: '/socket.io',
        transports: ['websocket'],
        reconnection: true,
        reconnectionAttempts: maxReconnectAttempts,
      })

      socket.value.on('connect', () => {
        console.log('Socket.IO 已连接')
        isConnected.value = true
        reconnectAttempts.value = 0
        ElMessage.success('实时连接已建立')
      })

      socket.value.on('disconnect', () => {
        console.log('Socket.IO 已断开')
        isConnected.value = false
      })

      // 后端事件转发到本地事件系统
      const bind = (eventName) => {
        socket.value.on(eventName, (payload) => trigger(eventName, payload))
      }
      ;[
        'status',
        'sensor_data',
        'prediction_result',
        'prediction_error',
        'monitoring_error',
      ].forEach(bind)

      socket.value.on('connect_error', (err) => {
        console.error('Socket.IO 连接错误:', err?.message || err)
        attemptReconnect()
      })
    } catch (error) {
      console.error('Socket.IO 初始化失败:', error)
      ElMessage.error('无法建立实时连接')
    }
  }
  
  /**
   * 断开WebSocket连接
   */
  const disconnect = () => {
    if (socket.value) {
      socket.value.close()
      socket.value = null
    }
    isConnected.value = false
  }
  
  /**
   * 尝试重连
   */
  const attemptReconnect = () => {
    if (reconnectAttempts.value < maxReconnectAttempts) {
      reconnectAttempts.value++
      console.log(`尝试重连 (${reconnectAttempts.value}/${maxReconnectAttempts})`)
      
      setTimeout(() => {
        connect()
      }, reconnectInterval.value)
    } else {
      console.log('达到最大重连次数，停止重连')
      ElMessage.error('连接失败，请刷新页面重试')
    }
  }
  
  /**
   * 发送消息
   */
  const emit = (eventName, payload) => {
    if (!socket.value || !isConnected.value) {
      console.warn('Socket 未连接，无法发送')
      return false
    }
    try {
      socket.value.emit(eventName, payload)
      return true
    } catch (error) {
      console.error('Socket 发送失败:', error)
      return false
    }
  }
  
  /**
   * 处理接收到的消息
   */
  const trigger = (type, payload) => {
    if (listeners[type]) {
      listeners[type].forEach((callback) => {
        try {
          callback(payload)
        } catch (error) {
          console.error(`事件监听器执行失败 (${type}):`, error)
        }
      })
    }
    // 内置处理
    if (type === 'sensor_data') handleSensorData(payload)
    if (type === 'prediction_result') handlePredictionResult(payload)
    if (type === 'prediction_error') handlePredictionError(payload)
    if (type === 'monitoring_error') handleMonitoringError(payload)
  }
  
  /**
   * 处理传感器数据
   */
  const handleSensorData = (data) => {
    console.log('收到传感器数据:', data)
    // 可以在这里更新全局状态或触发其他操作
  }
  
  /**
   * 处理预测结果
   */
  const handlePredictionResult = (data) => {
    console.log('收到预测结果:', data)
    ElMessage.success(`预测完成: 成色评分 ${data.predicted_score} 分`)
  }
  
  /**
   * 处理预测错误
   */
  const handlePredictionError = (data) => {
    console.error('预测错误:', data)
    ElMessage.error(`预测失败: ${data.error}`)
  }
  
  /**
   * 处理监控错误
   */
  const handleMonitoringError = (data) => {
    console.error('监控错误:', data)
    ElMessage.error(`监控失败: ${data.error}`)
  }
  
  /**
   * 添加事件监听器
   */
  const on = (eventType, callback) => {
    if (!listeners[eventType]) {
      listeners[eventType] = []
    }
    listeners[eventType].push(callback)
    
    // 返回取消监听的函数
    return () => {
      const index = listeners[eventType].indexOf(callback)
      if (index > -1) {
        listeners[eventType].splice(index, 1)
      }
    }
  }
  
  /**
   * 移除事件监听器
   */
  const off = (eventType, callback) => {
    if (listeners[eventType]) {
      const index = listeners[eventType].indexOf(callback)
      if (index > -1) {
        listeners[eventType].splice(index, 1)
      }
    }
  }
  
  /**
   * 请求预测
   */
  const requestPrediction = (batchId) => emit('request_prediction', { batch_id: batchId })
  
  /**
   * 请求监控数据
   */
  const requestMonitoring = (batchId) => emit('request_monitoring', { batch_id: batchId })
  
  return {
    isConnected,
    connect,
    disconnect,
    emit,
    on,
    off,
    requestPrediction,
    requestMonitoring
  }
}
