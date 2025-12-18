<template>
  <div class="annotations-info" :style="{ maxHeight: props.maxHeight ? `${props.maxHeight}px` : '100%' }">
    <!-- 图片切换按钮 -->
    <div class="image-navigation-section">
      <el-button-group class="navigation-button-group">
        <el-button size="default" type="primary" plain @click="handlePrevImage">
          <el-icon><ArrowLeft /></el-icon>
          <span>上一张</span>
        </el-button>
        <el-button size="default" type="primary" plain @click="handleNextImage">
          <span>下一张</span>
          <el-icon><ArrowRight /></el-icon>
        </el-button>
      </el-button-group>
    </div>
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

    <!-- 新增标注标签选择器 - 根据模型选择动态显示 -->
    <div v-if="selectedModelId" class="new-annotation-controls">
      <div class="label-header">
        <h4>{{ t("annotation.newAnnotationLabel") }}</h4>
        <el-button
          size="small"
          type="danger"
          plain
          @click="$emit('clearSelectedLabel')"
          :disabled="selectedLabelForNewAnnotation === 0"
          class="clear-button"
        >
          {{ t("annotation.clearSelection") }}
        </el-button>
      </div>
      <div class="label-selector">
        <el-radio-group
          :model-value="selectedLabelForNewAnnotation"
          @update:model-value="$emit('updateSelectedLabel', $event)"
          size="small"
        >
          <el-radio-button
            v-for="label in availableLabels"
            :key="label.id"
            :label="label.id"
            :style="{ '--label-color': label.color }"
          >
            <span class="label-text">
              <span class="label-color-indicator" :style="{ backgroundColor: label.color }"></span>
              <span class="label-sort" v-if="label.sort !== undefined && label.sort !== null">#{{ label.sort }}</span>
              {{ label.name }}
            </span>
          </el-radio-button>
        </el-radio-group>
      </div>
      <div class="instruction">
        <el-text type="info" size="small"> {{ t("annotation.dragToCreate") }} </el-text>
        <el-text v-if="currentImage?.id === null || currentImage?.id === undefined" type="warning" size="small">
          {{ t("annotation.unannotatedImage") }}
        </el-text>
      </div>
    </div>

    <!-- 图片信息和标注列表 - 始终显示 -->
    <div class="annotation-list-section">
      <div class="annotation-list-header">
        <div class="header-left">
          <div class="title-section">
            <h4>{{ t("annotation.list") }}</h4>
            <el-tag size="small" type="info" effect="plain" class="count-tag">
              {{ annotations.length }}
            </el-tag>
          </div>
        </div>
        <div class="header-right">
          <div class="toggle-group">
            <div class="label-name-toggle">
              <el-switch
                v-model="showLabelNameModel"
                :active-text="'显示名称'"
                :inactive-text="'隐藏名称'"
                size="small"
                @change="handleToggleLabelNameVisibility"
              />
            </div>
            <div class="annotation-toggle">
              <el-switch
                v-model="showAnnotationListModel"
                :active-text="t('annotation.show')"
                :inactive-text="t('annotation.hide')"
                size="small"
              />
            </div>
          </div>
        </div>
      </div>
      <!-- 推理操作栏（始终显示） -->
      <div class="inference-actions-bar">
        <div class="inference-actions-inline">
          <el-button
            size="small"
            type="primary"
            :disabled="!currentImage?.id || !selectedModelId"
            @click="handleSystemInference"
            :loading="systemInferenceLoading"
            class="system-inference-button"
          >
            系统推理
          </el-button>
          <div class="auto-inference-switch-wrapper">
            <span class="switch-label">自动推理</span>
            <el-switch
              v-model="autoInferenceEnabled"
              :disabled="!currentImage?.id || !selectedModelId"
              size="small"
              class="auto-inference-switch"
            />
          </div>
        </div>
      </div>
      <div v-if="annotations.length === 0" class="no-annotations">
        <el-empty
          :description="
            currentImage?.id === null || currentImage?.id === undefined
              ? t('annotation.unannotatedImageNoAnnotations')
              : t('annotation.noAnnotationsInfo')
          "
          :image-size="100"
        >
          <template #image v-if="currentImage?.id === null || currentImage?.id === undefined">
            <el-icon :size="60" color="#409EFF">
              <svg viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg">
                <path
                  d="M512 128c-211.2 0-384 172.8-384 384s172.8 384 384 384 384-172.8 384-384-172.8-384-384-384z m0 682.7c-164.3 0-298.7-134.4-298.7-298.7S347.7 213.3 512 213.3 810.7 347.7 810.7 512 676.3 810.7 512 810.7z m0-469.3c-94.3 0-170.7 76.4-170.7 170.7S417.7 682.7 512 682.7 682.7 606.3 682.7 512 606.3 341.3 512 341.3z"
                  fill="currentColor"
                />
                <path d="M512 469.3m-42.7 0a42.7 42.7 0 1 0 85.4 0 42.7 42.7 0 1 0-85.4 0Z" fill="currentColor" />
                <path d="M597.3 597.3L469.3 469.3" stroke="currentColor" stroke-width="42.7" stroke-linecap="round" />
              </svg>
            </el-icon>
          </template>
        </el-empty>
      </div>
      <div v-else class="annotation-list-container">
        <div class="annotation-list-tip">
          <el-text type="info" size="small">标注列表已迁移到分组弹框，按 G 键打开</el-text>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, nextTick, watch } from "vue";
import { useI18n } from "vue-i18n";
import { ArrowLeft, ArrowRight } from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";
import { getModelListApi } from "@/api/modules/model";
import type { ModelInfo } from "@/api/model/modelModel";
import { getLabelListByModelApi } from "@/api/modules/label";
import type { Label } from "@/api/model/labelModel";
import { systemInferenceApi } from "@/api/modules/annotation";

// 国际化
const { t } = useI18n();

interface AnnotationDetail {
  id: number;
  sort?: number;
  label_name: string;
  label_color: string;
  yolo_format: {
    label_id: number;
    center_x: number;
    center_y: number;
    width: number;
    height: number;
  };
  isModified?: boolean;
  isNew?: boolean;
  isVisible?: boolean;
  is_own?: boolean;
  is_auto?: boolean;
}

interface Label {
  id: number;
  name: string;
  color: string;
  sort?: number;
}

interface ImageInfo {
  id: number | null;
  file_name: string;
  file_path: string;
  width?: number;
  height?: number;
  format?: string;
  project_name?: string;
}

interface Props {
  currentImage: ImageInfo | null;
  annotations: AnnotationDetail[];
  selectedAnnotation: AnnotationDetail | null;
  availableLabels: Label[];
  selectedLabelForNewAnnotation: number;
  showAnnotationList: boolean;
  externalModelId?: number | null;
  maxHeight?: number | null;
}

const props = defineProps<Props>();

// 模型相关状态
const modelList = ref<ModelInfo[]>([]);
const modelLoading = ref(false);
const selectedModelId = ref<number | null>(null);
const modelSelectRef = ref<any>(null);

// 同步加载模型标签（不触发事件，用于内部同步）
const syncLoadLabelsForModel = async (modelId: number) => {
  try {
    // 加载该模型的标签
    const response = await getLabelListByModelApi({ modelId });

    if (response && response.data) {
      // 处理响应数据，可能 records 字段存在但为空数组
      const labels = response.data.records || [];
      if (Array.isArray(labels)) {
        emit("loadLabelsForModel", labels);
        emit("updateSelectedLabel", 0); // 清空选中的标签
        // 如果标签列表为空，不显示错误，这是正常情况
        if (labels.length === 0) {
        }
      } else {
        console.warn("标签列表响应格式异常:", response);
        ElMessage.warning(t("annotation.getLabelListFailed"));
      }
    } else {
      console.warn("获取标签列表响应为空:", response);
      ElMessage.warning(t("annotation.getLabelListFailed"));
    }
  } catch (error: any) {
    // 判断是否为请求取消错误（参考项目中 api/index.ts 的处理方式）
    const isCanceled =
      error?.name === "CanceledError" ||
      error?.code === "ERR_CANCELED" ||
      (error?.message && error.message.toLowerCase().includes("canceled"));

    if (isCanceled) {
      // 请求被取消是正常行为（用户快速切换模型等），不显示错误提示
      return;
    }

    // 真正的错误才显示提示
    console.error("获取标签列表失败:", error);
    ElMessage.error(t("annotation.getLabelListFailed"));
  }
};

// 监听外部传入的模型ID
watch(
  () => props.externalModelId,
  newModelId => {
    if (newModelId !== undefined && newModelId !== selectedModelId.value) {
      selectedModelId.value = newModelId;
      if (newModelId) {
        // 从外部同步时，只加载标签，不触发selectModel事件
        syncLoadLabelsForModel(newModelId);
      } else {
        // 清空时也要触发
        emit("loadLabelsForModel", null);
        emit("updateSelectedLabel", 0);
      }
    }
  },
  { immediate: true }
);

// 系统推理加载状态
const systemInferenceLoading = ref(false);

// 自动推理开关状态
const autoInferenceEnabled = ref(false);

// 计算属性处理开关的双向绑定
const showAnnotationListModel = computed({
  get: () => props.showAnnotationList,
  set: () => {
    // 当开关状态改变时，触发父组件的切换事件
    emit("toggleAnnotationList");
  }
});

// 全局显示标签名状态（默认隐藏）
const showLabelNameModel = ref(false);

// 处理全局标签名显示/隐藏切换
const handleToggleLabelNameVisibility = (value: boolean) => {
  showLabelNameModel.value = value;
  // 通知父组件更新所有标注的标签名显示状态
  emit("toggleLabelNameVisibility", value);
};

const emit = defineEmits<{
  batchDeleteAnnotations: [annotations: AnnotationDetail[]];
  updateSelectedLabel: [labelId: number];
  clearSelectedLabel: [];
  toggleAnnotationList: [];
  loadLabelsForModel: [labels: Label[] | null];
  selectModel: [modelId: number | null];
  navigateImage: [direction: "prev" | "next"];
  toggleLabelNameVisibility: [value: boolean];
  addInferenceAnnotations: [annotations: AnnotationDetail[]];
}>();

// 系统推理
const handleSystemInference = async () => {
  if (!props.currentImage?.id) {
    ElMessage.warning("请先选择图片");
    return;
  }

  if (!selectedModelId.value) {
    ElMessage.warning("请先选择模型");
    return;
  }

  try {
    systemInferenceLoading.value = true;
    const response = await systemInferenceApi({
      image_id: props.currentImage.id,
      model_id: selectedModelId.value
    });

    if (response && typeof response === "object" && response.code === 200) {
      const responseData = (response as any).data?.data || (response as any).data || {};
      const inferenceAnnotations = (responseData as any).annotations || [];

      if (Array.isArray(inferenceAnnotations) && inferenceAnnotations.length > 0) {
        // 将返回的标注数据转换为AnnotationDetail格式，并设置为系统标注
        const formattedAnnotations: AnnotationDetail[] = inferenceAnnotations
          .filter((ann: any) => {
            // 过滤掉缺少ID的标注
            if (!ann.id) {
              console.warn("标注缺少ID，跳过该标注:", ann);
              return false;
            }
            return true;
          })
          .map((ann: any) => {
            // 确保yolo_format格式正确
            const yoloFormat = ann.yolo_format || {};
            const labelId = ann.label_id || yoloFormat.label_id || 0;

            return {
              id: ann.id,
              label_name: ann.label_name || "未知标签",
              label_color: ann.label_color || "#909399",
              label_id: labelId,
              yolo_format: {
                label_id: labelId,
                center_x: yoloFormat.center_x || 0,
                center_y: yoloFormat.center_y || 0,
                width: yoloFormat.width || 0,
                height: yoloFormat.height || 0
              },
              confidence: ann.confidence !== undefined ? ann.confidence : null,
              is_auto: ann.is_auto !== undefined ? ann.is_auto : true, // 系统标注
              is_own: ann.is_own !== undefined ? ann.is_own : false, // 不是当前用户的标注
              isVisible: true, // 默认可见
              isModified: false,
              isNew: false
            };
          });

        if (formattedAnnotations.length > 0) {
          // 触发事件，将推理结果添加到系统分类下
          emit("addInferenceAnnotations", formattedAnnotations);
          ElMessage.success(`系统推理完成，已添加 ${formattedAnnotations.length} 个标注到系统分类`);
        } else {
          ElMessage.warning("系统推理完成，但返回的标注数据格式不正确");
        }
      } else {
        ElMessage.info("系统推理完成，未检测到标注");
      }
    } else {
      ElMessage.error(response?.message || "系统推理失败");
    }
  } catch (error: any) {
    console.error("系统推理失败:", error);
    ElMessage.error(error?.message || "系统推理失败，请稍后重试");
  } finally {
    systemInferenceLoading.value = false;
  }
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

// 处理模型选择变化
const handleModelChange = async (modelId: number | null) => {
  // 通知父组件模型选择变化
  emit("selectModel", modelId);

  if (!modelId) {
    // 清除选中标签并重新加载所有标签
    emit("updateSelectedLabel", 0);
    emit("loadLabelsForModel", null);
    return;
  }

  try {
    // 加载该模型的标签
    const response = await getLabelListByModelApi({ modelId });

    if (response && response.data) {
      // 处理响应数据，可能 records 字段存在但为空数组
      const labels = response.data.records || [];
      if (Array.isArray(labels)) {
        emit("loadLabelsForModel", labels);
        emit("updateSelectedLabel", 0); // 清空选中的标签
        // 如果标签列表为空，不显示错误，这是正常情况
        if (labels.length === 0) {
        }
      } else {
        console.warn("标签列表响应格式异常:", response);
        ElMessage.warning(t("annotation.getLabelListFailed"));
      }
    } else {
      console.warn("获取标签列表响应为空:", response);
      ElMessage.warning(t("annotation.getLabelListFailed"));
    }
  } catch (error: any) {
    // 判断是否为请求取消错误（参考项目中 api/index.ts 的处理方式）
    const isCanceled =
      error?.name === "CanceledError" ||
      error?.code === "ERR_CANCELED" ||
      (error?.message && error.message.toLowerCase().includes("canceled"));

    if (isCanceled) {
      // 请求被取消是正常行为（用户快速切换模型等），不显示错误提示
      return;
    }

    // 真正的错误才显示提示
    console.error("获取标签列表失败:", error);
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

// 处理上一张图片
const handlePrevImage = () => {
  emit("navigateImage", "prev");
};

// 处理下一张图片
const handleNextImage = () => {
  emit("navigateImage", "next");
};

// 监听图片切换，如果自动推理开启则自动调用推理接口
watch(
  () => props.currentImage?.id,
  (newImageId, oldImageId) => {
    // 只有当图片ID真正变化时才触发（排除初始化和null值）
    // oldImageId为undefined表示是初始化，不需要触发
    if (
      autoInferenceEnabled.value &&
      newImageId &&
      oldImageId !== undefined &&
      newImageId !== oldImageId &&
      selectedModelId.value
    ) {
      // 延迟执行，确保图片切换完成后再调用推理接口
      nextTick(() => {
        handleSystemInference();
      });
    }
  }
);

// 组件挂载时加载模型列表
onMounted(() => {
  loadModelList();
});
</script>

<style lang="scss" scoped>
.annotations-info {
  width: 100%;
  max-width: 100%; /* 确保不会超出父容器 */
  background: #f8f9fa;
  padding: 16px;
  display: flex;
  flex-direction: column;
  overflow-y: auto; /* 允许垂直滚动 */
  overflow-x: hidden; /* 防止水平溢出 */
  height: 100%;
  max-height: 100%;
  min-height: 0;
  box-sizing: border-box; /* 确保宽度计算包含内边距 */

  .image-navigation-section {
    margin-bottom: 16px;
    padding: 12px;
    background: white;
    border-radius: 4px;
    border: 1px solid #e4e7ed;
    display: flex;
    justify-content: center;
    align-items: center;
    flex-shrink: 0;

    .navigation-button-group {
      display: flex;
      justify-content: center;

      .el-button {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        font-size: 14px;
        height: 36px;
        min-width: 100px;

        .el-icon {
          font-size: 16px;
        }
      }
    }
  }

  .model-selector-section {
    margin-bottom: 16px;
    padding: 12px;
    background: white;
    border-radius: 4px;
    border: 1px solid #e4e7ed;
    flex-shrink: 0;
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
      max-width: 100%; /* 确保不会超出容器 */
      overflow: hidden; /* 防止内容溢出 */
    }
  }

  .new-annotation-controls {
    margin-bottom: 20px;
    padding: 16px;
    background: white;
    border-radius: 6px;
    border: 1px solid #e4e7ed;
    flex-shrink: 0;

    h4 {
      margin: 0 0 12px 0;
      font-size: 14px;
      color: #303133;
    }

    .label-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;

      h4 {
        margin: 0;
        font-size: 14px;
        color: #303133;
      }

      .clear-button {
        font-weight: 600;
        border-width: 2px;
        transition: all 0.3s ease;

        &:not(:disabled):hover {
          transform: translateY(-1px);
          box-shadow: 0 4px 8px rgba(245, 108, 108, 0.3);
        }

        &:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
      }
    }

    .label-selector {
      margin-bottom: 12px;
      width: 100%;
      max-width: 100%;
      overflow: hidden;

      .el-radio-group {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        width: 100%;
        max-width: 100%;

        .el-radio-button {
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
          }
        }
      }
    }

    .instruction {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }
  }

  .annotation-list-section {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-height: 0;
    overflow: hidden;
  }

  .annotation-list-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 12px;
    flex-shrink: 0;

    .header-left {
      display: flex;
      align-items: center;
      gap: 8px;
      flex: 1;

      .title-section {
        display: flex;
        align-items: center;
        gap: 6px;

        h4 {
          margin: 0;
          font-size: 14px;
          color: #303133;
        }

        .count-tag {
          font-size: 11px;
          padding: 2px 6px;
          border-radius: 10px;
          background-color: #f0f2f5;
          color: #606266;
          border: 1px solid #e4e7ed;
        }
      }

      .collapse-all-button {
        display: flex;
        align-items: center;
        gap: 4px;
        padding: 4px 8px;
        font-size: 12px;
        color: #606266;
        transition: all 0.2s ease;

        &:hover {
          color: #409eff;
          background-color: #f0f9ff;
        }

        .collapse-icon {
          transition: transform 0.2s ease;
          font-size: 12px;

          &.collapsed {
            transform: rotate(-90deg);
          }
        }
      }
    }

    .header-right {
      display: flex;
      flex-direction: column;
      align-items: flex-end;
      gap: 8px;

      .toggle-group {
        display: flex;
        flex-direction: column;
        gap: 8px;
        align-items: flex-end;

        .label-name-toggle,
        .annotation-toggle {
          .el-switch {
            --el-switch-on-color: #409eff;
            --el-switch-off-color: #dcdfe6;
          }
        }
      }
    }
  }

  h4 {
    margin: 0 0 12px 0;
    font-size: 14px;
    color: #303133;
  }

  .no-annotations {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 200px;
  }

  .annotation-list-container {
    flex: 1;
    min-height: 0;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    height: 0; /* 确保 flex 子元素能够正确计算高度 */

    .annotation-list-tip {
      display: flex;
      justify-content: center;
      align-items: center;
      padding: 20px;
      min-height: 100px;
    }
  }

  .inference-actions-bar {
    display: flex;
    justify-content: flex-start;
    align-items: center;
    padding: 8px 0;
    margin-bottom: 12px;
    flex-shrink: 0;

    .inference-actions-inline {
      display: flex;
      align-items: center;
      gap: 8px;

      .system-inference-button {
        font-size: 12px;
        padding: 4px 8px;

        &:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
      }

      .auto-inference-switch-wrapper {
        display: flex;
        align-items: center;
        gap: 6px;
        margin-left: 8px;

        .switch-label {
          font-size: 12px;
          color: #606266;
          white-space: nowrap;
        }

        .auto-inference-switch {
          flex-shrink: 0;
        }
      }

      .batch-delete-button {
        font-size: 12px;
        padding: 4px 8px;
        margin-left: 8px;

        &:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
      }
    }
  }

  .annotation-tabs {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-height: 0;
    overflow: hidden;

    :deep(.el-tabs__header) {
      margin: 0 0 12px 0;
      flex-shrink: 0;
    }

    :deep(.el-tabs__content) {
      flex: 1;
      min-height: 0;
      overflow-y: auto;
      overflow-x: hidden;
      height: 0; /* 确保 flex 子元素能够正确计算高度 */
    }

    :deep(.el-tab-pane) {
      height: 100%;
      display: flex;
      flex-direction: column;
      min-height: 0;
      overflow: visible;
    }

    .tab-label {
      display: flex;
      align-items: center;
      gap: 6px;

      .label-color-indicator {
        width: 12px;
        height: 12px;
        border-radius: 2px;
        flex-shrink: 0;
      }

      .tab-name {
        font-weight: 500;
      }

      .tab-count {
        margin-left: 2px;
      }
    }

    .tab-header-actions {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 8px 0;
      margin-bottom: 8px;
      border-bottom: 1px solid #e4e7ed;
      flex-shrink: 0;

      .tab-actions-left {
        display: flex;
        align-items: center;
        gap: 8px;

        .group-select-checkbox {
          flex-shrink: 0;
        }

        .group-select-button {
          font-size: 12px;
          padding: 4px 8px;
          color: #409eff;
          transition: all 0.2s ease;

          &:hover {
            color: #66b1ff;
            background-color: #f0f9ff;
          }
        }
      }

      .tab-actions-right {
        display: flex;
        gap: 8px;
        align-items: center;

        .el-button {
          font-size: 12px;
          padding: 4px 8px;
        }
      }
    }

    .tab-content {
      flex: 1;
      overflow-y: auto;
      overflow-x: hidden;
      min-height: 0;
      padding: 8px 0;

      /* 自定义滚动条样式 */
      &::-webkit-scrollbar {
        width: 4px;
      }

      &::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 2px;
      }

      &::-webkit-scrollbar-thumb {
        background: #c1c1c1;
        border-radius: 2px;

        &:hover {
          background: #a8a8a8;
        }
      }

      &.group-hidden {
        opacity: 0.6;
      }

      .empty-group {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 200px;
      }

      .annotation-items-list {
        display: flex;
        flex-direction: column;
        gap: 8px;
      }

      .label-group {
        border: 1px solid #e4e7ed;
        border-radius: 6px;
        background: #fafafa;
        overflow: hidden;
        transition: all 0.2s ease;

        &.label-group-hidden {
          opacity: 0.6;
          background: #f5f5f5;
          border-color: #d3d4d6;
        }

        .label-group-header {
          padding: 8px 12px;
          background: #f5f7fa;
          border-bottom: 1px solid #e4e7ed;
          transition: background-color 0.2s ease;
          display: flex;
          justify-content: space-between;
          align-items: center;
          gap: 12px;

          .label-group-title {
            display: flex;
            align-items: center;
            gap: 8px;
            flex: 1;
            min-width: 0;
            cursor: pointer;

            &:hover {
              opacity: 0.8;
            }

            .collapse-icon {
              transition: transform 0.2s ease;
              font-size: 12px;
              color: #606266;

              &.collapsed {
                transform: rotate(-90deg);
              }
            }

            .label-color-indicator {
              width: 12px;
              height: 12px;
              border-radius: 2px;
              flex-shrink: 0;
            }

            .label-group-name {
              font-weight: 500;
              color: #303133;
              flex: 1;
              min-width: 0;
            }
          }

          .label-group-actions {
            display: flex;
            align-items: center;
            gap: 8px;
            flex-shrink: 0;

            .label-group-select-checkbox {
              flex-shrink: 0;
            }

            .label-group-visibility-button {
              font-size: 12px;
              padding: 4px 8px;
            }
          }
        }

        .label-group-content {
          padding: 4px;
          display: flex;
          flex-direction: column;
          gap: 4px;
        }
      }
    }
  }

  .annotation-group {
    margin-bottom: 12px;
    border: 1px solid #e4e7ed;
    border-radius: 8px;
    background: white;
    overflow: hidden;
    transition: all 0.2s ease;

    &.group-hidden {
      opacity: 0.6;
      background: #f5f5f5;
      border-color: #d3d4d6;
    }

    .group-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 16px;
      background: #f8f9fa;
      border-bottom: 1px solid #e4e7ed;
      cursor: pointer;
      transition: background-color 0.2s ease;

      &:hover {
        background: #e9ecef;
      }

      .group-title {
        display: flex;
        align-items: center;
        gap: 8px;
        flex: 1;
        min-width: 0;

        .collapse-icon {
          transition: transform 0.2s ease;
          font-size: 14px;
          color: #606266;

          &.collapsed {
            transform: rotate(-90deg);
          }
        }

        .label-color-indicator {
          width: 14px;
          height: 14px;
          border-radius: 3px;
          flex-shrink: 0;
        }

        .group-name {
          font-weight: 500;
          color: #303133;
          flex: 1;
          min-width: 0;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }
      }

      .group-actions {
        display: flex;
        gap: 8px;
        align-items: center;

        .el-button {
          font-size: 12px;
          padding: 4px 8px;
        }
      }
    }

    .group-content {
      padding: 8px;
    }
  }

  .annotation-item {
    background: white;
    border: 1px solid #e4e7ed;
    border-radius: 6px;
    padding: 8px 10px;
    margin-bottom: 4px;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    justify-content: space-between;

    &:hover {
      border-color: #409eff;
      box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
    }

    &.active {
      border-color: #409eff;
      background: #f0f9ff;
      box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
    }

    &.modified {
      border-color: #e6a23c;
      background: #fdf6ec;
    }

    &.new-annotation {
      border-color: #67c23a;
      background: #f0f9ff;
    }

    &.hidden-annotation {
      opacity: 0.6;
      background: #f5f5f5;
      border-color: #d3d4d6;
    }

    .annotation-header {
      display: flex;
      align-items: center;
      gap: 8px;
      flex: 1;
      min-width: 0;
      cursor: pointer;

      .el-checkbox {
        flex-shrink: 0;
      }

      .annotation-name {
        display: flex;
        align-items: center;
        gap: 6px;
        font-weight: 500;
        color: #303133;
        flex: 1;
        min-width: 0;
        cursor: pointer;
        user-select: none;

        .annotation-index {
          font-size: 12px;
          color: #909399;
          font-weight: 400;
          min-width: 20px;
        }
      }

      .annotation-status {
        display: flex;
        gap: 4px;
        align-items: center;
      }
    }

    .annotation-actions {
      display: flex;
      gap: 8px;
      align-items: center;

      .el-button {
        font-size: 12px;
        padding: 4px 8px;
      }

      .annotation-visibility-button {
        font-size: 12px;
        padding: 4px 8px;
      }
    }
  }
}
</style>
