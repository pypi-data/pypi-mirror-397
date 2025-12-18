<template>
  <el-drawer v-model="drawerVisible" :title="drawerTitle" :size="'50%'" :before-close="handleClose">
    <div class="bind-scene-drawer">
      <!-- 步骤条 -->
      <el-steps :active="currentStep" finish-status="success" align-center>
        <el-step title="选择场景" description="选择要绑定的场景" />
        <el-step title="配置模型通道" description="为每个场景的模型选择摄像头通道" />
        <el-step title="确认绑定" description="确认绑定信息" />
      </el-steps>

      <!-- 步骤1：选择场景 -->
      <div v-if="currentStep === 0" class="step-content">
        <div class="step-header">
          <h3>选择场景</h3>
          <p>请选择要绑定到门店的场景</p>
        </div>

        <div class="scene-list">
          <el-table
            :data="sceneList"
            v-loading="sceneLoading"
            style="width: 100%"
            height="400"
            ref="sceneTableRef"
            @selection-change="handleSceneSelectionChange"
            @row-click="handleRowClick"
            :row-class-name="getRowClassName"
          >
            <el-table-column type="selection" width="55" />
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="name" label="场景名称" width="200" />
            <el-table-column prop="description" label="场景描述" min-width="200" show-overflow-tooltip />
            <el-table-column prop="hz" label="执行频率" width="120">
              <template #default="scope"> {{ scope.row.hz }}秒 </template>
            </el-table-column>
            <el-table-column prop="created" label="创建时间" width="180" />
          </el-table>
        </div>
      </div>

      <!-- 步骤2：配置模型通道 -->
      <div v-if="currentStep === 1" class="step-content">
        <div class="step-header">
          <h3>配置模型通道</h3>
          <p>为每个场景的模型选择摄像头通道</p>
        </div>

        <div v-if="channelLoading" class="loading-container">
          <el-skeleton :rows="3" animated />
        </div>

        <div v-else class="model-config-list">
          <div v-for="scene in selectedScenes" :key="scene.id" class="scene-model-config">
            <div class="scene-header">
              <h4>{{ scene.name }}</h4>
              <el-tag type="primary" size="small">{{ scene.hz }}秒</el-tag>
            </div>

            <div v-if="sceneModels[scene.id] && sceneModels[scene.id].length > 0" class="models-container">
              <div v-for="model in sceneModels[scene.id]" :key="model.id" class="model-item">
                <div class="model-info">
                  <span class="model-name">{{ model.name }}</span>
                  <span class="model-desc">{{ model.desc || "无描述" }}</span>
                </div>

                <div class="camera-selection">
                  <el-select
                    v-model="modelCameraMappings[model.id]"
                    multiple
                    placeholder="选择摄像头通道"
                    style="width: 100%"
                    @change="handleModelCameraChange(model.id, $event)"
                    :loading="channelLoading"
                    :disabled="channelLoading"
                  >
                    <el-option
                      v-for="channel in cameraChannelList"
                      :key="channel.id"
                      :label="`${channel.brand_name} - ${channel.channel_id}`"
                      :value="channel.id"
                    />
                  </el-select>
                  <div v-if="!channelLoading && cameraChannelList.length === 0" class="no-channels-tip">
                    <el-text type="info" size="small">该门店暂无摄像头通道</el-text>
                  </div>
                </div>
              </div>
            </div>

            <div v-else class="no-models">
              <el-empty description="该场景暂无关联模型" :image-size="80" />
            </div>
          </div>
        </div>
      </div>

      <!-- 步骤3：确认绑定 -->
      <div v-if="currentStep === 2" class="step-content">
        <div class="step-header">
          <h3>确认绑定信息</h3>
          <p>请确认以下绑定信息</p>
        </div>

        <div class="confirm-info">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="门店名称">{{ drawerProps.storeName }}</el-descriptions-item>
            <el-descriptions-item label="门店ID">{{ drawerProps.storeId }}</el-descriptions-item>
            <el-descriptions-item label="绑定场景" :span="1">
              <div v-for="scene in selectedScenes" :key="scene.id" class="scene-summary">
                <div class="scene-info">
                  <span class="scene-name">{{ scene.name }}</span>
                  <span class="scene-freq">{{ scene.hz }}秒</span>
                </div>
                <div v-if="sceneModels[scene.id] && sceneModels[scene.id].length > 0" class="models-summary">
                  <div v-for="model in sceneModels[scene.id]" :key="model.id" class="model-summary">
                    <span class="model-name">{{ model.name }}</span>
                    <div class="channels-summary">
                      <el-tag
                        v-for="channelId in modelCameraMappings[model.id] || []"
                        :key="channelId"
                        type="success"
                        size="small"
                        style="margin-right: 4px"
                      >
                        {{ getChannelName(channelId) }}
                      </el-tag>
                    </div>
                  </div>
                </div>
                <div v-else class="no-models-summary">
                  <el-tag type="info" size="small">无关联模型</el-tag>
                </div>
              </div>
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="drawer-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button v-if="currentStep > 0" @click="prevStep">上一步</el-button>
        <el-button v-if="currentStep < 2" type="primary" @click="nextStep" :disabled="!canNextStep"> 下一步 </el-button>
        <el-button v-if="currentStep === 2" type="success" @click="handleBind" :loading="binding"> 确认绑定 </el-button>
      </div>
    </div>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import {
  getStoreUnboundScenes,
  getStoreCameraChannels,
  bindStoreScene,
  type SceneInfo,
  type ModelInfo,
  type CameraChannelInfo,
  type StoreSceneBindParams,
  type ModelCameraMapping
} from "@/api/modules/store";

interface DrawerProps {
  title: string;
  storeId: number;
  storeName: string;
  getTableList?: () => void;
}

const drawerVisible = ref(false);
const currentStep = ref(0);
const binding = ref(false);

// 表格引用
const sceneTableRef = ref();

const drawerProps = ref<DrawerProps>({
  title: "",
  storeId: 0,
  storeName: ""
});

// 场景相关
const sceneList = ref<SceneInfo[]>([]);
const sceneLoading = ref(false);
const selectedScenes = ref<SceneInfo[]>([]);

// 模型相关
const sceneModels = ref<Record<number, ModelInfo[]>>({});

// 摄像头通道相关
const cameraChannelList = ref<CameraChannelInfo[]>([]);
const channelLoading = ref(false);
const channelsLoaded = ref(false); // 添加标记，避免重复加载

// 模型摄像头通道映射
const modelCameraMappings = ref<Record<number, number[]>>({});

// 计算属性
const drawerTitle = computed(() => {
  return drawerProps.value.title || "绑定场景";
});

const canNextStep = computed(() => {
  if (currentStep.value === 0) {
    return selectedScenes.value.length > 0;
  } else if (currentStep.value === 1) {
    // 检查是否所有选中的场景都有模型配置
    for (const scene of selectedScenes.value) {
      if (!sceneModels.value[scene.id] || sceneModels.value[scene.id].length === 0) {
        continue; // 跳过没有模型的场景
      }
      // 检查该场景的模型是否都配置了摄像头通道
      for (const model of sceneModels.value[scene.id]) {
        if (!modelCameraMappings.value[model.id] || modelCameraMappings.value[model.id].length === 0) {
          return false;
        }
      }
    }
    return true;
  }
  return true;
});

// 打开抽屉
const openDrawer = (props: DrawerProps) => {
  drawerProps.value = props;
  drawerVisible.value = true;
  currentStep.value = 0;

  // 重置数据
  selectedScenes.value = [];
  sceneModels.value = {};
  modelCameraMappings.value = {};
  channelsLoaded.value = false; // 重置通道加载状态

  // 加载场景列表
  loadSceneList();
};

// 关闭抽屉
const handleClose = () => {
  drawerVisible.value = false;
  currentStep.value = 0;
  selectedScenes.value = [];
  sceneModels.value = {};
  modelCameraMappings.value = {};
  channelsLoaded.value = false; // 重置通道加载状态
};

// 加载场景列表
const loadSceneList = async () => {
  sceneLoading.value = true;
  try {
    // 直接获取未绑定的场景列表
    const response = await getStoreUnboundScenes(drawerProps.value.storeId);
    sceneList.value = response.data || [];
  } catch {
    ElMessage.error("加载场景列表失败");
    sceneList.value = [];
  } finally {
    sceneLoading.value = false;
  }
};

// 加载摄像头通道列表
const loadCameraChannels = async () => {
  if (!drawerProps.value.storeId || channelsLoaded.value) return;

  channelLoading.value = true;
  try {
    const response = await getStoreCameraChannels(drawerProps.value.storeId);
    // 根据实际接口返回格式调整数据获取方式
    if (response.data && Array.isArray(response.data)) {
      cameraChannelList.value = response.data;
    } else {
      cameraChannelList.value = [];
    }
    channelsLoaded.value = true; // 标记已加载
  } catch {
    ElMessage.error("加载摄像头通道列表失败");
    cameraChannelList.value = [];
  } finally {
    channelLoading.value = false;
  }
};

// 处理场景选择变化
const handleSceneSelectionChange = (selection: SceneInfo[]) => {
  selectedScenes.value = selection;
};

// 处理行点击事件
const handleRowClick = (row: SceneInfo) => {
  if (sceneTableRef.value) {
    sceneTableRef.value.toggleRowSelection(row);
  }
};

// 获取行样式类名
const getRowClassName = () => {
  return "clickable-row";
};

// 处理模型摄像头通道变化
const handleModelCameraChange = (modelId: number, channelIds: number[]) => {
  modelCameraMappings.value[modelId] = channelIds;
};

// 获取通道名称
const getChannelName = (channelId: number) => {
  const channel = cameraChannelList.value.find(ch => ch.id === channelId);
  return channel ? `${channel.brand_name} - ${channel.channel_id}` : `通道${channelId}`;
};

// 下一步
const nextStep = async () => {
  if (currentStep.value === 0) {
    if (selectedScenes.value.length === 0) {
      ElMessage.warning("请选择至少一个场景");
      return;
    }

    try {
      currentStep.value = 1;

      // 只在第一次进入步骤1时加载摄像头通道列表
      if (!channelsLoaded.value) {
        await loadCameraChannels();
      }

      // 使用接口返回的模型信息，不需要单独查询
      for (const scene of selectedScenes.value) {
        if (scene.models && scene.models.length > 0) {
          sceneModels.value[scene.id] = scene.models;
        } else {
          sceneModels.value[scene.id] = [];
        }
      }
    } catch {
      ElMessage.error("加载配置信息失败，请重试");
      currentStep.value = 0; // 回退到上一步
    }
  } else if (currentStep.value === 1) {
    // 检查是否所有模型都配置了摄像头通道
    let hasUnconfiguredModel = false;
    let unconfiguredModelName = "";

    for (const scene of selectedScenes.value) {
      if (sceneModels.value[scene.id] && sceneModels.value[scene.id].length > 0) {
        for (const model of sceneModels.value[scene.id]) {
          if (!modelCameraMappings.value[model.id] || modelCameraMappings.value[model.id].length === 0) {
            hasUnconfiguredModel = true;
            unconfiguredModelName = model.name;
            break;
          }
        }
      }
      if (hasUnconfiguredModel) break;
    }

    if (hasUnconfiguredModel) {
      ElMessage.warning(`请为模型"${unconfiguredModelName}"配置摄像头通道`);
      return;
    }

    currentStep.value = 2;
  }
};

// 上一步
const prevStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--;
  }
};

// 绑定场景
const handleBind = async () => {
  if (selectedScenes.value.length === 0) {
    ElMessage.warning("请选择场景");
    return;
  }

  try {
    await ElMessageBox.confirm(
      `确定要将 ${selectedScenes.value.length} 个场景绑定到门店"${drawerProps.value.storeName}"吗？`,
      "确认绑定",
      { type: "warning" }
    );

    binding.value = true;

    // 批量绑定场景
    const bindPromises = selectedScenes.value.map(scene => {
      // 构建该场景的模型摄像头映射
      const mappings: ModelCameraMapping[] = [];
      if (sceneModels.value[scene.id]) {
        for (const model of sceneModels.value[scene.id]) {
          if (modelCameraMappings.value[model.id] && modelCameraMappings.value[model.id].length > 0) {
            mappings.push({
              model_id: model.id,
              camera_channel_ids: modelCameraMappings.value[model.id]
            });
          }
        }
      }

      const params: StoreSceneBindParams = {
        store_id: drawerProps.value.storeId,
        scene_id: scene.id,
        model_camera_mappings: mappings
      };
      return bindStoreScene(params);
    });

    await Promise.all(bindPromises);

    ElMessage.success(`成功绑定 ${selectedScenes.value.length} 个场景`);
    handleClose();

    // 刷新门店列表
    if (drawerProps.value.getTableList) {
      drawerProps.value.getTableList();
    }
  } catch (error: any) {
    if (error !== "cancel") {
      ElMessage.error("绑定失败");
    }
  } finally {
    binding.value = false;
  }
};

// 暴露方法给父组件
defineExpose({
  openDrawer
});
</script>

<style scoped lang="scss">
.bind-scene-drawer {
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.step-content {
  flex: 1;
  margin: 20px 0;
}

.step-header {
  margin-bottom: 20px;

  h3 {
    margin: 0 0 8px 0;
    color: #303133;
  }

  p {
    margin: 0;
    color: #909399;
    font-size: 14px;
  }
}

.scene-list {
  margin-top: 20px;
}

.loading-container {
  margin-top: 20px;
  padding: 20px;
}

.model-config-list {
  margin-top: 20px;
  max-height: 500px;
  overflow-y: auto;
}

.scene-model-config {
  margin-bottom: 24px;
  padding: 16px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  background: #fafafa;
}

.scene-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;

  h4 {
    margin: 0;
    color: #303133;
  }
}

.models-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.model-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px;
  background: white;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
}

.model-info {
  flex: 1;
  min-width: 200px;

  .model-name {
    display: block;
    font-weight: 500;
    color: #303133;
    margin-bottom: 4px;
  }

  .model-desc {
    display: block;
    font-size: 12px;
    color: #909399;
  }
}

.camera-selection {
  flex: 1;
  min-width: 300px;
}

.no-channels-tip {
  margin-top: 8px;
  text-align: center;
}

.no-models {
  text-align: center;
  padding: 20px;
}

.confirm-info {
  margin-top: 20px;
}

.scene-summary {
  margin-bottom: 16px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 6px;
}

.scene-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;

  .scene-name {
    font-weight: 500;
    color: #303133;
  }

  .scene-freq {
    color: #909399;
    font-size: 12px;
  }
}

.models-summary {
  margin-left: 16px;
}

.model-summary {
  margin-bottom: 8px;

  .model-name {
    display: block;
    font-size: 14px;
    color: #606266;
    margin-bottom: 4px;
  }

  .channels-summary {
    margin-left: 16px;
  }
}

.no-models-summary {
  margin-left: 16px;
}

.drawer-footer {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

:deep(.el-drawer__body) {
  padding: 0;
}

:deep(.el-steps) {
  margin-bottom: 20px;
}

:deep(.clickable-row) {
  cursor: pointer;
}

:deep(.clickable-row:hover) {
  background-color: #f5f7fa;
}
</style>
