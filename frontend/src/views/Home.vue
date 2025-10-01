<template>
  <div class="home">
    <!-- 欢迎横幅 -->
    <div class="welcome-banner">
      <div class="banner-content">
        <h1 class="banner-title">瓷路算法</h1>
        <p class="banner-subtitle">龙泉青瓷窑温智能预测系统</p>
        <p class="banner-description">
          融合传统陶瓷工艺与现代AI技术，通过机器学习算法预测窑温曲线和釉面成色，
          帮助青瓷匠人优化烧制工艺，传承千年技艺。
        </p>
        <div class="banner-actions">
          <el-button type="primary" size="large" @click="goToKiln3D">
            <el-icon><View /></el-icon>
            3D窑炉模型
          </el-button>
          <el-button type="success" size="large" @click="goToPrediction">
            <el-icon><MagicStick /></el-icon>
            智能预测
          </el-button>
        </div>
      </div>
    </div>

    <!-- 功能卡片 -->
    <div class="feature-cards">
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="feature in features" :key="feature.id">
          <el-card class="feature-card" @click="handleFeatureClick(feature)">
            <div class="feature-icon">
              <el-icon :size="40">
                <component :is="feature.icon" />
              </el-icon>
            </div>
            <h3 class="feature-title">{{ feature.title }}</h3>
            <p class="feature-description">{{ feature.description }}</p>
            <div class="feature-status">
              <el-tag :type="feature.status === 'active' ? 'success' : 'info'">
                {{ feature.status === 'active' ? '已启用' : '开发中' }}
              </el-tag>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 系统状态 -->
    <div class="system-status">
      <el-card>
        <template #header>
          <div class="card-header">
            <el-icon><Monitor /></el-icon>
            <span>系统状态</span>
          </div>
        </template>
        <el-row :gutter="20">
          <el-col :span="6" v-for="status in systemStatus" :key="status.name">
            <div class="status-item">
              <div class="status-value">{{ status.value }}</div>
              <div class="status-label">{{ status.label }}</div>
              <div class="status-trend" :class="status.trend">
                <el-icon v-if="status.trend === 'up'"><TrendCharts /></el-icon>
                <el-icon v-else-if="status.trend === 'down'"><Bottom /></el-icon>
                <el-icon v-else><Minus /></el-icon>
                {{ status.change }}
              </div>
            </div>
          </el-col>
        </el-row>
      </el-card>
    </div>

    <!-- 最新预测结果 -->
    <div class="recent-predictions">
      <el-card>
        <template #header>
          <div class="card-header">
            <el-icon><DataAnalysis /></el-icon>
            <span>最新预测结果</span>
            <el-button type="text" @click="goToDataAnalysis">查看全部</el-button>
          </div>
        </template>
        <el-table :data="recentPredictions" style="width: 100%">
          <el-table-column prop="batchName" label="批次名称" />
          <el-table-column prop="predictedScore" label="预测评分">
            <template #default="scope">
              <el-tag :type="getScoreType(scope.row.predictedScore)">
                {{ scope.row.predictedScore }}分
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="confidence" label="置信度">
            <template #default="scope">
              {{ (scope.row.confidence * 100).toFixed(1) }}%
            </template>
          </el-table-column>
          <el-table-column prop="predictionTime" label="预测时间" />
          <el-table-column label="操作">
            <template #default="scope">
              <el-button type="text" @click="viewPrediction(scope.row)">查看详情</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { 
  View, MagicStick, Monitor, DataAnalysis, TrendCharts, Bottom, Minus,
  DataBoard, Setting, Document, Camera, Connection
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useWebSocket } from '../utils/websocket'

const router = useRouter()
const { isConnected } = useWebSocket()

// 功能卡片数据
const features = ref([
  {
    id: 1,
    title: '3D窑炉模型',
    description: 'Three.js构建的龙泉窑剖面模型，实时显示火焰流动和温度分布',
    icon: 'View',
    status: 'active',
    route: '/kiln-3d'
  },
  {
    id: 2,
    title: '智能预测',
    description: '基于LightGBM的成色预测，准确率85%+，预测最佳升温曲线',
    icon: 'MagicStick',
    status: 'active',
    route: '/prediction'
  },
  {
    id: 3,
    title: '实时监控',
    description: 'WebSocket实时推送窑温数据，手机扫码远程监控',
    icon: 'Monitor',
    status: 'active',
    route: '/monitoring'
  },
  {
    id: 4,
    title: '数据分析',
    description: 'ECharts可视化分析，温差云图，成色概率分布',
    icon: 'DataBoard',
    status: 'active',
    route: '/data-analysis'
  },
  {
    id: 5,
    title: '批次管理',
    description: '管理烧制批次，记录胎土配方、匣钵厚度等参数',
    icon: 'Document',
    status: 'active',
    route: '/batch-management'
  },
  {
    id: 6,
    title: '图像分析',
    description: 'AI图像分析，缺陷检测，成色评估',
    icon: 'Camera',
    status: 'developing',
    route: '/image-analysis'
  }
])

// 系统状态数据
const systemStatus = ref([
  { name: 'activeBatches', label: '活跃批次', value: '3', trend: 'up', change: '+1' },
  { name: 'totalPredictions', label: '总预测数', value: '127', trend: 'up', change: '+5' },
  { name: 'accuracy', label: '预测准确率', value: '87.3%', trend: 'up', change: '+2.1%' },
  { name: 'systemUptime', label: '系统运行', value: '99.8%', trend: 'stable', change: '0%' }
])

// 最新预测结果
const recentPredictions = ref([
  {
    id: 1,
    batchName: '龙泉青瓷批次_001',
    predictedScore: 87,
    confidence: 0.92,
    predictionTime: '2024-01-15 14:30:25'
  },
  {
    id: 2,
    batchName: '龙泉青瓷批次_002',
    predictedScore: 82,
    confidence: 0.88,
    predictionTime: '2024-01-15 13:45:12'
  },
  {
    id: 3,
    batchName: '龙泉青瓷批次_003',
    predictedScore: 91,
    confidence: 0.95,
    predictionTime: '2024-01-15 12:20:08'
  }
])

// 方法
const goToKiln3D = () => {
  router.push('/kiln-3d')
}

const goToPrediction = () => {
  ElMessage.info('智能预测功能开发中...')
}

const goToDataAnalysis = () => {
  router.push('/data-analysis')
}

const handleFeatureClick = (feature) => {
  if (feature.status === 'active') {
    if (feature.route) {
      router.push(feature.route)
    }
  } else {
    ElMessage.info(`${feature.title}功能开发中...`)
  }
}

const getScoreType = (score) => {
  if (score >= 90) return 'success'
  if (score >= 80) return 'warning'
  return 'danger'
}

const viewPrediction = (prediction) => {
  ElMessage.info(`查看预测详情: ${prediction.batchName}`)
}

// 生命周期
onMounted(() => {
  // 初始化数据
  console.log('首页加载完成')
})
</script>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
}

.welcome-banner {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(255, 255, 255, 0.7) 100%);
  border-radius: 20px;
  padding: 60px 40px;
  margin-bottom: 40px;
  text-align: center;
  backdrop-filter: blur(10px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.banner-title {
  font-size: 48px;
  font-weight: bold;
  color: #333;
  margin: 0 0 10px 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.banner-subtitle {
  font-size: 24px;
  color: #666;
  margin: 0 0 20px 0;
}

.banner-description {
  font-size: 16px;
  color: #888;
  line-height: 1.6;
  margin: 0 0 40px 0;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.banner-actions {
  display: flex;
  gap: 20px;
  justify-content: center;
}

.feature-cards {
  margin-bottom: 40px;
}

.feature-card {
  height: 200px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
}

.feature-icon {
  text-align: center;
  margin-bottom: 15px;
  color: #667eea;
}

.feature-title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin: 0 0 10px 0;
  text-align: center;
}

.feature-description {
  font-size: 14px;
  color: #666;
  line-height: 1.4;
  margin: 0 0 15px 0;
  text-align: center;
}

.feature-status {
  text-align: center;
}

.system-status {
  margin-bottom: 40px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: bold;
  color: #333;
}

.status-item {
  text-align: center;
  padding: 20px;
  background: linear-gradient(135deg, #f8f9ff 0%, #f0f2ff 100%);
  border-radius: 10px;
  border: 1px solid #e8ecff;
}

.status-value {
  font-size: 28px;
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

.status-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 10px;
}

.status-trend {
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 3px;
}

.status-trend.up {
  color: #67c23a;
}

.status-trend.down {
  color: #f56c6c;
}

.status-trend.stable {
  color: #909399;
}

.recent-predictions {
  margin-bottom: 40px;
}

@media (max-width: 768px) {
  .banner-title {
    font-size: 36px;
  }
  
  .banner-subtitle {
    font-size: 20px;
  }
  
  .banner-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .feature-card {
    height: auto;
    min-height: 180px;
  }
}
</style>
