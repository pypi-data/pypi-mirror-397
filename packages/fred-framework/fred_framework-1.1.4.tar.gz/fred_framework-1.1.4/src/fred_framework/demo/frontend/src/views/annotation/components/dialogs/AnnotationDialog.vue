<template>
  <el-dialog
    :model-value="visible"
    width="95%"
    top="1vh"
    custom-class="annotation-dialog"
    :close-on-click-modal="false"
    @close="handleClose"
    @update:model-value="$emit('update:visible', $event)"
  >
    <template #header>
      <div class="dialog-header">
        <span class="dialog-title">{{ dialogTitle }}</span>
        <el-tooltip content="切换功能区显示/隐藏（快捷键：空格键）" placement="bottom">
          <el-button
            :icon="showSidebar ? Hide : View"
            circle
            size="small"
            type="primary"
            @click="toggleSidebar"
            class="sidebar-toggle-btn"
          />
        </el-tooltip>
      </div>
    </template>
    <div class="annotation-detail">
      <div class="image-annotation-container">
        <AnnotationCanvas
          ref="annotationCanvasRef"
          :current-image="currentImage"
          :annotations="annotations"
          :selected-annotation="selectedAnnotation"
          :available-labels="availableLabels"
          :selected-label-for-new-annotation="selectedLabelForNewAnnotation"
          :get-image-url="getImageUrl"
          :image-dimensions="imageDimensions"
          :image-info="imageInfo"
          :new-annotation-preview="newAnnotationPreview"
          :last-resize-end-time="props.lastResizeEndTime"
          :show-label-name="showLabelName"
          @image-load="handleImageLoad"
          @image-error="handleImageError"
          @image-height-change="handleImageHeightChange"
          @select-annotation="handleSelectAnnotation"
          @create-annotation-start="handleCreateAnnotationStart"
          @annotation-mouse-down="handleAnnotationMouseDown"
          @resize-start="handleResizeStart"
        />

        <Transition name="slide-fade">
          <div v-show="showSidebar" class="floating-sidebar">
            <AnnotationList
              :current-image="currentImage"
              :annotations="annotations"
              :selected-annotation="selectedAnnotation"
              :available-labels="availableLabels"
              :selected-label-for-new-annotation="selectedLabelForNewAnnotation"
              :show-annotation-list="showAnnotationList"
              :external-model-id="selectedModelId"
              :max-height="imageDisplayHeight"
              @select-annotation="handleSelectAnnotation"
              @delete-annotation="handleDeleteAnnotation"
              @update-selected-label="handleUpdateSelectedLabel"
              @clear-selected-label="handleClearSelectedLabel"
              @toggle-annotation-list="handleToggleAnnotationList"
              @toggle-annotation-visibility="handleToggleAnnotationVisibility"
              @toggle-group-visibility="handleToggleGroupVisibility"
              @load-labels-for-model="handleLoadLabelsForModel"
              @select-model="handleSelectModel"
              @change-label="handleChangeLabel"
              @navigate-image="handleNavigateImage"
              @toggle-label-name-visibility="handleToggleLabelNameVisibility"
              @batch-delete-annotations="handleBatchDeleteAnnotations"
              @add-inference-annotations="handleAddInferenceAnnotations"
              @toggle-label-group-visibility="handleToggleLabelGroupVisibility"
            />
          </div>
        </Transition>

        <!-- 标注分组侧滑悬浮框 -->
        <Transition name="slide-fade-left">
          <AnnotationGroupDialog
            v-show="showGroupDialog"
            :annotations="annotations"
            :selected-annotation="selectedAnnotation"
            @select-annotation="handleSelectAnnotation"
            @delete-annotation="handleDeleteAnnotation"
            @batch-delete-annotations="handleBatchDeleteAnnotations"
            @toggle-annotation-visibility="handleToggleAnnotationVisibility"
            @toggle-group-visibility="handleToggleGroupVisibility"
            @toggle-label-group-visibility="handleToggleLabelGroupVisibility"
            @change-label="handleChangeLabel"
          />
        </Transition>
      </div>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, onUnmounted, watch } from "vue";
import { Hide, View } from "@element-plus/icons-vue";
import AnnotationCanvas from "../canvas/AnnotationCanvas.vue";
import AnnotationList from "../lists/AnnotationList.vue";
import AnnotationGroupDialog from "./AnnotationGroupDialog.vue";

interface AnnotationDetail {
  id: number;
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
}

interface Label {
  id: number;
  name: string;
  color: string;
}

interface ImageInfo {
  id: number | null;
  file_name: string;
  file_path: string;
  width?: number;
  height?: number;
  format?: string;
  project_name?: string;
  deleted?: number; // 删除状态：0-正常，1-已删除
}

interface Props {
  visible: boolean;
  currentImage: ImageInfo | null;
  annotations: AnnotationDetail[];
  selectedAnnotation: AnnotationDetail | null;
  availableLabels: Label[];
  selectedLabelForNewAnnotation: number;
  imageDimensions: { width: number; height: number };
  imageInfo: ImageInfo | null;
  getImageUrl: (filePath: string) => string;
  showAnnotationList: boolean;
  selectedModelId?: number | null;
  newAnnotationPreview?: {
    show: boolean;
    x: number;
    y: number;
    width: number;
    height: number;
  };
  lastResizeEndTime?: number;
}

const props = defineProps<Props>();

// 图片实际显示高度，用于限制右侧列表高度
const imageDisplayHeight = ref<number | null>(null);

// 全局标签名显示状态（默认隐藏）
const showLabelName = ref(false);

// 功能区显示/隐藏状态（默认显示）
const showSidebar = ref(true);

// 标注分组弹框显示/隐藏状态（默认隐藏）
const showGroupDialog = ref(false);

// 切换功能区显示/隐藏
const toggleSidebar = () => {
  showSidebar.value = !showSidebar.value;
};

// 切换标注分组弹框显示/隐藏
const toggleGroupDialog = () => {
  showGroupDialog.value = !showGroupDialog.value;
};

// 键盘事件处理函数
const handleKeyDown = (event: KeyboardEvent) => {
  // 只在对话框可见时响应快捷键
  if (!props.visible) return;

  // 如果用户正在输入框中输入，不响应快捷键
  const target = event.target as HTMLElement;
  if (target.tagName === "INPUT" || target.tagName === "TEXTAREA" || target.isContentEditable) {
    return;
  }

  // 按下空格键切换功能区显示/隐藏
  if (event.key === " " || event.code === "Space") {
    event.preventDefault(); // 防止页面滚动
    toggleSidebar();
  }

  // 按下G键切换标注分组弹框显示/隐藏
  if (event.key === "g" || event.key === "G" || event.code === "KeyG") {
    event.preventDefault();
    toggleGroupDialog();
  }
};

// 监听对话框可见性变化，动态添加/移除键盘事件监听
watch(
  () => props.visible,
  newVisible => {
    if (newVisible) {
      window.addEventListener("keydown", handleKeyDown);
    } else {
      window.removeEventListener("keydown", handleKeyDown);
    }
  },
  { immediate: true }
);

// 组件卸载时移除事件监听
onUnmounted(() => {
  window.removeEventListener("keydown", handleKeyDown);
});

const emit = defineEmits<{
  "update:visible": [value: boolean];
  close: [];
  imageLoad: [event: Event];
  imageError: [event: Event];
  selectAnnotation: [annotation: AnnotationDetail];
  deleteAnnotation: [annotation: AnnotationDetail];
  createAnnotationStart: [event: MouseEvent];
  annotationMouseDown: [event: MouseEvent | TouchEvent, annotation: AnnotationDetail];
  resizeStart: [event: MouseEvent | TouchEvent, annotation: AnnotationDetail, handle: string];
  updateSelectedLabel: [labelId: number];
  clearSelectedLabel: [];
  toggleAnnotationList: [];
  toggleAnnotationVisibility: [annotation: AnnotationDetail];
  toggleGroupVisibility: [group: any];
  toggleLabelGroupVisibility: [labelGroup: any];
  loadLabelsForModel: [labels: any[] | null];
  selectModel: [modelId: number | null];
  changeLabel: [annotation: AnnotationDetail];
  navigateImage: [direction: "prev" | "next"];
  batchDeleteAnnotations: [annotations: AnnotationDetail[]];
  addInferenceAnnotations: [annotations: AnnotationDetail[]];
}>();

const annotationCanvasRef = ref();

const dialogTitle = computed(() => {
  const imageName = props.currentImage?.file_name || "";
  const isUnannotated = props.currentImage?.id === null || props.currentImage?.id === undefined;
  const status = isUnannotated ? "未标注图片" : "标注详情";
  return `${status} - ${imageName} (快捷键：A/D 切换图片，W/S 切换标注，C 删除标注，X 切换标签，Q 显示/隐藏标注，空格键 切换功能区，G 显示/隐藏分组弹框，R 删除图片，Ctrl+滚轮 缩放图片，ESC 关闭)`;
});

const handleClose = () => {
  emit("close");
};

const handleImageLoad = (event: Event) => {
  emit("imageLoad", event);
};

const handleImageError = (event: Event) => {
  emit("imageError", event);
};

const handleImageHeightChange = (height: number) => {
  // 减小标注列表高度，减去40px，确保不影响图片区域
  imageDisplayHeight.value = Math.max(0, height - 40);
};

const handleSelectAnnotation = (annotation: AnnotationDetail) => {
  emit("selectAnnotation", annotation);
};

const handleDeleteAnnotation = (annotation: AnnotationDetail) => {
  emit("deleteAnnotation", annotation);
};

const handleCreateAnnotationStart = (event: MouseEvent) => {
  emit("createAnnotationStart", event);
};

const handleAnnotationMouseDown = (event: MouseEvent | TouchEvent, annotation: AnnotationDetail) => {
  emit("annotationMouseDown", event, annotation);
};

const handleResizeStart = (event: MouseEvent | TouchEvent, annotation: AnnotationDetail, handle: string) => {
  emit("resizeStart", event, annotation, handle);
};

const handleUpdateSelectedLabel = (labelId: number) => {
  emit("updateSelectedLabel", labelId);
};

const handleClearSelectedLabel = () => {
  emit("clearSelectedLabel");
};

const handleToggleAnnotationList = () => {
  emit("toggleAnnotationList");
};

const handleToggleAnnotationVisibility = (annotation: AnnotationDetail) => {
  emit("toggleAnnotationVisibility", annotation);
};

const handleToggleGroupVisibility = (group: any) => {
  emit("toggleGroupVisibility", group);
};

const handleLoadLabelsForModel = (labels: any[] | null) => {
  emit("loadLabelsForModel", labels);
};

const handleSelectModel = (modelId: number | null) => {
  emit("selectModel", modelId);
};

const handleChangeLabel = (annotation: AnnotationDetail) => {
  emit("changeLabel", annotation);
};

const handleNavigateImage = (direction: "prev" | "next") => {
  emit("navigateImage", direction);
};

const handleToggleLabelNameVisibility = (value: boolean) => {
  showLabelName.value = value;
};

const handleBatchDeleteAnnotations = (annotations: AnnotationDetail[]) => {
  emit("batchDeleteAnnotations", annotations);
};

const handleAddInferenceAnnotations = (annotations: AnnotationDetail[]) => {
  emit("addInferenceAnnotations", annotations);
};

const handleToggleLabelGroupVisibility = (labelGroup: any) => {
  emit("toggleLabelGroupVisibility", labelGroup);
};

// 暴露方法给父组件
defineExpose({
  annotationCanvasRef
});
</script>

<style lang="scss" scoped>
.annotation-detail {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;

  .image-annotation-container {
    position: relative;
    height: 100%;
    min-height: 0;
    background: #f5f5f5;
    overflow: hidden;

    /* 图片区域全屏显示 */
    > :first-child {
      width: 100%;
      height: 100%;
      min-width: 0;
      min-height: 0;
      overflow: hidden; // 防止出现滚动条
    }

    /* 浮动功能区 */
    .floating-sidebar {
      position: absolute;
      top: 0;
      right: 0;
      bottom: 0;
      width: 350px;
      max-width: 100%; /* 确保不会超出父容器 */
      z-index: 10;
      background: #fff;
      box-shadow: -2px 0 8px rgba(0, 0, 0, 0.15);
      overflow-y: auto; /* 允许垂直滚动 */
      overflow-x: hidden; /* 防止水平溢出 */
      display: flex;
      flex-direction: column;
      box-sizing: border-box; /* 确保宽度计算包含内边距和边框 */
    }
  }
}

/* 左侧滑入动画 */
.slide-fade-left-enter-active {
  transition: all 0.3s ease-out;
}

.slide-fade-left-leave-active {
  transition: all 0.3s ease-in;
}

.slide-fade-left-enter-from {
  transform: translateX(-100%);
  opacity: 0;
}

.slide-fade-left-leave-to {
  transform: translateX(-100%);
  opacity: 0;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding-right: 80px; // 为关闭按钮留出足够空间，避免重叠
  position: relative;

  .dialog-title {
    flex: 1;
    font-size: 16px;
    font-weight: 500;
    color: var(--el-text-color-primary);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    padding-right: 12px; // 与按钮保持间距
  }

  .sidebar-toggle-btn {
    margin-left: 12px;
    margin-right: 20px; // 增加右边距，让按钮向左移动，避免与关闭按钮重叠
    flex-shrink: 0;
    position: relative;
    z-index: 1; // 确保按钮在关闭按钮上方
    box-shadow: 0 2px 8px rgba(64, 158, 255, 0.4); // 添加蓝色阴影，让按钮更突出
    transition: all 0.3s ease; // 添加过渡动画

    &:hover {
      box-shadow: 0 4px 12px rgba(64, 158, 255, 0.6); // 悬停时阴影更明显
      transform: scale(1.05); // 悬停时稍微放大
    }

    &:active {
      transform: scale(0.95); // 点击时稍微缩小
    }
  }
}

/* 过渡动画 */
.slide-fade-enter-active {
  transition: all 0.3s ease-out;
}

.slide-fade-leave-active {
  transition: all 0.3s ease-in;
}

.slide-fade-enter-from {
  transform: translateX(100%);
  opacity: 0;
}

.slide-fade-leave-to {
  transform: translateX(100%);
  opacity: 0;
}

:deep(.annotation-dialog) {
  margin-top: 1vh !important;
  height: 98vh;
  display: flex;
  flex-direction: column;
  max-height: 98vh;

  .el-dialog__header {
    flex-shrink: 0;
    padding: 15px 20px;
    border-bottom: 1px solid var(--el-border-color-lighter);
    position: relative;

    // 确保关闭按钮有足够的空间，不与自定义按钮重叠
    .el-dialog__headerbtn {
      right: 20px;
      top: 15px;
      z-index: 10; // 确保关闭按钮在最上层
    }
  }

  .el-dialog__body {
    padding: 0;
    flex: 1;
    min-height: 0;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }

  .el-dialog__footer {
    display: none;
  }
}
</style>
