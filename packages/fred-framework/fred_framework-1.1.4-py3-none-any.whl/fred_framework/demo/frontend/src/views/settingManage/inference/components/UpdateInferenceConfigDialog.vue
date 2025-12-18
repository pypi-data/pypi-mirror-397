<template>
  <el-drawer
    :model-value="visible"
    @update:model-value="handleVisibleChange"
    :title="t('inference.updateConfigTitle')"
    :size="drawerSize"
    :close-on-click-modal="false"
    :destroy-on-close="true"
    direction="rtl"
    class="inference-config-update-drawer"
  >
    <div v-if="updateConfig.id" class="update-config-content">
      <!-- 配置信息 -->
      <el-descriptions :column="3" border class="config-info">
        <el-descriptions-item :label="t('inference.storeName')">{{ updateConfig.store_name || "-" }}</el-descriptions-item>
        <el-descriptions-item :label="t('inference.currentVersion')">{{ updateConfig.version || "-" }}</el-descriptions-item>
        <el-descriptions-item :label="t('inference.updateVersion')">
          <el-input
            v-model="editableLatestVersion"
            :placeholder="t('inference.versionPlaceholder')"
            size="small"
            style="width: 200px"
          />
        </el-descriptions-item>
      </el-descriptions>

      <!-- 版本比较提示 -->
      <div class="version-comparison-tip">
        <el-alert
          v-if="updateConfig.version !== editableLatestVersion"
          :title="
            t('inference.versionDifferent', {
              current: updateConfig.version,
              update: editableLatestVersion
            })
          "
          type="warning"
          show-icon
          :closable="false"
        />
        <el-alert v-else :title="t('inference.versionSame')" type="info" :closable="false" show-icon />
      </div>

      <!-- 配置比较 -->
      <div class="config-comparison">
        <div class="comparison-header">
          <h4>{{ t("inference.configComparison") }}</h4>
        </div>

        <div class="comparison-content">
          <div class="config-panel">
            <div class="config-display">
              <JsonViewer
                :content="updateConfig.content || ''"
                :title="t('inference.currentConfig')"
                :height="'calc(100vh - 500px)'"
                :show-stats="true"
                :show-actions="true"
                :show-expand-collapse="true"
                :show-copy="true"
                :show-download="false"
                :download-file-name="`current-config-${updateConfig.version || 'config'}.json`"
              />
            </div>
          </div>

          <div class="config-panel">
            <div class="config-display">
              <JsonViewer
                :content="latestConfig.content || ''"
                :title="t('inference.newConfig')"
                :height="'calc(100vh - 500px)'"
                :show-stats="true"
                :show-actions="true"
                :show-expand-collapse="true"
                :show-copy="true"
                :show-download="false"
                :download-file-name="`latest-config-${editableLatestVersion || 'config'}.json`"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="drawer-footer">
        <el-button @click="handleCancel">{{ t("inference.cancel") }}</el-button>
        <el-button type="primary" @click="handleUpdateConfig" :loading="updateLoading">{{
          t("inference.confirmUpdate")
        }}</el-button>
      </div>
    </template>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from "vue";
import { ElMessage } from "element-plus";
import { useI18n } from "vue-i18n";
import { getLatestInferenceConfig, unifiedUpdateInferenceConfig } from "../api/inference.api";
import { type InferenceConfigInfo } from "../types/inference.types";
import JsonViewer from "@/components/JsonViewer/index.vue";

const { t } = useI18n();

// Props
interface Props {
  visible: boolean;
  updateConfig: InferenceConfigInfo;
}

const props = withDefaults(defineProps<Props>(), {
  visible: false,
  updateConfig: () => ({}) as InferenceConfigInfo
});

// Emits
const emit = defineEmits<{
  "update:visible": [value: boolean];
  success: [];
}>();

// 响应式数据
const updateLoading = ref(false);
const editableLatestVersion = ref<string>("");
const latestConfig = ref<InferenceConfigInfo>({} as InferenceConfigInfo);

// 计算抽屉宽度 - 自适应
const drawerSize = computed(() => {
  const windowWidth = window.innerWidth;
  if (windowWidth <= 768) return "90%";
  if (windowWidth <= 1024) return "60%";
  if (windowWidth <= 1440) return "60%";
  return "40%";
});

// 处理更新配置
const handleUpdateConfig = async () => {
  try {
    updateLoading.value = true;

    // 验证版本号是否为空
    if (!editableLatestVersion.value.trim()) {
      ElMessage.error(t("inference.enterVersion"));
      return;
    }

    // 验证store_id是否存在且为有效整数
    const storeId = latestConfig.value.store_id;
    if (!storeId || isNaN(Number(storeId)) || Number(storeId) <= 0) {
      console.error("store_id验证失败:", {
        storeId,
        type: typeof storeId,
        latestConfig: latestConfig.value
      });
      ElMessage.error(t("inference.storeInfoInvalid"));
      return;
    }

    // 使用统一更新接口，后端自动判断更新或新增
    await unifiedUpdateInferenceConfig({
      store_id: Number(storeId),
      version: editableLatestVersion.value,
      content: latestConfig.value.content
    });

    // 根据版本是否相同显示不同的成功消息
    const isVersionSame = props.updateConfig.version === editableLatestVersion.value;
    if (isVersionSame) {
      ElMessage.success(t("inference.updateSuccess"));
    } else {
      ElMessage.success(t("inference.updateNewVersionSuccess"));
    }

    emit("update:visible", false);
    emit("success");
  } catch (err: unknown) {
    console.error("更新配置失败:", err);
    const anyErr = err as any;
    const errorMessage = anyErr?.response?.data?.message || (anyErr?.message as string) || t("inference.updateFailed");
    ElMessage.error(errorMessage);
  } finally {
    updateLoading.value = false;
  }
};

// 处理可见性变化
const handleVisibleChange = (value: boolean) => {
  emit("update:visible", value);
};

// 处理取消
const handleCancel = () => {
  emit("update:visible", false);
};

// 加载最新配置
const loadLatestConfig = async () => {
  if (!props.updateConfig.store_id) {
    console.error("当前配置store_id无效:", props.updateConfig);
    ElMessage.error(t("inference.storeInfoError"));
    return;
  }

  try {
    // 获取最新配置
    const response = await getLatestInferenceConfig(props.updateConfig.store_id);
    latestConfig.value = response.data;

    // 验证获取到的最新配置是否有效
    if (!latestConfig.value.store_id) {
      console.error("获取最新配置失败，返回数据:", response.data);
      ElMessage.error(t("inference.getLatestConfigFailed"));
      return;
    }

    // 初始化可编辑版本号，默认为最新配置的版本号
    editableLatestVersion.value = latestConfig.value.version || "";
  } catch (err: unknown) {
    console.error("获取最新配置失败:", err);
    const anyErr = err as any;
    const errorMessage = anyErr?.response?.data?.message || (anyErr?.message as string) || t("inference.getLatestConfigFailed");
    ElMessage.error(errorMessage);
  }
};

// 监听visible变化，当打开时加载最新配置
watch(
  () => props.visible,
  newVisible => {
    if (newVisible && props.updateConfig.id) {
      nextTick(() => {
        loadLatestConfig();
      });
    }
  },
  { immediate: true }
);
</script>

<style scoped lang="scss">
.inference-config-update-drawer {
  .update-config-content {
    .config-info {
      margin-bottom: 20px;
    }

    .version-comparison-tip {
      margin-bottom: 20px;
    }

    .config-comparison {
      .comparison-header {
        margin-bottom: 16px;
        padding-bottom: 8px;
        border-bottom: 1px solid #e4e7ed;

        h4 {
          margin: 0;
          color: #303133;
        }
      }

      .comparison-content {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 16px;
        height: calc(100vh - 450px);
        min-height: 450px;

        .config-panel {
          display: flex;
          flex-direction: column;
          border: 1px solid #e4e7ed;
          border-radius: 6px;
          overflow: hidden;

          .config-display {
            flex: 1;
            overflow: hidden;
            background-color: #fafafa;
          }
        }
      }
    }
  }

  .drawer-footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    padding: 16px 0;
    border-top: 1px solid #e4e7ed;
    margin-top: 20px;
  }
}

// 响应式设计
@media (max-width: 768px) {
  .inference-config-update-drawer {
    .update-config-content {
      .config-comparison {
        .comparison-content {
          grid-template-columns: 1fr;
          height: auto;
          min-height: 300px;
        }
      }
    }
  }
}
</style>
