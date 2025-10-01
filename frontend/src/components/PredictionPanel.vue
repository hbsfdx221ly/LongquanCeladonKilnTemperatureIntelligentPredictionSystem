<template>
  <div class="prediction-panel">
    <!-- 预测表单 -->
    <el-card class="prediction-form-card mb-20">
      <template #header>
        <div class="card-header">
          <el-icon><MagicStick /></el-icon>
          <span>智能成色预测</span>
        </div>
      </template>
      
      <el-form 
        ref="predictionForm" 
        :model="predictionForm" 
        :rules="predictionRules"
        label-width="120px"
        class="prediction-form"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="批次名称" prop="batchName">
              <el-input v-model="predictionForm.batchName" placeholder="请输入批次名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="窑位位置" prop="kilnPosition">
              <el-select v-model="predictionForm.kilnPosition" placeholder="请选择窑位">
                <el-option label="窑位 A" value="窑位_A" />
                <el-option label="窑位 B" value="窑位_B" />
                <el-option label="窑位 C" value="窑位_C" />
                <el-option label="窑位 D" value="窑位_D" />
                <el-option label="窑位 E" value="窑位_E" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="匣钵厚度(mm)" prop="saggerThickness">
              <el-input-number 
                v-model="predictionForm.saggerThickness" 
                :min="1" 
                :max="10" 
                :step="0.1"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="木炭用量(kg)" prop="charcoalAmount">
              <el-input-number 
                v-model="predictionForm.charcoalAmount" 
                :min="10" 
                :max="500" 
                :step="5"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="胎土配方" prop="clayRatio">
          <div class="clay-ratio-container">
            <el-row :gutter="10">
              <el-col :span="6" v-for="(item, index) in clayRatioItems" :key="index">
                <div class="clay-ratio-item">
                  <label>{{ item.label }}</label>
                  <el-input-number 
                    v-model="predictionForm.clayRatio[item.key]"
                    :min="0"
                    :max="1"
                    :step="0.01"
                    :precision="2"
                    size="small"
                  />
                </div>
              </el-col>
            </el-row>
            <div class="ratio-total">
              总和: {{ totalRatio.toFixed(2) }}
              <el-tag :type="totalRatio === 1 ? 'success' : 'warning'" size="small">
                {{ totalRatio === 1 ? '正常' : '需调整' }}
              </el-tag>
            </div>
          </div>
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            @click="submitPrediction"
            :loading="predicting"
            size="large"
          >
            <el-icon><MagicStick /></el-icon>
            {{ predicting ? '预测中...' : '开始预测' }}
          </el-button>
          <el-button @click="resetForm" size="large">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 预测结果 -->
    <el-card v-if="predictionResult" class="prediction-result-card">
      <template #header>
        <div class="card-header">
          <el-icon><DataAnalysis /></el-icon>
          <span>预测结果</span>
          <el-tag :type="getScoreType(predictionResult.predicted_score)" size="large">
            {{ predictionResult.predicted_score }}分
          </el-tag>
        </div>
      </template>
      
      <div class="result-content">
        <!-- 预测评分 -->
        <div class="score-section">
          <div class="score-display">
            <div class="score-circle">
              <div class="score-value">{{ predictionResult.predicted_score }}</div>
              <div class="score-label">预测评分</div>
            </div>
            <div class="score-info">
              <div class="confidence">
                <span class="label">置信度:</span>
                <span class="value">{{ (predictionResult.confidence * 100).toFixed(1) }}%</span>
              </div>
              <div class="model-version">
                <span class="label">模型版本:</span>
                <span class="value">{{ predictionResult.model_version }}</span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 成色概率分布 -->
        <div class="color-probability-section">
          <h4>成色概率分布</h4>
          <div class="color-bars">
            <div 
              v-for="(prob, color) in colorProbability" 
              :key="color"
              class="color-bar"
            >
              <div class="color-label">{{ color }}</div>
              <div class="color-progress">
                <el-progress 
                  :percentage="prob * 100" 
                  :color="getColorBarColor(color)"
                  :show-text="false"
                />
                <span class="color-percentage">{{ (prob * 100).toFixed(1) }}%</span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 特征重要性 -->
        <div class="feature-importance-section">
          <h4>特征重要性</h4>
          <div class="feature-bars">
            <div 
              v-for="(importance, feature) in featureImportance" 
              :key="feature"
              class="feature-bar"
            >
              <div class="feature-label">{{ feature }}</div>
              <div class="feature-progress">
                <el-progress 
                  :percentage="importance * 100" 
                  color="#667eea"
                  :show-text="false"
                />
                <span class="feature-percentage">{{ (importance * 100).toFixed(1) }}%</span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 预测原因 -->
        <div class="prediction-reason-section">
          <h4>预测原因</h4>
          <div class="reason-text">{{ predictionResult.prediction_reason }}</div>
        </div>
        
        <!-- 温度曲线预测 -->
        <div class="temperature-curve-section">
          <h4>预测温度曲线</h4>
          <div ref="temperatureCurveChart" class="curve-chart"></div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { 
  MagicStick, DataAnalysis, Refresh 
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { predictionAPI, batchAPI } from '../utils/api'

// 响应式数据
const predictionForm = ref({
  batchName: '',
  kilnPosition: '',
  saggerThickness: 3.0,
  charcoalAmount: 100,
  clayRatio: {
    '高岭土': 0.5,
    '石英': 0.25,
    '长石': 0.15,
    '其他': 0.1
  }
})

const predictionRules = ref({
  batchName: [
    { required: true, message: '请输入批次名称', trigger: 'blur' }
  ],
  kilnPosition: [
    { required: true, message: '请选择窑位位置', trigger: 'change' }
  ],
  saggerThickness: [
    { required: true, message: '请输入匣钵厚度', trigger: 'blur' }
  ],
  charcoalAmount: [
    { required: true, message: '请输入木炭用量', trigger: 'blur' }
  ]
})

const clayRatioItems = ref([
  { key: '高岭土', label: '高岭土' },
  { key: '石英', label: '石英' },
  { key: '长石', label: '长石' },
  { key: '其他', label: '其他' }
])

const predicting = ref(false)
const predictionResult = ref(null)
const temperatureCurveChart = ref(null)

// 计算属性
const totalRatio = computed(() => {
  return Object.values(predictionForm.value.clayRatio).reduce((sum, ratio) => sum + ratio, 0)
})

const colorProbability = computed(() => {
  if (!predictionResult.value?.color_probability) return {}
  return JSON.parse(predictionResult.value.color_probability)
})

const featureImportance = computed(() => {
  if (!predictionResult.value?.feature_importance) return {}
  return JSON.parse(predictionResult.value.feature_importance)
})

// 方法
const submitPrediction = async () => {
  try {
    // 验证配方总和
    if (Math.abs(totalRatio.value - 1) > 0.01) {
      ElMessage.warning('胎土配方总和必须为1，请调整比例')
      return
    }
    
    predicting.value = true
    
    // 创建批次
    const batchData = {
      batch_name: predictionForm.value.batchName,
      clay_ratio: predictionForm.value.clayRatio,
      sagger_thickness: predictionForm.value.saggerThickness,
      charcoal_amount: predictionForm.value.charcoalAmount,
      kiln_position: predictionForm.value.kilnPosition
    }
    
    const batchResponse = await batchAPI.createBatch(batchData)
    const batchId = batchResponse.data.id
    
    // 执行预测
    const predictionResponse = await predictionAPI.predictBatch(batchId)
    predictionResult.value = predictionResponse.data
    
    // 绘制温度曲线
    await nextTick()
    drawTemperatureCurve()
    
    ElMessage.success('预测完成')
    
  } catch (error) {
    console.error('预测失败:', error)
    ElMessage.error('预测失败，请重试')
  } finally {
    predicting.value = false
  }
}

const resetForm = () => {
  predictionForm.value = {
    batchName: '',
    kilnPosition: '',
    saggerThickness: 3.0,
    charcoalAmount: 100,
    clayRatio: {
      '高岭土': 0.5,
      '石英': 0.25,
      '长石': 0.15,
      '其他': 0.1
    }
  }
  predictionResult.value = null
}

const getScoreType = (score) => {
  if (score >= 90) return 'success'
  if (score >= 80) return 'warning'
  return 'danger'
}

const getColorBarColor = (color) => {
  const colorMap = {
    '青绿色': '#67c23a',
    '天青色': '#409eff',
    '粉青色': '#e6a23c',
    '梅子青': '#f56c6c'
  }
  return colorMap[color] || '#909399'
}

const drawTemperatureCurve = () => {
  if (!temperatureCurveChart.value || !predictionResult.value?.temperature_curve) return
  
  const curveData = JSON.parse(predictionResult.value.temperature_curve)
  const chart = echarts.init(temperatureCurveChart.value)
  
  const option = {
    title: {
      text: '预测温度曲线',
      left: 'center',
      textStyle: {
        color: '#333',
        fontSize: 14
      }
    },
    tooltip: {
      trigger: 'axis',
      formatter: function(params) {
        const data = params[0]
        return `时间: ${data.name}小时<br/>温度: ${data.value}°C<br/>阶段: ${data.data.phase}`
      }
    },
    xAxis: {
      type: 'category',
      data: curveData.map(item => item.hour),
      name: '时间(小时)',
      axisLabel: {
        color: '#666'
      }
    },
    yAxis: {
      type: 'value',
      name: '温度(°C)',
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
      name: '预测温度',
      type: 'line',
      data: curveData.map(item => ({
        value: item.temperature,
        phase: item.phase
      })),
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
  
  chart.setOption(option)
}

// 生命周期
onMounted(() => {
  console.log('预测面板加载完成')
})
</script>

<style scoped>
.prediction-panel {
  padding: 20px;
}

.prediction-form-card,
.prediction-result-card {
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

.clay-ratio-container {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 15px;
  background: #fafafa;
}

.clay-ratio-item {
  text-align: center;
}

.clay-ratio-item label {
  display: block;
  margin-bottom: 5px;
  font-size: 12px;
  color: #666;
}

.ratio-total {
  text-align: center;
  margin-top: 15px;
  font-weight: bold;
  color: #333;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.result-content {
  padding: 20px 0;
}

.score-section {
  text-align: center;
  margin-bottom: 30px;
}

.score-display {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 40px;
}

.score-circle {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: white;
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
}

.score-value {
  font-size: 36px;
  font-weight: bold;
  line-height: 1;
}

.score-label {
  font-size: 14px;
  margin-top: 5px;
}

.score-info {
  text-align: left;
}

.confidence,
.model-version {
  margin-bottom: 10px;
  font-size: 14px;
}

.label {
  color: #666;
  margin-right: 10px;
}

.value {
  font-weight: bold;
  color: #333;
}

.color-probability-section,
.feature-importance-section,
.prediction-reason-section,
.temperature-curve-section {
  margin-bottom: 30px;
}

.color-probability-section h4,
.feature-importance-section h4,
.prediction-reason-section h4,
.temperature-curve-section h4 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 16px;
}

.color-bars,
.feature-bars {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.color-bar,
.feature-bar {
  display: flex;
  align-items: center;
  gap: 15px;
}

.color-label,
.feature-label {
  width: 80px;
  font-size: 14px;
  color: #666;
}

.color-progress,
.feature-progress {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 10px;
}

.color-percentage,
.feature-percentage {
  width: 50px;
  text-align: right;
  font-size: 12px;
  color: #666;
}

.reason-text {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  line-height: 1.6;
  color: #333;
}

.curve-chart {
  height: 300px;
  width: 100%;
}

@media (max-width: 768px) {
  .prediction-panel {
    padding: 10px;
  }
  
  .score-display {
    flex-direction: column;
    gap: 20px;
  }
  
  .color-bar,
  .feature-bar {
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
  }
  
  .color-label,
  .feature-label {
    width: auto;
  }
  
  .curve-chart {
    height: 250px;
  }
}
</style>
