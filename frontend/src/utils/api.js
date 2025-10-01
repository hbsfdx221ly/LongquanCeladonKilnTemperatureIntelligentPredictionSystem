/**
 * API工具类
 */

import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建axios实例
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 可以在这里添加认证token等
    console.log('发送请求:', config.method?.toUpperCase(), config.url)
    return config
  },
  (error) => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    const { data } = response
    
    // 检查业务状态
    if (data.success === false) {
      ElMessage.error(data.error || '请求失败')
      return Promise.reject(new Error(data.error || '请求失败'))
    }
    
    return data
  },
  (error) => {
    console.error('响应错误:', error)
    
    let message = '网络错误'
    if (error.response) {
      const { status, data } = error.response
      switch (status) {
        case 400:
          message = data.error || '请求参数错误'
          break
        case 401:
          message = '未授权，请重新登录'
          break
        case 403:
          message = '权限不足'
          break
        case 404:
          message = '请求的资源不存在'
          break
        case 500:
          message = '服务器内部错误'
          break
        default:
          message = data.error || `请求失败 (${status})`
      }
    } else if (error.code === 'ECONNABORTED') {
      message = '请求超时'
    }
    
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

// 批次管理API
export const batchAPI = {
  // 获取批次列表
  getBatches: (params = {}) => {
    return api.get('/batches', { params })
  },
  
  // 获取单个批次
  getBatch: (id) => {
    return api.get(`/batches/${id}`)
  },
  
  // 创建批次
  createBatch: (data) => {
    return api.post('/batches', data)
  },
  
  // 更新批次
  updateBatch: (id, data) => {
    return api.put(`/batches/${id}`, data)
  },
  
  // 删除批次
  deleteBatch: (id) => {
    return api.delete(`/batches/${id}`)
  },
  
  // 开始烧制
  startBatch: (id) => {
    return api.post(`/batches/${id}/start`)
  },
  
  // 完成烧制
  completeBatch: (id) => {
    return api.post(`/batches/${id}/complete`)
  },
  
  // 获取批次汇总
  getBatchSummary: (id) => {
    return api.get(`/batches/${id}/summary`)
  }
}

// 预测管理API
export const predictionAPI = {
  // 获取预测列表
  getPredictions: (params = {}) => {
    return api.get('/predictions', { params })
  },
  
  // 获取单个预测
  getPrediction: (id) => {
    return api.get(`/predictions/${id}`)
  },
  
  // 执行预测
  predictBatch: (batchId) => {
    return api.post('/predictions/predict', { batch_id: batchId })
  },
  
  // 获取批次预测历史
  getBatchPredictions: (batchId) => {
    return api.get(`/predictions/batch/${batchId}`)
  },
  
  // 提交预测反馈
  submitFeedback: (predictionId, data) => {
    return api.post(`/predictions/${predictionId}/feedback`, data)
  },
  
  // 获取预测准确率
  getAccuracy: () => {
    return api.get('/predictions/accuracy')
  },
  
  // 获取特征重要性
  getFeatureImportance: () => {
    return api.get('/predictions/features/importance')
  }
}

// 传感器数据API
export const sensorAPI = {
  // 获取传感器数据
  getSensorData: (params = {}) => {
    return api.get('/sensor-data', { params })
  },
  
  // 添加传感器数据
  addSensorData: (data) => {
    return api.post('/sensor-data', data)
  },
  
  // 获取最新传感器数据
  getLatestSensorData: (batchId) => {
    return api.get(`/sensor-data/batch/${batchId}/latest`)
  },
  
  // 获取温度曲线
  getTemperatureCurve: (batchId, hours = 24) => {
    return api.get(`/sensor-data/batch/${batchId}/temperature-curve`, {
      params: { hours }
    })
  },
  
  // 获取温度热力图
  getTemperatureHeatmap: (batchId) => {
    return api.get(`/sensor-data/batch/${batchId}/heatmap`)
  },
  
  // 获取传感器统计
  getSensorStatistics: (batchId, hours = 24) => {
    return api.get(`/sensor-data/batch/${batchId}/statistics`, {
      params: { hours }
    })
  }
}

// 图像管理API
export const imageAPI = {
  // 获取图像列表
  getImages: (params = {}) => {
    return api.get('/images', { params })
  },
  
  // 获取单个图像
  getImage: (id) => {
    return api.get(`/images/${id}`)
  },
  
  // 获取图像文件
  getImageFile: (id) => {
    return api.get(`/images/${id}/file`, { responseType: 'blob' })
  },
  
  // 上传图像
  uploadImage: (formData) => {
    return api.post('/images', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },
  
  // 更新图像信息
  updateImage: (id, data) => {
    return api.put(`/images/${id}`, data)
  },
  
  // 删除图像
  deleteImage: (id) => {
    return api.delete(`/images/${id}`)
  },
  
  // 分析图像
  analyzeImage: (id) => {
    return api.post(`/images/${id}/analysis`)
  },
  
  // 获取烧制前后对比
  getBeforeAfterImages: (batchId) => {
    return api.get(`/images/batch/${batchId}/before-after`)
  }
}

// 系统API
export const systemAPI = {
  // 获取系统状态
  getHealth: () => {
    return api.get('/health')
  },
  
  // 获取系统信息
  getInfo: () => {
    return api.get('/')
  }
}

export default api
