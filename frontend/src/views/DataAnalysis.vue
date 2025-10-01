<template>
  <div class="data-analysis">
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header"><span>预测准确率</span></div>
          </template>
          <div class="stats">
            <div class="stat-item"><label>总预测:</label><span>{{ stats.total_predictions }}</span></div>
            <div class="stat-item"><label>准确率:</label><span>{{ (stats.accuracy*100).toFixed(1) }}%</span></div>
            <div class="stat-item"><label>MAE:</label><span>{{ stats.mae.toFixed(2) }}</span></div>
            <div class="stat-item"><label>RMSE:</label><span>{{ stats.rmse.toFixed(2) }}</span></div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header"><span>特征重要性(平均)</span></div>
          </template>
          <div ref="featureChart" class="chart"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
  
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { predictionAPI } from '../utils/api'
import { ElMessage } from 'element-plus'

const stats = ref({ total_predictions: 0, accuracy: 0, mae: 0, rmse: 0 })
const featureChart = ref(null)

const fetchStats = async () => {
  try {
    const res = await predictionAPI.getAccuracy()
    stats.value = res.data
  } catch { ElMessage.error('加载准确率失败') }
}

const drawFeatureChart = async () => {
  try {
    const res = await predictionAPI.getFeatureImportance()
    const data = res.data.feature_importance || {}
    await nextTick()
    const chart = echarts.init(featureChart.value)
    chart.setOption({
      tooltip: {},
      xAxis: { type: 'category', data: Object.keys(data) },
      yAxis: { type: 'value' },
      series: [{ type: 'bar', data: Object.values(data), itemStyle: { color: '#667eea' } }]
    })
  } catch { ElMessage.error('加载特征重要性失败') }
}

onMounted(async () => {
  await fetchStats()
  await drawFeatureChart()
})
</script>

<style scoped>
.data-analysis { padding: 20px; }
.chart { height: 320px; width: 100%; }
.stats { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
.stat-item { background: #fafafa; border: 1px solid #eee; border-radius: 6px; padding: 10px; }
.stat-item label { color: #666; margin-right: 6px; }
</style>
