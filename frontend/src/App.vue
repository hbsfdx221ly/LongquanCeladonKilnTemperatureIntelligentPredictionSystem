<template>
  <div id="app">
    <el-container class="app-container">
      <!-- 顶部导航栏 -->
    <el-header class="app-header">
        <div class="header-content">
          <div class="logo">
            <el-icon class="logo-icon"><Monitor /></el-icon>
            <span class="logo-text">瓷路算法</span>
            <span class="logo-subtitle">龙泉青瓷窑温智能预测系统</span>
          </div>
          
          <div class="header-actions">
            <el-button 
              type="primary" 
              :icon="Monitor" 
              @click="showMonitoring = true"
            >
              实时监控
            </el-button>
            <el-button 
              type="success" 
              :icon="DataAnalysis" 
              @click="showPrediction = true"
            >
              智能预测
            </el-button>
            <el-button 
              type="info" 
              :icon="Camera" 
              @click="showQRCode = true"
            >
              扫码监控
            </el-button>
          </div>
        </div>
      </el-header>

      <!-- 主要内容区域 -->
      <el-main class="app-main">
        <router-view />
      </el-main>

      <!-- 底部信息栏 -->
      <el-footer class="app-footer">
        <div class="footer-content">
          <span>© 2024 瓷路算法 - 传统技艺 × 大数据</span>
          <span class="footer-status">
            <el-icon :class="connectionStatus ? 'status-online' : 'status-offline'">
              <Connection />
            </el-icon>
            {{ connectionStatus ? '系统在线' : '系统离线' }}
          </span>
        </div>
      </el-footer>
    </el-container>

    <!-- 实时监控弹窗 -->
    <el-dialog
      v-model="showMonitoring"
      title="窑温实时监控"
      width="90%"
      :before-close="handleCloseMonitoring"
    >
      <MonitoringPanel @close="showMonitoring = false" />
    </el-dialog>

    <!-- 智能预测弹窗 -->
    <el-dialog
      v-model="showPrediction"
      title="智能成色预测"
      width="80%"
      :before-close="handleClosePrediction"
    >
      <PredictionPanel @close="showPrediction = false" />
    </el-dialog>

    <!-- 扫码监控弹窗 -->
    <el-dialog
      v-model="showQRCode"
      title="手机扫码监控"
      width="400px"
      :before-close="handleCloseQRCode"
    >
      <QRCodePanel @close="showQRCode = false" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { Monitor, DataAnalysis, Camera, Connection } from '@element-plus/icons-vue'
import MonitoringPanel from './components/MonitoringPanel.vue'
import PredictionPanel from './components/PredictionPanel.vue'
import QRCodePanel from './components/QRCodePanel.vue'
import { useWebSocket } from './utils/websocket'

// 响应式数据
const showMonitoring = ref(false)
const showPrediction = ref(false)
const showQRCode = ref(false)
const connectionStatus = ref(false)

// WebSocket连接
const { connect, disconnect, isConnected } = useWebSocket()

// 生命周期
onMounted(() => {
  // 初始化WebSocket连接
  connect()
  connectionStatus.value = isConnected.value
})

onUnmounted(() => {
  disconnect()
})

// 监听连接状态变化
watch(isConnected, (newStatus) => {
  connectionStatus.value = newStatus
})

// 事件处理
const handleCloseMonitoring = () => {
  showMonitoring.value = false
}

const handleClosePrediction = () => {
  showPrediction.value = false
}

const handleCloseQRCode = () => {
  showQRCode.value = false
}
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.app-header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
  padding: 0;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  padding: 0 20px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-icon {
  font-size: 32px;
  color: #667eea;
}

.logo-text {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.logo-subtitle {
  font-size: 14px;
  color: #666;
  margin-left: 10px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.app-main {
  padding: 20px;
  min-height: calc(100vh - 120px);
}

.app-footer {
  background: rgba(0, 0, 0, 0.8);
  color: white;
  height: 60px;
  padding: 0;
}

.footer-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  padding: 0 20px;
}

.footer-status {
  display: flex;
  align-items: center;
  gap: 5px;
}

.status-online {
  color: #67c23a;
}

.status-offline {
  color: #f56c6c;
}
</style>
