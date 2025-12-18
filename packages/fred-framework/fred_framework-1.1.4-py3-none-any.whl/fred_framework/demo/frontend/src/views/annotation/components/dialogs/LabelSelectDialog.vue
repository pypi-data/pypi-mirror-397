<template>
  <el-dialog
    v-model="dialogVisible"
    title="选择标签"
    width="500px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    @close="handleClose"
  >
    <div class="label-select-dialog-content">
      <!-- 模型选择器 -->
      <div class="model-selector-section">
        <div class="model-header">
          <h4>{{ t("annotation.model") }}</h4>
        </div>
        <div class="model-selector">
          <el-select
            ref="modelSelectRef"
            v-model="selectedModelId"
            :placeholder="t('annotation.selectModel')"
            clearable
            filterable
            :loading="modelLoading"
            @change="handleModelChange"
            @blur="handleModelSelectBlur"
            @visible-change="handleModelSelectVisibleChange"
          >
            <el-option v-for="model in modelList" :key="model.id" :label="model.name" :value="model.id" />
          </el-select>
        </div>
      </div>

      <!-- 标签列表 -->
      <div v-if="!selectedModelId || displayLabels.length === 0" class="no-labels">
        <el-empty description="请先选择模型" :image-size="80">
          <template #image>
            <el-icon :size="60" color="#909399">
              <svg viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg">
                <path
                  d="M512 128c-211.2 0-384 172.8-384 384s172.8 384 384 384 384-172.8 384-384-172.8-384-384-384z m0 682.7c-164.3 0-298.7-134.4-298.7-298.7S347.7 213.3 512 213.3 810.7 347.7 810.7 512 676.3 810.7 512 810.7z"
                  fill="currentColor"
                />
              </svg>
            </el-icon>
          </template>
        </el-empty>
      </div>
      <div v-else class="label-list">
        <div
          v-for="label in displayLabels"
          :key="label.id"
          class="label-item"
          :class="{ selected: selectedLabelId === label.id }"
          @click="selectLabel(label.id)"
        >
          <span class="label-text">
            <span class="label-color-indicator" :style="{ backgroundColor: label.color }"></span>
            <span class="label-sort" v-if="label.sort !== undefined && label.sort !== null">#{{ label.sort }}</span>
            <span class="label-name">{{ label.name }}</span>
            <el-icon v-if="selectedLabelId === label.id" class="check-icon">
              <Check />
            </el-icon>
          </span>
        </div>
      </div>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, computed } from "vue";
import { Check } from "@element-plus/icons-vue";
import { useI18n } from "vue-i18n";
import { ElMessage } from "element-plus";
import { getModelListApi } from "@/api/modules/model";
import type { ModelInfo } from "@/api/model/modelModel";
import { getLabelListByModelApi } from "@/api/modules/label";

const { t } = useI18n();

interface Label {
  id: number;
  name: string;
  color: string;
  sort?: number;
}

interface Props {
  visible: boolean;
  availableLabels: Label[];
  currentLabelId?: number;
  externalModelId?: number | null;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  "update:visible": [value: boolean];
  confirm: [labelId: number];
  close: [];
  loadLabelsForModel: [labels: Label[] | null];
  selectModel: [modelId: number | null];
}>();

const dialogVisible = ref(false);
const selectedLabelId = ref<number>(0);

// 模型相关状态
const modelList = ref<ModelInfo[]>([]);
const modelLoading = ref(false);
const selectedModelId = ref<number | null>(null);
const modelSelectRef = ref<any>(null);

// 本地标签列表状态，用于控制弹框内显示的标签
const localLabels = ref<Label[]>([]);

// 计算显示的标签列表，优先使用本地标签，确保只有成功获取时才显示
const displayLabels = computed(() => {
  // 如果本地有标签（在当前弹框中成功获取的），优先使用
  if (localLabels.value.length > 0) {
    return localLabels.value;
  }
  // 否则使用从父组件传入的标签
  return props.availableLabels || [];
});

// 监听visible变化
watch(
  () => props.visible,
  newVal => {
    dialogVisible.value = newVal;
    if (newVal) {
      // 打开时设置当前选中的标签
      selectedLabelId.value = props.currentLabelId || 0;

      // 打开时同步外部模型选择
      if (props.externalModelId !== undefined && props.externalModelId !== null) {
        selectedModelId.value = props.externalModelId;
        // 如果有模型ID，加载该模型的标签
        if (props.externalModelId) {
          handleModelChangeSync(props.externalModelId);
        } else {
          // 如果没有模型，清空本地标签
          localLabels.value = [];
        }
      } else {
        // 如果没有外部模型ID，清空本地标签，使用父组件传入的标签
        localLabels.value = [];
      }
    } else {
      // 关闭时清空本地标签
      localLabels.value = [];
    }
  }
);

// 监听外部模型ID变化
watch(
  () => props.externalModelId,
  newModelId => {
    if (newModelId !== undefined && newModelId !== selectedModelId.value) {
      selectedModelId.value = newModelId;
      // 如果有模型ID，加载该模型的标签
      if (newModelId) {
        handleModelChangeSync(newModelId);
      } else {
        // 如果没有模型ID，清空本地标签
        localLabels.value = [];
        emit("loadLabelsForModel", null);
      }
    }
  }
);

// 监听dialogVisible变化
watch(dialogVisible, newVal => {
  emit("update:visible", newVal);
});

const selectLabel = (labelId: number) => {
  selectedLabelId.value = labelId;
  // 选择标签后直接确认并关闭弹框
  emit("confirm", labelId);
  handleClose();
};

const handleClose = () => {
  dialogVisible.value = false;
  emit("close");
};

// 加载模型列表
const loadModelList = async () => {
  if (modelList.value.length > 0) return; // 已经加载过了

  try {
    modelLoading.value = true;
    const response = await getModelListApi({
      pageNum: 1,
      pageSize: 1000 // 获取所有模型
    });

    if (response && response.data && response.data.records) {
      modelList.value = response.data.records;
    } else {
      ElMessage.warning(t("annotation.getModelListFailed"));
    }
  } catch (error) {
    console.error("获取模型列表失败:", error);
    ElMessage.error(t("annotation.getModelListFailed"));
  } finally {
    modelLoading.value = false;
  }
};

// 同步加载模型标签（不触发事件，用于内部同步）
const handleModelChangeSync = async (modelId: number) => {
  try {
    // 加载该模型的标签
    const response = await getLabelListByModelApi({ modelId });

    if (response && response.data && response.data.records) {
      const labels = response.data.records;
      // 更新本地标签列表
      localLabels.value = labels;
      emit("loadLabelsForModel", labels);
      selectedLabelId.value = 0; // 清空选中的标签
    } else {
      // 获取失败时清空本地标签
      localLabels.value = [];
      emit("loadLabelsForModel", []);
      ElMessage.warning(t("annotation.getLabelListFailed"));
    }
  } catch (error: any) {
    // 判断是否为请求取消错误（参考项目中 api/index.ts 的处理方式）
    const isCanceled =
      error?.name === "CanceledError" ||
      error?.code === "ERR_CANCELED" ||
      (error?.message && error.message.toLowerCase().includes("canceled"));

    if (isCanceled) {
      // 请求被取消是正常行为（用户快速切换模型等），只清空标签，不显示错误提示
      localLabels.value = [];
      emit("loadLabelsForModel", []);
      return;
    }

    // 真正的错误才显示提示
    console.error("获取标签列表失败:", error);
    localLabels.value = [];
    emit("loadLabelsForModel", []);
    ElMessage.error(t("annotation.getLabelListFailed"));
  }
};

// 处理模型选择变化
const handleModelChange = async (modelId: number | null) => {
  // 通知父组件模型选择变化
  emit("selectModel", modelId);

  if (!modelId) {
    // 清除选中标签并重新加载所有标签
    localLabels.value = [];
    selectedLabelId.value = 0;
    emit("loadLabelsForModel", null);
    return;
  }

  try {
    // 加载该模型的标签
    const response = await getLabelListByModelApi({ modelId });

    if (response && response.data && response.data.records) {
      const labels = response.data.records;
      // 更新本地标签列表
      localLabels.value = labels;
      emit("loadLabelsForModel", labels);
      selectedLabelId.value = 0; // 清空选中的标签
    } else {
      // 获取失败时清空本地标签
      localLabels.value = [];
      emit("loadLabelsForModel", []);
      ElMessage.warning(t("annotation.getLabelListFailed"));
    }
  } catch (error: any) {
    // 判断是否为请求取消错误（参考项目中 api/index.ts 的处理方式）
    const isCanceled =
      error?.name === "CanceledError" ||
      error?.code === "ERR_CANCELED" ||
      (error?.message && error.message.toLowerCase().includes("canceled"));

    if (isCanceled) {
      // 请求被取消是正常行为（用户快速切换模型等），只清空标签，不显示错误提示
      localLabels.value = [];
      emit("loadLabelsForModel", []);
      return;
    }

    // 真正的错误才显示提示
    console.error("获取标签列表失败:", error);
    localLabels.value = [];
    emit("loadLabelsForModel", []);
    ElMessage.error(t("annotation.getLabelListFailed"));
  }

  // 选择后立即失焦，避免快捷键输入到选择框
  if (modelSelectRef.value) {
    // 立即移除焦点，不等待 nextTick
    setTimeout(() => {
      if (modelSelectRef.value) {
        modelSelectRef.value.blur();
        // 确保焦点不在选择框上，将焦点移到 body
        document.body.focus();
      }
    }, 0);
  }
};

// 处理模型选择器失焦
const handleModelSelectBlur = () => {
  // 选择器失焦后，确保不再聚焦
  if (modelSelectRef.value) {
    modelSelectRef.value.blur();
  }
};

// 处理模型选择器下拉框显示/隐藏
const handleModelSelectVisibleChange = (visible: boolean) => {
  // 当下拉框关闭时，确保移除焦点
  if (!visible && modelSelectRef.value) {
    setTimeout(() => {
      if (modelSelectRef.value) {
        modelSelectRef.value.blur();
        // 将焦点移到 body，确保不在选择框上
        document.body.focus();
      }
    }, 0);
  }
};

// 组件挂载时加载模型列表
onMounted(() => {
  loadModelList();
});
</script>

<style lang="scss" scoped>
.label-select-dialog-content {
  .model-selector-section {
    margin-bottom: 16px;
    padding: 12px;
    background: #f8f9fa;
    border-radius: 4px;
    border: 1px solid #e4e7ed;
    display: flex;
    align-items: center;
    gap: 12px;

    .model-header {
      flex-shrink: 0;
      white-space: nowrap;

      h4 {
        margin: 0;
        font-size: 14px;
        color: #303133;
      }
    }

    .model-selector {
      flex: 1;
      min-width: 0;
    }
  }

  .label-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;

    .label-item {
      display: inline-flex;
      align-items: center;
      padding: 6px 12px;
      border: 1px solid #e4e7ed;
      border-radius: 4px;
      cursor: pointer;
      transition: all 0.2s ease;
      background: white;

      &:hover {
        border-color: #409eff;
        background-color: #f0f9ff;
      }

      &.selected {
        border-color: #409eff;
        background-color: #f0f9ff;
        box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
      }

      .label-text {
        display: flex;
        align-items: center;
        gap: 4px;

        .label-color-indicator {
          width: 12px;
          height: 12px;
          border-radius: 2px;
          flex-shrink: 0;
        }

        .label-sort {
          font-size: 11px;
          color: #909399;
          font-weight: 500;
        }

        .label-name {
          font-weight: 500;
          color: #303133;
          white-space: nowrap;
        }

        .check-icon {
          color: #409eff;
          font-size: 14px;
          margin-left: 4px;
        }
      }
    }
  }

  .no-labels {
    padding: 40px 0;
  }
}
</style>
