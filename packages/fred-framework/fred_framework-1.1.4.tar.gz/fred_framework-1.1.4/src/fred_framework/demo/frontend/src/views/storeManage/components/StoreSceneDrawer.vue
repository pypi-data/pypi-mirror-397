<template>
  <el-drawer v-model="drawerVisible" :title="drawerTitle" :size="'90%'" :before-close="handleClose">
    <div class="store-scene-drawer">
      <!-- 搜索区域 -->
      <div class="search-area">
        <el-input v-model="searchForm.name" placeholder="请输入场景名称" style="width: 300px" clearable @input="handleSearch">
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>

        <!-- 统计信息 -->
        <div class="statistics-info">
          <el-tag type="success" size="small"> 已绑定场景: {{ sceneDetails.length }} </el-tag>
          <el-tag type="info" size="small"> 总模型数: {{ totalModels }} </el-tag>
          <el-tag type="primary" size="small"> 总通道数: {{ totalChannels }} </el-tag>
        </div>
      </div>

      <!-- 场景详情列表 -->
      <div class="scene-details-list">
        <div v-for="scene in filteredSceneDetails" :key="scene.id" class="scene-detail-card">
          <!-- 场景基本信息 -->
          <div class="scene-header" @click="toggleSceneExpanded(scene.id)">
            <div class="scene-info">
              <div class="scene-title-row">
                <h3 class="scene-name">{{ scene.name }}</h3>
                <el-icon class="expand-icon" :class="{ expanded: expandedScenes.includes(scene.id) }">
                  <ArrowDown />
                </el-icon>
              </div>
              <div class="scene-meta">
                <el-tag :type="scene.status === 1 ? 'success' : 'danger'" size="small">
                  {{ scene.status === 1 ? "启用" : "禁用" }}
                </el-tag>
                <el-tag type="primary" size="small">{{ scene.hz }}秒</el-tag>
                <span class="scene-desc">{{ scene.description || "无描述" }}</span>
              </div>
            </div>
            <div class="scene-actions" @click.stop>
              <el-button type="primary" size="small" @click="toggleSceneExpanded(scene.id)">
                {{ expandedScenes.includes(scene.id) ? "收起" : "展开" }}
              </el-button>
              <el-button type="danger" size="small" @click="unbindScene(scene)"> 解绑场景 </el-button>
            </div>
          </div>

          <!-- 场景模型详情（可展开） -->
          <div v-if="expandedScenes.includes(scene.id)" class="scene-models">
            <div v-if="scene.models && scene.models.length > 0" class="models-container">
              <div v-for="model in scene.models" :key="model.id" class="model-detail-card">
                <!-- 模型信息 -->
                <div class="model-header" @click="toggleModelExpanded(model.id)">
                  <div class="model-info">
                    <div class="model-title-row">
                      <h4 class="model-name">{{ model.name }}</h4>
                      <el-icon class="expand-icon" :class="{ expanded: expandedModels.includes(model.id) }">
                        <ArrowDown />
                      </el-icon>
                    </div>
                    <p class="model-desc">{{ model.desc || "无描述" }}</p>
                  </div>
                  <div class="model-meta" @click.stop>
                    <el-tag type="info" size="small">模型ID: {{ model.id }}</el-tag>
                    <el-button type="text" size="small" @click="toggleModelExpanded(model.id)">
                      {{ expandedModels.includes(model.id) ? "收起通道" : "查看通道" }}
                    </el-button>
                    <el-button type="primary" size="small" @click="handleAddChannel(model)">
                      <el-icon><Plus /></el-icon>
                      新增通道
                    </el-button>
                  </div>
                </div>

                <!-- 模型摄像头通道详情（可展开） -->
                <div v-if="expandedModels.includes(model.id)" class="model-channels">
                  <div v-if="model.camera_channels && model.camera_channels.length > 0" class="channels-container">
                    <ProTable
                      :data="model.camera_channels"
                      :columns="channelColumns"
                      :pagination="false"
                      :show-header="true"
                      size="small"
                      class="channel-table"
                    />
                  </div>
                  <div v-else class="no-channels">
                    <div style="text-align: center; padding: 20px">
                      <p style="color: #999; margin-bottom: 16px">该模型暂无关联的摄像头通道</p>
                      <p style="color: #909399; font-size: 12px">请点击上方的"新增通道"按钮添加通道</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="no-models">
              <el-empty description="该场景暂无关联模型" :image-size="80" />
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-if="filteredSceneDetails.length === 0" class="empty-state">
          <el-empty description="该门店暂无绑定的场景" :image-size="120" />
        </div>
      </div>
    </div>

    <!-- 通道替换对话框 -->
    <el-dialog v-model="channelReplaceDialogVisible" title="替换通道" width="500px" :before-close="handleCancelChannelReplace">
      <div class="channel-replace-content">
        <p class="replace-tip">请从下拉菜单中选择要替换的通道：</p>

        <el-select
          v-model="selectedChannelId"
          placeholder="请选择要替换的通道"
          style="width: 100%"
          :loading="channelReplaceLoading"
          filterable
          clearable
        >
          <template #empty>
            <div class="select-empty">
              <el-empty description="暂无可用的通道" :image-size="60" />
            </div>
          </template>

          <el-option
            v-for="channel in availableChannels"
            :key="channel.id"
            :label="`${channel.brand_name} - ${channel.channel_id} (${channel.ip})`"
            :value="channel.id"
          >
            <div class="channel-option">
              <div class="channel-main-info">
                <span class="channel-name">{{ channel.brand_name }} - {{ channel.channel_id }}</span>
              </div>
            </div>
          </el-option>
        </el-select>

        <div v-if="availableChannels.length === 0 && !channelReplaceLoading" class="no-channels-tip">
          <el-empty description="暂无可用的通道" :image-size="80" />
        </div>
      </div>

      <template #footer>
        <el-button @click="handleCancelChannelReplace">取消</el-button>
        <el-button
          type="primary"
          @click="handleSaveChannelReplace"
          :loading="channelReplaceLoading"
          :disabled="!selectedChannelId"
        >
          确定替换
        </el-button>
      </template>
    </el-dialog>

    <!-- 新增通道对话框 -->
    <el-dialog v-model="channelAddDialogVisible" title="新增通道" width="500px" :before-close="handleCancelChannelAdd">
      <div class="dialog-content">
        <p class="add-tip">请从下拉菜单中选择要添加的通道：</p>

        <el-select
          v-model="selectedChannelIdForAdd"
          placeholder="请选择要添加的通道"
          style="width: 100%"
          :loading="channelAddLoading"
          filterable
          clearable
        >
          <template #empty>
            <div class="select-empty">
              <el-empty description="暂无可用的通道" :image-size="60" />
            </div>
          </template>

          <el-option
            v-for="channel in availableChannelsForAdd"
            :key="channel.id"
            :label="`${channel.brand_name} - ${channel.channel_id} (${channel.ip})`"
            :value="channel.id"
          >
            <div class="channel-option">
              <div class="channel-main-info">
                <span class="channel-name">{{ channel.brand_name }} - {{ channel.channel_id }}</span>
              </div>
            </div>
          </el-option>
        </el-select>

        <div v-if="availableChannelsForAdd.length === 0 && !channelAddLoading" class="no-channels-tip">
          <el-empty description="暂无可用的通道" :image-size="80" />
        </div>
      </div>

      <template #footer>
        <el-button @click="handleCancelChannelAdd">取消</el-button>
        <el-button type="primary" @click="handleSaveChannelAdd" :loading="channelAddLoading" :disabled="!selectedChannelIdForAdd">
          确定添加
        </el-button>
      </template>
    </el-dialog>
  </el-drawer>
</template>

<script setup lang="tsx">
import { ref, computed, reactive } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { Search, ArrowDown, Plus } from "@element-plus/icons-vue";
import ProTable from "@/components/ProTable/index.vue";
import { ColumnProps } from "@/components/ProTable/interface";
import {
  getStoreSceneDetails,
  unbindStoreScene,
  getStoreCameraChannels,
  replaceModelCameraChannel,
  removeModelCameraChannel,
  addModelCameraChannel,
  type StoreSceneDetail
} from "@/api/modules/store";

interface DrawerProps {
  title: string;
  storeId: number;
  storeName: string;
  getTableList?: () => void;
}

const drawerVisible = ref(false);
const loading = ref(false);

const drawerProps = ref<DrawerProps>({
  title: "",
  storeId: 0,
  storeName: ""
});

// 搜索表单
const searchForm = reactive({
  name: ""
});

// 场景详情列表
const sceneDetails = ref<StoreSceneDetail[]>([]);

// 展开状态
const expandedScenes = ref<number[]>([]);
const expandedModels = ref<number[]>([]);

// 通道替换相关状态
const channelReplaceDialogVisible = ref(false);
const availableChannels = ref<any[]>([]);
const selectedChannelId = ref<number | null>(null);
const currentChannelId = ref(0);
const currentModelId = ref(0);
const currentSceneId = ref(0);
const channelReplaceLoading = ref(false);

// 新增通道相关状态
const channelAddDialogVisible = ref(false);
const availableChannelsForAdd = ref<any[]>([]);
const selectedChannelIdForAdd = ref<number | null>(null);
const currentModelForAdd = ref<any>(null);
const currentSceneForAdd = ref<any>(null);
const channelAddLoading = ref(false);

// 通道表格列定义
const channelColumns: ColumnProps[] = [
  { prop: "channel_id", label: "通道编号", minWidth: 120 },
  { prop: "brand_name", label: "品牌", minWidth: 120 },
  { prop: "type", label: "类型", minWidth: 100 },
  { prop: "ip", label: "IP地址", minWidth: 150 },
  { prop: "user", label: "用户名", minWidth: 120 },
  {
    prop: "status",
    label: "状态",
    minWidth: 100,
    render: (scope: any) => {
      return (
        <el-tag type={scope.row.status === 1 ? "success" : "danger"} size="small">
          {scope.row.status === 1 ? "可用" : "不可用"}
        </el-tag>
      );
    }
  },
  {
    prop: "operation",
    label: "操作",
    width: 120,
    fixed: "right",
    render: (scope: any) => {
      return (
        <div>
          <el-button type="primary" size="small" link onClick={() => handleReplaceChannel(scope.row)}>
            替换
          </el-button>
          <el-button type="danger" size="small" link onClick={() => handleRemoveChannel(scope.row)}>
            移除
          </el-button>
        </div>
      );
    }
  }
];

// 计算属性
const drawerTitle = computed(() => {
  return drawerProps.value.title || "场景管理";
});

const totalModels = computed(() => {
  return sceneDetails.value.reduce((total, scene) => total + (scene.models?.length || 0), 0);
});

const totalChannels = computed(() => {
  return sceneDetails.value.reduce((total, scene) => {
    return (
      total +
      (scene.models?.reduce((modelTotal, model) => {
        return modelTotal + (model.camera_channels?.length || 0);
      }, 0) || 0)
    );
  }, 0);
});

const filteredSceneDetails = computed(() => {
  if (!searchForm.name) {
    return sceneDetails.value;
  }
  return sceneDetails.value.filter(scene => scene.name.toLowerCase().includes(searchForm.name.toLowerCase()));
});

// 打开抽屉
const openDrawer = (props: DrawerProps) => {
  drawerProps.value = props;
  drawerVisible.value = true;

  // 重置搜索条件
  searchForm.name = "";
  expandedScenes.value = [];
  expandedModels.value = [];

  // 加载场景详情
  loadSceneDetails();
};

// 默认展开所有模型
const expandAllModels = () => {
  const allModelIds: number[] = [];
  sceneDetails.value.forEach(scene => {
    if (scene.models) {
      scene.models.forEach(model => {
        allModelIds.push(model.id);
      });
    }
  });
  expandedModels.value = allModelIds;
};

// 关闭抽屉
const handleClose = () => {
  drawerVisible.value = false;
  expandedScenes.value = [];
  expandedModels.value = [];
};

// 加载场景详情
const loadSceneDetails = async () => {
  if (!drawerProps.value.storeId) return;

  loading.value = true;
  try {
    const response = await getStoreSceneDetails(drawerProps.value.storeId);
    if (response.data) {
      sceneDetails.value = response.data;
      // 加载完成后自动展开所有模型，方便用户看到新增通道按钮
      expandAllModels();
    } else {
      sceneDetails.value = [];
    }
  } catch {
    ElMessage.error("加载场景详情失败");
    sceneDetails.value = [];
  } finally {
    loading.value = false;
  }
};

// 搜索处理
const handleSearch = () => {
  // 搜索逻辑已在computed中处理
};

// 切换场景展开状态
const toggleSceneExpanded = (sceneId: number) => {
  const index = expandedScenes.value.indexOf(sceneId);
  if (index > -1) {
    expandedScenes.value.splice(index, 1);
    // 收起场景时也收起所有模型
    expandedModels.value = expandedModels.value.filter(modelId => {
      const scene = sceneDetails.value.find(s => s.id === sceneId);
      return !scene?.models?.some(m => m.id === modelId);
    });
  } else {
    expandedScenes.value.push(sceneId);
  }
};

// 切换模型展开状态
const toggleModelExpanded = (modelId: number) => {
  const index = expandedModels.value.indexOf(modelId);
  if (index > -1) {
    expandedModels.value.splice(index, 1);
  } else {
    expandedModels.value.push(modelId);
  }
};

// 解绑场景
const unbindScene = async (scene: StoreSceneDetail) => {
  try {
    await ElMessageBox.confirm(`确定要解绑场景"${scene.name}"吗？解绑后将删除该场景与门店的所有关联关系。`, "确认解绑", {
      type: "warning"
    });

    // 调用解绑场景API
    await unbindStoreScene({
      store_id: drawerProps.value.storeId,
      scene_id: scene.id
    });

    ElMessage.success("解绑成功");

    // 重新加载场景详情
    await loadSceneDetails();

    // 通知父组件刷新表格数据
    if (drawerProps.value.getTableList) {
      drawerProps.value.getTableList();
    }
  } catch (error: any) {
    if (error !== "cancel") {
      ElMessage.error("解绑失败");
    }
  }
};

// 替换通道
const handleReplaceChannel = async (channel: any) => {
  // 找到通道所属的场景和模型
  let foundScene: any = null;
  let foundModel: any = null;

  for (const scene of sceneDetails.value) {
    if (scene.models) {
      for (const model of scene.models) {
        if (model.camera_channels) {
          const foundChannel = model.camera_channels.find((c: any) => c.id === channel.id);
          if (foundChannel) {
            foundScene = scene;
            foundModel = model;
            break;
          }
        }
      }
    }
    if (foundScene) break;
  }

  if (foundScene && foundModel) {
    currentSceneId.value = foundScene.id;
    currentModelId.value = foundModel.id;
    currentChannelId.value = channel.id;
    selectedChannelId.value = null;

    // 加载门店可用通道列表
    await loadAvailableChannels();
    channelReplaceDialogVisible.value = true;
  }
};

// 移除通道
const handleRemoveChannel = async (channel: any) => {
  try {
    await ElMessageBox.confirm(`确定要移除通道"${channel.channel_id}"吗？`, "确认移除", {
      type: "warning"
    });

    // 找到通道所属的场景和模型
    let foundScene: any = null;
    let foundModel: any = null;

    for (const scene of sceneDetails.value) {
      if (scene.models) {
        for (const model of scene.models) {
          if (model.camera_channels) {
            const foundChannel = model.camera_channels.find((c: any) => c.id === channel.id);
            if (foundChannel) {
              foundScene = scene;
              foundModel = model;
              break;
            }
          }
        }
      }
      if (foundScene) break;
    }

    if (foundScene && foundModel) {
      // 调用API删除模型摄像头通道关系
      await removeModelCameraChannel({
        store_id: drawerProps.value.storeId,
        scene_id: foundScene.id,
        model_id: foundModel.id,
        channel_id: channel.id
      });

      // 从模型中移除通道
      if (foundModel.camera_channels) {
        const index = foundModel.camera_channels.findIndex((c: any) => c.id === channel.id);
        if (index > -1) {
          foundModel.camera_channels.splice(index, 1);
        }
      }

      ElMessage.success("移除成功");
    }
  } catch (error: any) {
    if (error !== "cancel") {
      ElMessage.error("移除失败");
    }
  }
};

// 加载可用通道列表
const loadAvailableChannels = async () => {
  try {
    channelReplaceLoading.value = true;
    const response = await getStoreCameraChannels(drawerProps.value.storeId);

    // API返回的数据结构是 { code: 200, data: [...] }
    const channels = (response as any).data || [];

    // 只过滤掉当前模型中的通道，不排除其他模型中的通道
    const currentModelChannelIds = new Set();
    const currentScene = sceneDetails.value.find(scene => scene.id === currentSceneId.value);
    if (currentScene && currentScene.models) {
      const currentModel = currentScene.models.find(model => model.id === currentModelId.value);
      if (currentModel && currentModel.camera_channels) {
        currentModel.camera_channels.forEach(channel => {
          currentModelChannelIds.add(channel.id);
        });
      }
    }

    availableChannels.value = channels.filter((channel: any) => !currentModelChannelIds.has(channel.id));
  } catch {
    ElMessage.error("加载可用通道失败");
    availableChannels.value = [];
  } finally {
    channelReplaceLoading.value = false;
  }
};

// 保存通道替换
const handleSaveChannelReplace = async () => {
  if (!selectedChannelId.value) {
    ElMessage.warning("请选择要替换的通道");
    return;
  }

  if (selectedChannelId.value === currentChannelId.value) {
    ElMessage.warning("不能选择相同的通道");
    return;
  }

  try {
    channelReplaceLoading.value = true;

    // 调用API替换模型摄像头通道关系
    await replaceModelCameraChannel({
      store_id: drawerProps.value.storeId,
      scene_id: currentSceneId.value,
      model_id: currentModelId.value,
      old_channel_id: currentChannelId.value,
      new_channel_id: selectedChannelId.value
    });

    // 找到对应的场景和模型，更新通道信息
    const scene = sceneDetails.value.find((s: any) => s.id === currentSceneId.value);
    if (scene && scene.models) {
      const model = scene.models.find((m: any) => m.id === currentModelId.value);
      if (model && model.camera_channels) {
        const channelIndex = model.camera_channels.findIndex((c: any) => c.id === currentChannelId.value);
        if (channelIndex > -1) {
          // 找到新通道信息
          const newChannel = availableChannels.value.find(c => c.id === selectedChannelId.value);
          if (newChannel) {
            // 更新通道信息，保留关系ID
            const originalChannel = model.camera_channels[channelIndex];
            model.camera_channels[channelIndex] = {
              ...newChannel,
              relation_id: originalChannel.relation_id
            };
          }
        }
      }
    }

    ElMessage.success("替换成功");
    channelReplaceDialogVisible.value = false;
  } catch {
    ElMessage.error("替换失败");
  } finally {
    channelReplaceLoading.value = false;
  }
};

// 取消通道替换
const handleCancelChannelReplace = () => {
  channelReplaceDialogVisible.value = false;
  selectedChannelId.value = null;
  currentChannelId.value = 0;
  availableChannels.value = [];
};

// 新增通道
const handleAddChannel = async (model: any) => {
  // 找到模型所属的场景
  let foundScene: any = null;
  for (const scene of sceneDetails.value) {
    if (scene.models) {
      const foundModel = scene.models.find((m: any) => m.id === model.id);
      if (foundModel) {
        foundScene = scene;
        break;
      }
    }
  }

  if (!foundScene) {
    ElMessage.error("未找到对应的场景");
    return;
  }

  currentModelForAdd.value = model;
  currentSceneForAdd.value = foundScene;
  selectedChannelIdForAdd.value = null;

  // 加载门店可用通道列表
  await loadAvailableChannelsForAdd();
  channelAddDialogVisible.value = true;
};

// 加载门店可用通道列表（用于新增）
const loadAvailableChannelsForAdd = async () => {
  try {
    channelAddLoading.value = true;
    const response = await getStoreCameraChannels(drawerProps.value.storeId);

    // API返回的数据结构是 { code: 200, data: [...] }
    const channels = (response as any).data || [];

    // 只过滤掉当前模型中的通道，不排除其他模型中的通道
    const currentModelChannelIds = new Set();
    if (currentModelForAdd.value && currentModelForAdd.value.camera_channels) {
      currentModelForAdd.value.camera_channels.forEach(channel => {
        currentModelChannelIds.add(channel.id);
      });
    }

    availableChannelsForAdd.value = channels.filter((channel: any) => !currentModelChannelIds.has(channel.id));
  } catch {
    ElMessage.error("加载可用通道失败");
    availableChannelsForAdd.value = [];
  } finally {
    channelAddLoading.value = false;
  }
};

// 保存新增通道
const handleSaveChannelAdd = async () => {
  if (!selectedChannelIdForAdd.value) {
    ElMessage.warning("请选择要添加的通道");
    return;
  }

  try {
    channelAddLoading.value = true;

    // 调用API新增模型摄像头通道关系
    await addModelCameraChannel({
      store_id: drawerProps.value.storeId,
      scene_id: currentSceneForAdd.value.id,
      model_id: currentModelForAdd.value.id,
      channel_id: selectedChannelIdForAdd.value
    });

    // 更新本地数据
    const selectedChannel = availableChannelsForAdd.value.find((channel: any) => channel.id === selectedChannelIdForAdd.value);

    if (selectedChannel && currentModelForAdd.value) {
      if (!currentModelForAdd.value.camera_channels) {
        currentModelForAdd.value.camera_channels = [];
      }
      currentModelForAdd.value.camera_channels.push({
        ...selectedChannel,
        relation_id: Date.now() // 临时ID，实际应该从API返回
      });
    }

    ElMessage.success("添加成功");
    channelAddDialogVisible.value = false;
  } catch {
    ElMessage.error("添加失败");
  } finally {
    channelAddLoading.value = false;
  }
};

// 取消新增通道
const handleCancelChannelAdd = () => {
  channelAddDialogVisible.value = false;
  selectedChannelIdForAdd.value = null;
  currentModelForAdd.value = null;
  currentSceneForAdd.value = null;
  availableChannelsForAdd.value = [];
};

// 暴露方法给父组件
defineExpose({
  openDrawer
});
</script>

<style scoped lang="scss">
.store-scene-drawer {
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.search-area {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.statistics-info {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.scene-details-list {
  flex: 1;
  overflow-y: auto;
}

.scene-detail-card {
  margin-bottom: 16px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  background: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.scene-detail-card:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  border-color: #409eff;
}

.scene-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 16px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.scene-header:hover {
  background-color: #f5f7fa;
}

.scene-info {
  flex: 1;

  .scene-title-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;
  }

  .scene-name {
    margin: 0;
    color: #303133;
    font-size: 18px;
  }

  .expand-icon {
    font-size: 16px;
    color: #909399;
    transition: transform 0.3s ease;
  }

  .expand-icon.expanded {
    transform: rotate(180deg);
  }

  .scene-meta {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;

    .scene-desc {
      color: #909399;
      font-size: 14px;
    }
  }
}

.scene-actions {
  margin-left: 16px;
}

.scene-models {
  padding: 16px;
  background: #fafafa;
}

.models-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.model-detail-card {
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 12px;
  transition: all 0.3s ease;
}

.model-detail-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-color: #409eff;
}

.model-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
  cursor: pointer;
  transition: background-color 0.2s ease;
  padding: 8px;
  margin: -8px -8px 8px -8px;
  border-radius: 4px;
}

.model-header:hover {
  background-color: #f5f7fa;
}

.model-info {
  flex: 1;

  .model-title-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 4px;
  }

  .model-name {
    margin: 0;
    color: #303133;
    font-size: 16px;
  }

  .expand-icon {
    font-size: 14px;
    color: #909399;
    transition: transform 0.3s ease;
  }

  .expand-icon.expanded {
    transform: rotate(180deg);
  }

  .model-desc {
    margin: 0;
    color: #909399;
    font-size: 14px;
  }
}

.model-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.model-channels {
  margin-top: 12px;
  width: 100%;
}

.channels-container {
  margin-top: 8px;
  width: 100%;
  overflow-x: auto;
}

.no-channels,
.no-models {
  text-align: center;
  padding: 20px;
}

.empty-state {
  text-align: center;
  padding: 40px;
}

:deep(.el-drawer__body) {
  padding: 0;
}

/* 通道表格样式 */
.channel-table {
  width: 100%;
}

:deep(.channel-table .el-table) {
  font-size: 12px;
  width: 100% !important;
}

:deep(.channel-table .el-table th) {
  background: #f5f7fa;
}

:deep(.channel-table .el-table td) {
  background: #fff;
}

:deep(.channel-table .el-table tbody tr:hover td) {
  background: #f5f7fa;
}

:deep(.channel-table .el-table__body-wrapper) {
  width: 100% !important;
}

:deep(.channel-table .el-table__header-wrapper) {
  width: 100% !important;
}

/* 通道替换对话框样式 */
.channel-replace-content {
  padding: 20px 0;
}

.replace-tip {
  margin: 0 0 16px 0;
  color: #606266;
  font-size: 14px;
}

.channel-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.channel-main-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}

.channel-name {
  font-weight: 500;
  color: #303133;
}

.channel-ip {
  font-size: 12px;
  color: #909399;
}

.no-channels-tip {
  margin-top: 20px;
  text-align: center;
}

.select-empty {
  padding: 20px;
  text-align: center;
}

/* 响应式优化 */
@media (max-width: 768px) {
  :deep(.channel-table .el-table) {
    font-size: 11px;
  }

  :deep(.channel-table .el-table .el-table__cell) {
    padding: 8px 4px;
  }

  .channels-container {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
}
</style>
