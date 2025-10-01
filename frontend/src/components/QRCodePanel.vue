<template>
  <div class="qrcode-panel">
    <div class="qrcode-content">
      <!-- 二维码显示 -->
      <div class="qrcode-container">
        <div ref="qrcodeElement" class="qrcode-display"></div>
        <div class="qrcode-info">
          <h3>手机扫码监控</h3>
          <p>使用手机扫描二维码即可远程监控窑温</p>
        </div>
      </div>
      
      <!-- 监控链接 -->
      <div class="monitoring-link">
        <el-input 
          v-model="monitoringUrl" 
          readonly 
          placeholder="监控链接"
        >
          <template #append>
            <el-button @click="copyLink">
              <el-icon><CopyDocument /></el-icon>
              复制
            </el-button>
          </template>
        </el-input>
      </div>
      
      <!-- 功能说明 -->
      <div class="features-list">
        <h4>移动端功能</h4>
        <ul>
          <li>
            <el-icon><Monitor /></el-icon>
            实时温度监控
          </li>
          <li>
            <el-icon><Bell /></el-icon>
            异常报警推送
          </li>
          <li>
            <el-icon><DataAnalysis /></el-icon>
            预测结果查看
          </li>
          <li>
            <el-icon><Camera /></el-icon>
            图像上传分析
          </li>
        </ul>
      </div>
      
      <!-- 操作按钮 -->
      <div class="action-buttons">
        <el-button type="primary" @click="refreshQRCode">
          <el-icon><Refresh /></el-icon>
          刷新二维码
        </el-button>
        <el-button @click="downloadQRCode">
          <el-icon><Download /></el-icon>
          下载二维码
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import QRCode from 'qrcode'
import { 
  CopyDocument, Monitor, Bell, DataAnalysis, Camera, 
  Refresh, Download 
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// 响应式数据
const qrcodeElement = ref(null)
const monitoringUrl = ref('')
const qrCodeInstance = ref(null)

// 生命周期
onMounted(() => {
  generateMonitoringUrl()
  generateQRCode()
})

onUnmounted(() => {
  // 清理资源
})

// 生成监控链接
const generateMonitoringUrl = () => {
  const baseUrl = window.location.origin
  const mobilePath = '/mobile-monitoring'
  monitoringUrl.value = `${baseUrl}${mobilePath}`
}

// 生成二维码
const generateQRCode = async () => {
  try {
    if (!qrcodeElement.value) return
    
    // 清除现有二维码
    qrcodeElement.value.innerHTML = ''
    
    // 生成二维码
    const canvas = await QRCode.toCanvas(monitoringUrl.value, {
      width: 200,
      margin: 2,
      color: {
        dark: '#333333',
        light: '#FFFFFF'
      }
    })
    
    // 添加到DOM
    qrcodeElement.value.appendChild(canvas)
    
    // 保存实例用于下载
    qrCodeInstance.value = canvas
    
    ElMessage.success('二维码生成成功')
    
  } catch (error) {
    console.error('二维码生成失败:', error)
    ElMessage.error('二维码生成失败')
  }
}

// 复制链接
const copyLink = async () => {
  try {
    await navigator.clipboard.writeText(monitoringUrl.value)
    ElMessage.success('链接已复制到剪贴板')
  } catch (error) {
    console.error('复制失败:', error)
    ElMessage.error('复制失败，请手动复制')
  }
}

// 刷新二维码
const refreshQRCode = () => {
  generateQRCode()
}

// 下载二维码
const downloadQRCode = () => {
  if (!qrCodeInstance.value) {
    ElMessage.warning('二维码未生成')
    return
  }
  
  try {
    // 创建下载链接
    const link = document.createElement('a')
    link.download = '瓷路算法-监控二维码.png'
    link.href = qrCodeInstance.value.toDataURL()
    
    // 触发下载
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    ElMessage.success('二维码下载成功')
    
  } catch (error) {
    console.error('下载失败:', error)
    ElMessage.error('下载失败')
  }
}
</script>

<style scoped>
.qrcode-panel {
  padding: 20px;
}

.qrcode-content {
  text-align: center;
}

.qrcode-container {
  margin-bottom: 30px;
}

.qrcode-display {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
  padding: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.qrcode-info h3 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 18px;
}

.qrcode-info p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.monitoring-link {
  margin-bottom: 30px;
}

.features-list {
  margin-bottom: 30px;
  text-align: left;
}

.features-list h4 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 16px;
  text-align: center;
}

.features-list ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.features-list li {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 0;
  color: #666;
  font-size: 14px;
}

.features-list li .el-icon {
  color: #667eea;
  font-size: 16px;
}

.action-buttons {
  display: flex;
  gap: 15px;
  justify-content: center;
}

@media (max-width: 768px) {
  .qrcode-panel {
    padding: 10px;
  }
  
  .qrcode-display {
    padding: 15px;
  }
  
  .action-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  .action-buttons .el-button {
    width: 100%;
    max-width: 200px;
  }
}
</style>
