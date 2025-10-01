<template>
  <div class="monitoring-panel">
    <!-- 实时数据概览 -->
    <el-row :gutter="20" class="mb-20">
      <el-col :span="6" v-for="metric in realtimeMetrics" :key="metric.key">
        <el-card class="metric-card">
          <div class="metric-content">
            <div class="metric-icon">
              <el-icon :size="24">
                <component :is="metric.icon" />
              </el-icon>
            </div>
            <div class="metric-info">
              <div class="metric-value">{{ metric.value }}</div>
              <div class="metric-label">{{ metric.label }}</div>
              <div class="metric-trend" :class="metric.trend">
                <el-icon v-if="metric.trend === 'up'"><TrendCharts /></el-icon>
                <el-icon v-else-if="metric.trend === 'down'"><Bottom /></el-icon>
                <el-icon v-else><Minus /></el-icon>
                {{ metric.change }}
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 温度曲线图 -->
    <el-card class="chart-card mb-20">
      <template #header>
        <div class="card-header">
          <el-icon><TrendCharts /></el-icon>
          <span>实时温度曲线</span>
          <div class="header-actions">
            <el-button-group>
              <el-button 
                :type="isRealtime ? 'primary' : 'default'"
                @click="toggleRealtime"
              >
                {{ isRealtime ? '实时' : '历史' }}
              </el-button>
              <el-button @click="refreshChart">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </el-button-group>
          </div>
        </div>
      </template>
      
      <div ref="temperatureChart" class="chart-container"></div>
    </el-card>

    <!-- 窑位温度分布 -->
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card class="heatmap-card">
          <template #header>
            <div class="card-header">
              <el-icon><Grid /></el-icon>
              <span>窑位温度分布</span>
            </div>
          </template>
          
          <div ref="heatmapChart" class="heatmap-container"></div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card class="atmosphere-card">
          <template #header>
            <div class="card-header">
              <el-icon><WindPower /></el-icon>
              <span>窑内气氛</span>
            </div>
          </template>
          
          <div class="atmosphere-metrics">
            <div class="atmosphere-item" v-for="item in atmosphereData" :key="item.key">
              <div class="atmosphere-label">{{ item.label }}</div>
              <div class="atmosphere-value">{{ item.value }}</div>
              <div class="atmosphere-progress">
                <el-progress 
                  :percentage="item.percentage" 
                  :color="item.color"
                  :show-text="false"
                />
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { 
  TrendCharts, Bottom, Minus, Refresh, Grid, WindPower
} from '@element-plus/icons-vue'
import { useWebSocket } from '../utils/websocket'

// 响应式数据
const temperatureChart = ref(null)
const heatmapChart = ref(null)
const isRealtime = ref(true)
const chartInstance = ref(null)
const heatmapInstance = ref(null)

// WebSocket连接
const { on, off, requestMonitoring } = useWebSocket()

// 实时指标数据
const realtimeMetrics = ref([
  {
    key: 'temperature',
    label: '当前温度',
    value: '1200°C',
    trend: 'up',
    change: '+5°C',
    icon: 'TrendCharts'
  },
  {
    key: 'oxygen',
    label: '氧气浓度',
    value: '18.2%',
    trend: 'stable',
    change: '0%',
    icon: 'WindPower'
  },
  {
    key: 'pressure',
    label: '窑内压力',
    value: '101.5kPa',
    trend: 'down',
    change: '-0.2kPa',
    icon: 'Grid'
  },
  {
    key: 'humidity',
    label: '湿度',
    value: '45%',
    trend: 'up',
    change: '+2%',
    icon: 'Water'
  }
])

// 气氛数据
const atmosphereData = ref([
  {
    key: 'oxygen',
    label: '氧气浓度',
    value: '18.2%',
    percentage: 91,
    color: '#67c23a'
  },
  {
    key: 'co',
    label: '一氧化碳',
    value: '50ppm',
    percentage: 25,
    color: '#e6a23c'
  },
  {
    key: 'co2',
    label: '二氧化碳',
    value: '2.1%',
    percentage: 42,
    color: '#f56c6c'
  }
])

// 温度数据
const temperatureData = ref([])
const timeLabels = ref([])

// 生命周期
onMounted(async () => {
  await nextTick()
  initCharts()
  startRealtimeMonitoring()
  
  // 监听WebSocket消息
  on('sensor_data', handleSensorData)
})

onUnmounted(() => {
  stopRealtimeMonitoring()
  off('sensor_data', handleSensorData)
  
  if (chartInstance.value) {
    chartInstance.value.dispose()
  }
  if (heatmapInstance.value) {
    heatmapInstance.value.dispose()
  }
})

// 初始化图表
const initCharts = () => {
  initTemperatureChart()
  initHeatmapChart()
}

// 初始化温度曲线图
const initTemperatureChart = () => {
  if (!temperatureChart.value) return
  
  chartInstance.value = echarts.init(temperatureChart.value)
  
  const option = {
    title: {
      text: '窑温实时监控',
      left: 'center',
      textStyle: {
        color: '#333',
        fontSize: 16
      }
    },
    tooltip: {
      trigger: 'axis',
      formatter: function(params) {
        const data = params[0]
        return `${data.name}<br/>温度: ${data.value}°C`
      }
    },
    xAxis: {
      type: 'category',
      data: timeLabels.value,
      axisLabel: {
        color: '#666'
      }
    },
    yAxis: {
      type: 'value',
      name: '温度(°C)',
      min: 0,
      max: 1400,
      axisLabel: {
        color: '#666',
        formatter: '{value}°C'
      },
      splitLine: {
        lineStyle: {
          color: '#f0f0f0'
        }
      }
    },
    series: [{
      name: '温度',
      type: 'line',
      data: temperatureData.value,
      smooth: true,
      lineStyle: {
        color: '#667eea',
        width: 3
      },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(102, 126, 234, 0.3)' },
            { offset: 1, color: 'rgba(102, 126, 234, 0.1)' }
          ]
        }
      },
      markLine: {
        data: [
          { yAxis: 1200, name: '目标温度', lineStyle: { color: '#f56c6c', type: 'dashed' } }
        ]
      }
    }],
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    }
  }
  
  chartInstance.value.setOption(option)
}

// 初始化热力图
const initHeatmapChart = () => {
  if (!heatmapChart.value) return
  
  heatmapInstance.value = echarts.init(heatmapChart.value)
  
  // 生成热力图数据
  const data = []
  for (let i = 0; i < 5; i++) {
    for (let j = 0; j < 5; j++) {
      const value = Math.random() * 200 + 1000 // 1000-1200度
      data.push([j, i, value])
    }
  }
  
  const option = {
    title: {
      text: '窑位温度分布',
      left: 'center',
      textStyle: {
        color: '#333',
        fontSize: 14
      }
    },
    tooltip: {
      position: 'top',
      formatter: function(params) {
        return `位置: (${params.data[0]}, ${params.data[1]})<br/>温度: ${params.data[2]}°C`
      }
    },
    grid: {
      height: '50%',
      top: '10%'
    },
    xAxis: {
      type: 'category',
      data: ['A', 'B', 'C', 'D', 'E'],
      splitArea: {
        show: true
      }
    },
    yAxis: {
      type: 'category',
      data: ['1', '2', '3', '4', '5'],
      splitArea: {
        show: true
      }
    },
    visualMap: {
      min: 1000,
      max: 1300,
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: '15%',
      inRange: {
        color: ['#4A90E2', '#7ED321', '#F5A623', '#FF6B6B', '#FF2D92']
      }
    },
    series: [{
      name: '温度',
      type: 'heatmap',
      data: data,
      label: {
        show: true,
        formatter: function(params) {
          return params.data[2] + '°C'
        }
      },
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }]
  }
  
  heatmapInstance.value.setOption(option)
}

// 开始实时监控
const startRealtimeMonitoring = () => {
  // 模拟实时数据更新
  setInterval(() => {
    if (isRealtime.value) {
      updateRealtimeData()
    }
  }, 2000)
}

// 停止实时监控
const stopRealtimeMonitoring = () => {
  // 清理定时器
}

// 更新实时数据
const updateRealtimeData = () => {
  const now = new Date()
  const timeLabel = now.toLocaleTimeString()
  const temperature = 1200 + Math.random() * 100 - 50
  
  // 更新温度数据
  temperatureData.value.push(temperature)
  timeLabels.value.push(timeLabel)
  
  // 保持最近50个数据点
  if (temperatureData.value.length > 50) {
    temperatureData.value.shift()
    timeLabels.value.shift()
  }
  
  // 更新图表
  if (chartInstance.value) {
    chartInstance.value.setOption({
      xAxis: { data: timeLabels.value },
      series: [{ data: temperatureData.value }]
    })
  }
  
  // 更新实时指标
  updateRealtimeMetrics(temperature)
}

// 更新实时指标
const updateRealtimeMetrics = (temperature) => {
  realtimeMetrics.value[0].value = `${Math.round(temperature)}°C`
  realtimeMetrics.value[0].change = temperature > 1200 ? '+5°C' : '-3°C'
  realtimeMetrics.value[0].trend = temperature > 1200 ? 'up' : 'down'
}

// 处理传感器数据
const handleSensorData = (data) => {
  console.log('收到传感器数据:', data)
  // 更新界面数据
}

// 切换实时/历史模式
const toggleRealtime = () => {
  isRealtime.value = !isRealtime.value
}

// 刷新图表
const refreshChart = () => {
  if (chartInstance.value) {
    chartInstance.value.resize()
  }
  if (heatmapInstance.value) {
    heatmapInstance.value.resize()
  }
}
</script>

<style scoped>
.monitoring-panel {
  padding: 20px;
}

.metric-card {
  background: rgba(255, 255, 255, 0.9);
  border: none;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  border-radius: 12px;
}

.metric-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.metric-icon {
  color: #667eea;
}

.metric-info {
  flex: 1;
}

.metric-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

.metric-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.metric-trend {
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 3px;
}

.metric-trend.up {
  color: #67c23a;
}

.metric-trend.down {
  color: #f56c6c;
}

.metric-trend.stable {
  color: #909399;
}

.chart-card {
  background: rgba(255, 255, 255, 0.9);
  border: none;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  border-radius: 12px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: bold;
  color: #333;
}

.header-actions {
  margin-left: auto;
}

.chart-container {
  height: 400px;
  width: 100%;
}

.heatmap-card,
.atmosphere-card {
  background: rgba(255, 255, 255, 0.9);
  border: none;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  border-radius: 12px;
}

.heatmap-container {
  height: 300px;
  width: 100%;
}

.atmosphere-metrics {
  padding: 20px 0;
}

.atmosphere-item {
  margin-bottom: 20px;
}

.atmosphere-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.atmosphere-value {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin-bottom: 10px;
}

.atmosphere-progress {
  margin-top: 5px;
}

@media (max-width: 768px) {
  .monitoring-panel {
    padding: 10px;
  }
  
  .chart-container {
    height: 300px;
  }
  
  .heatmap-container {
    height: 250px;
  }
}
</style>
