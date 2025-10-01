<template>
  <div class="batch-management">
    <el-card class="mb-20">
      <template #header>
        <div class="card-header">
          <span>批次列表</span>
          <div class="actions">
            <el-button type="primary" @click="fetchData" :loading="loading">刷新</el-button>
            <el-button @click="openCreate">新建批次</el-button>
          </div>
        </div>
      </template>
      <el-table :data="batches" style="width: 100%" :loading="loading">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="batch_name" label="名称" />
        <el-table-column prop="status" label="状态" width="100" />
        <el-table-column prop="predicted_score" label="预测分" width="100" />
        <el-table-column prop="confidence" label="置信度" width="100">
          <template #default="scope">{{ scope.row.confidence ? (scope.row.confidence*100).toFixed(1)+'%' : '-' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="220">
          <template #default="scope">
            <el-button type="text" @click="startFiring(scope.row)">开始烧制</el-button>
            <el-button type="text" @click="predict(scope.row)">预测</el-button>
            <el-button type="text" @click="remove(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination">
        <el-pagination
          background
          layout="prev, pager, next"
          :page-size="query.per_page"
          :total="total"
          @current-change="pageChange"
        />
      </div>
    </el-card>

    <!-- 创建批次对话框 -->
    <el-dialog v-model="createVisible" title="新建批次" width="520px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="批次名称">
          <el-input v-model="form.batch_name" />
        </el-form-item>
        <el-form-item label="窑位">
          <el-select v-model="form.kiln_position">
            <el-option label="窑位 A" value="窑位_A" />
            <el-option label="窑位 B" value="窑位_B" />
            <el-option label="窑位 C" value="窑位_C" />
            <el-option label="窑位 D" value="窑位_D" />
            <el-option label="窑位 E" value="窑位_E" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createVisible=false">取消</el-button>
        <el-button type="primary" @click="create">创建</el-button>
      </template>
    </el-dialog>
  </div>
  
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { batchAPI, predictionAPI } from '../utils/api'

const loading = ref(false)
const batches = ref([])
const total = ref(0)
const query = ref({ page: 1, per_page: 10 })

const createVisible = ref(false)
const form = ref({ batch_name: '', kiln_position: '窑位_A' })

const fetchData = async () => {
  loading.value = true
  try {
    const res = await batchAPI.getBatches({ page: query.value.page, per_page: query.value.per_page })
    batches.value = res.data
    total.value = res.pagination.total
  } catch (e) {
    ElMessage.error('加载批次失败')
  } finally {
    loading.value = false
  }
}

const pageChange = (p) => { query.value.page = p; fetchData() }

const openCreate = () => { createVisible.value = true }
const create = async () => {
  if (!form.value.batch_name) return ElMessage.warning('请输入批次名称')
  try {
    await batchAPI.createBatch({ batch_name: form.value.batch_name, kiln_position: form.value.kiln_position })
    ElMessage.success('创建成功')
    createVisible.value = false
    fetchData()
  } catch { ElMessage.error('创建失败') }
}

const remove = async (row) => {
  await ElMessageBox.confirm('确认删除该批次吗？', '提示')
  await batchAPI.deleteBatch(row.id)
  ElMessage.success('已删除')
  fetchData()
}

const startFiring = async (row) => {
  await batchAPI.startBatch(row.id)
  ElMessage.success('已开始烧制')
  fetchData()
}

const predict = async (row) => {
  try {
    const res = await predictionAPI.predictBatch(row.id)
    if (res?.data) ElMessage.success('预测完成，分数 ' + res.data.predicted_score)
  } catch { ElMessage.error('预测失败') }
}

onMounted(fetchData)
</script>

<style scoped>
.batch-management { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.pagination { margin-top: 12px; display: flex; justify-content: center; }
</style>
