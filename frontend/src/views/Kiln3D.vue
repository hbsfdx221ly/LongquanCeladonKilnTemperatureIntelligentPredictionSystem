<template>
  <div class="kiln-3d">
    <!-- 3D窑炉模型容器 -->
    <div class="kiln-container">
      <div ref="threeContainer" class="three-container"></div>
      
      <!-- 控制面板 -->
      <div class="control-panel">
        <el-card class="control-card">
          <template #header>
            <div class="card-header">
              <el-icon><Setting /></el-icon>
              <span>窑炉控制</span>
            </div>
          </template>
          
          <!-- 温度控制 -->
          <div class="control-section">
            <h4>温度控制</h4>
            <el-slider
              v-model="temperature"
              :min="20"
              :max="1300"
              :step="10"
              show-input
              @change="updateTemperature"
            />
            <div class="temperature-display">
              当前温度: {{ temperature }}°C
            </div>
          </div>
          
          <!-- 火焰强度 -->
          <div class="control-section">
            <h4>火焰强度</h4>
            <el-slider
              v-model="flameIntensity"
              :min="0"
              :max="100"
              :step="5"
              @change="updateFlameIntensity"
            />
          </div>
          
          <!-- 窑位选择 -->
          <div class="control-section">
            <h4>窑位选择</h4>
            <el-radio-group v-model="selectedPosition" @change="updatePosition">
              <el-radio label="A">窑位 A</el-radio>
              <el-radio label="B">窑位 B</el-radio>
              <el-radio label="C">窑位 C</el-radio>
              <el-radio label="D">窑位 D</el-radio>
              <el-radio label="E">窑位 E</el-radio>
            </el-radio-group>
          </div>
          
          <!-- 动画控制 -->
          <div class="control-section">
            <h4>动画控制</h4>
            <el-button-group>
              <el-button 
                :type="isAnimating ? 'primary' : 'default'"
                @click="toggleAnimation"
              >
                <el-icon><VideoPlay v-if="!isAnimating" /><VideoPause v-else /></el-icon>
                {{ isAnimating ? '暂停' : '播放' }}
              </el-button>
              <el-button @click="resetAnimation">
                <el-icon><Refresh /></el-icon>
                重置
              </el-button>
            </el-button-group>
          </div>
        </el-card>
      </div>
      
      <!-- 温度信息面板 -->
      <div class="temperature-panel">
        <el-card class="temp-card">
          <template #header>
            <div class="card-header">
              <el-icon><Thermometer /></el-icon>
              <span>温度分布</span>
            </div>
          </template>
          
          <div class="temp-grid">
            <div 
              v-for="(temp, index) in temperatureGrid" 
              :key="index"
              class="temp-cell"
              :style="{ backgroundColor: getTemperatureColor(temp) }"
            >
              <div class="temp-value">{{ temp }}°C</div>
              <div class="temp-position">{{ getPositionLabel(index) }}</div>
            </div>
          </div>
        </el-card>
      </div>
      
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-overlay">
        <el-icon class="loading-icon"><Loading /></el-icon>
        <div class="loading-text">正在加载3D模型...</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import * as THREE from 'three'
import { 
  Setting, VideoPlay, VideoPause, Refresh, Loading 
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// 响应式数据
const threeContainer = ref(null)
const loading = ref(true)
const temperature = ref(1200)
const flameIntensity = ref(80)
const selectedPosition = ref('A')
const isAnimating = ref(true)

// 3D相关变量
let scene, camera, renderer, kiln, flame, animationId
let temperatureGrid = ref([])

// 生命周期
onMounted(async () => {
  await nextTick()
  initThreeJS()
  generateTemperatureGrid()
})

onUnmounted(() => {
  if (animationId) {
    cancelAnimationFrame(animationId)
  }
  if (renderer) {
    renderer.dispose()
  }
})

// 初始化Three.js
const initThreeJS = () => {
  try {
    // 创建场景
    scene = new THREE.Scene()
    scene.background = new THREE.Color(0x87CEEB) // 天蓝色背景
    
    // 创建相机
    camera = new THREE.PerspectiveCamera(
      75, 
      threeContainer.value.clientWidth / threeContainer.value.clientHeight, 
      0.1, 
      1000
    )
    camera.position.set(10, 8, 10)
    camera.lookAt(0, 0, 0)
    
    // 创建渲染器
    renderer = new THREE.WebGLRenderer({ antialias: true })
    renderer.setSize(threeContainer.value.clientWidth, threeContainer.value.clientHeight)
    renderer.shadowMap.enabled = true
    renderer.shadowMap.type = THREE.PCFSoftShadowMap
    threeContainer.value.appendChild(renderer.domElement)
    
    // 创建窑炉模型
    createKilnModel()
    
    // 创建火焰效果
    createFlameEffect()
    
    // 添加光照
    addLighting()
    
    // 添加控制器
    addControls()
    
    // 开始渲染循环
    animate()
    
    loading.value = false
    ElMessage.success('3D窑炉模型加载完成')
    
  } catch (error) {
    console.error('3D模型初始化失败:', error)
    ElMessage.error('3D模型加载失败')
    loading.value = false
  }
}

// 创建窑炉模型
const createKilnModel = () => {
  // 窑炉主体
  const kilnGeometry = new THREE.CylinderGeometry(3, 4, 8, 16)
  const kilnMaterial = new THREE.MeshLambertMaterial({ 
    color: 0x8B4513,
    transparent: true,
    opacity: 0.8
  })
  kiln = new THREE.Mesh(kilnGeometry, kilnMaterial)
  kiln.position.y = 4
  kiln.castShadow = true
  kiln.receiveShadow = true
  scene.add(kiln)
  
  // 窑炉内部
  const innerGeometry = new THREE.CylinderGeometry(2.5, 3.5, 7.5, 16)
  const innerMaterial = new THREE.MeshLambertMaterial({ 
    color: 0x2F2F2F,
    transparent: true,
    opacity: 0.6
  })
  const innerKiln = new THREE.Mesh(innerGeometry, innerMaterial)
  innerKiln.position.y = 4
  scene.add(innerKiln)
  
  // 窑炉顶部
  const topGeometry = new THREE.CylinderGeometry(3.2, 3.2, 0.5, 16)
  const topMaterial = new THREE.MeshLambertMaterial({ color: 0x654321 })
  const top = new THREE.Mesh(topGeometry, topMaterial)
  top.position.y = 8.25
  top.castShadow = true
  scene.add(top)
  
  // 添加窑位标记
  createKilnPositions()
}

// 创建窑位标记
const createKilnPositions = () => {
  const positions = [
    { label: 'A', x: 0, y: 2, z: 2.5 },
    { label: 'B', x: 2, y: 2, z: 0 },
    { label: 'C', x: 0, y: 4, z: 2.5 },
    { label: 'D', x: -2, y: 4, z: 0 },
    { label: 'E', x: 0, y: 6, z: 2.5 }
  ]
  
  positions.forEach(pos => {
    const geometry = new THREE.SphereGeometry(0.2, 8, 8)
    const material = new THREE.MeshLambertMaterial({ 
      color: pos.label === selectedPosition.value ? 0xff0000 : 0x00ff00 
    })
    const marker = new THREE.Mesh(geometry, material)
    marker.position.set(pos.x, pos.y, pos.z)
    marker.userData = { label: pos.label }
    scene.add(marker)
  })
}

// 创建火焰效果
const createFlameEffect = () => {
  const flameGeometry = new THREE.ConeGeometry(0.5, 2, 8)
  const flameMaterial = new THREE.MeshLambertMaterial({ 
    color: 0xff4500,
    transparent: true,
    opacity: 0.7
  })
  flame = new THREE.Mesh(flameGeometry, flameMaterial)
  flame.position.set(0, 1, 0)
  scene.add(flame)
}

// 添加光照
const addLighting = () => {
  // 环境光
  const ambientLight = new THREE.AmbientLight(0x404040, 0.6)
  scene.add(ambientLight)
  
  // 主光源
  const directionalLight = new THREE.DirectionalLight(0xffffff, 1)
  directionalLight.position.set(10, 10, 5)
  directionalLight.castShadow = true
  directionalLight.shadow.mapSize.width = 2048
  directionalLight.shadow.mapSize.height = 2048
  scene.add(directionalLight)
  
  // 火焰光源
  const flameLight = new THREE.PointLight(0xff4500, 2, 10)
  flameLight.position.set(0, 1, 0)
  scene.add(flameLight)
}

// 添加控制器
const addControls = () => {
  // 简单的鼠标控制
  let mouseX = 0, mouseY = 0
  let isMouseDown = false
  
  const onMouseMove = (event) => {
    if (!isMouseDown) return
    
    mouseX = (event.clientX / window.innerWidth) * 2 - 1
    mouseY = -(event.clientY / window.innerHeight) * 2 + 1
    
    camera.position.x = Math.sin(mouseX * Math.PI) * 15
    camera.position.z = Math.cos(mouseX * Math.PI) * 15
    camera.position.y = 8 + mouseY * 5
    camera.lookAt(0, 4, 0)
  }
  
  const onMouseDown = () => {
    isMouseDown = true
  }
  
  const onMouseUp = () => {
    isMouseDown = false
  }
  
  renderer.domElement.addEventListener('mousemove', onMouseMove)
  renderer.domElement.addEventListener('mousedown', onMouseDown)
  renderer.domElement.addEventListener('mouseup', onMouseUp)
}

// 动画循环
const animate = () => {
  animationId = requestAnimationFrame(animate)
  
  if (isAnimating.value) {
    // 火焰动画
    if (flame) {
      flame.rotation.y += 0.02
      flame.scale.y = 1 + Math.sin(Date.now() * 0.005) * 0.2
    }
    
    // 窑炉旋转
    if (kiln) {
      kiln.rotation.y += 0.005
    }
  }
  
  renderer.render(scene, camera)
}

// 生成温度网格
const generateTemperatureGrid = () => {
  const grid = []
  for (let i = 0; i < 25; i++) {
    // 模拟温度分布：中心高，边缘低
    const x = (i % 5) - 2
    const z = Math.floor(i / 5) - 2
    const distance = Math.sqrt(x * x + z * z)
    const temp = temperature.value - distance * 50 + Math.random() * 20 - 10
    grid.push(Math.max(20, Math.min(1300, Math.round(temp))))
  }
  temperatureGrid.value = grid
}

// 获取温度颜色
const getTemperatureColor = (temp) => {
  if (temp < 200) return '#4A90E2' // 蓝色
  if (temp < 400) return '#7ED321' // 绿色
  if (temp < 600) return '#F5A623' // 橙色
  if (temp < 800) return '#FF6B6B' // 红色
  if (temp < 1000) return '#FF2D92' // 粉红
  return '#8B00FF' // 紫色
}

// 获取位置标签
const getPositionLabel = (index) => {
  const labels = ['A1', 'A2', 'A3', 'A4', 'A5',
                  'B1', 'B2', 'B3', 'B4', 'B5',
                  'C1', 'C2', 'C3', 'C4', 'C5',
                  'D1', 'D2', 'D3', 'D4', 'D5',
                  'E1', 'E2', 'E3', 'E4', 'E5']
  return labels[index] || 'N/A'
}

// 事件处理
const updateTemperature = () => {
  generateTemperatureGrid()
  ElMessage.info(`温度已更新至 ${temperature.value}°C`)
}

const updateFlameIntensity = () => {
  if (flame) {
    flame.scale.setScalar(flameIntensity.value / 100)
  }
  ElMessage.info(`火焰强度已更新至 ${flameIntensity.value}%`)
}

const updatePosition = () => {
  // 更新窑位标记颜色
  scene.children.forEach(child => {
    if (child.userData && child.userData.label) {
      child.material.color.setHex(
        child.userData.label === selectedPosition.value ? 0xff0000 : 0x00ff00
      )
    }
  })
  ElMessage.info(`已选择窑位 ${selectedPosition.value}`)
}

const toggleAnimation = () => {
  isAnimating.value = !isAnimating.value
  ElMessage.info(isAnimating.value ? '动画已开始' : '动画已暂停')
}

const resetAnimation = () => {
  temperature.value = 1200
  flameIntensity.value = 80
  selectedPosition.value = 'A'
  isAnimating.value = true
  generateTemperatureGrid()
  updatePosition()
  ElMessage.info('动画已重置')
}
</script>

<style scoped>
.kiln-3d {
  height: 100vh;
  position: relative;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.kiln-container {
  position: relative;
  width: 100%;
  height: 100%;
}

.three-container {
  width: 100%;
  height: 100%;
  position: absolute;
  top: 0;
  left: 0;
}

.control-panel {
  position: absolute;
  top: 20px;
  left: 20px;
  width: 300px;
  z-index: 100;
}

.control-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border: none;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: bold;
  color: #333;
}

.control-section {
  margin-bottom: 20px;
}

.control-section h4 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 14px;
}

.temperature-display {
  text-align: center;
  margin-top: 10px;
  font-weight: bold;
  color: #667eea;
}

.temperature-panel {
  position: absolute;
  bottom: 20px;
  right: 20px;
  width: 300px;
  z-index: 100;
}

.temp-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border: none;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.temp-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 2px;
}

.temp-cell {
  aspect-ratio: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  border-radius: 4px;
  color: white;
  font-size: 10px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
}

.temp-value {
  font-weight: bold;
  font-size: 11px;
}

.temp-position {
  font-size: 8px;
  opacity: 0.8;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: white;
  z-index: 1000;
}

.loading-icon {
  font-size: 48px;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

.loading-text {
  font-size: 18px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .control-panel,
  .temperature-panel {
    position: relative;
    width: 100%;
    margin: 10px;
  }
  
  .kiln-container {
    height: calc(100vh - 200px);
  }
}
</style>
