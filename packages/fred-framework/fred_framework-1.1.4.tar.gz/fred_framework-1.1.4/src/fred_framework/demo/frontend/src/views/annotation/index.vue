<template>
  <div class="annotation-container">
    <!-- 图片网格布局 -->
    <div class="image-grid-container">
      <!-- 搜索条件组件 -->
      <AnnotationSearch
        :search-form="searchForm"
        :export-loading="exportLoading"
        :train-loading="trainLoading"
        @search="handleSearch"
        @reset="handleReset"
        @export-annotations="handleExportAnnotations"
        @train-annotations="handleTrainAnnotations"
        @update-search-form="handleUpdateSearchForm"
      />

      <!-- 视图切换和内容区域 -->
      <div class="grid-header">
        <div class="header-content">
          <div class="header-actions">
            <div class="view-options">
              <el-radio-group v-model="viewMode" size="small">
                <el-radio-button value="grid">
                  <el-icon><Grid /></el-icon>
                  {{ t("annotation.gridView") }}
                </el-radio-button>
                <el-radio-button value="table">
                  <el-icon><List /></el-icon>
                  {{ t("annotation.tableView") }}
                </el-radio-button>
              </el-radio-group>
            </div>
            <!-- 批量操作按钮 -->
            <div class="batch-actions" v-if="validSelectedCount > 0">
              <el-button v-if="isAllSelectedDeleted" type="success" :icon="RefreshRight" @click="handleBatchRestore">
                {{ t("annotation.batchRestore") }} ({{ validSelectedCount }})
              </el-button>
              <el-button v-else type="danger" :icon="Delete" @click="handleBatchDelete">
                {{ t("annotation.batchDelete") }} ({{ validSelectedCount }})
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 网格视图 -->
      <ImageGridView
        v-if="viewMode === 'grid'"
        :image-list="imageList"
        :get-image-url="getImageUrl"
        :format-date="formatDate"
        :selected-items="selectedImages"
        @image-click="openDetailDialog"
        @selection-change="handleGridSelectionChange"
      />

      <!-- 表格视图 -->
      <ImageTableView
        v-else
        :image-list="imageList"
        :get-image-url="getImageUrl"
        :format-date="formatDate"
        @image-click="openDetailDialog"
        @mark-deleted="handleMarkImageDeletedFromTable"
        @selection-change="handleTableSelectionChange"
      />

      <!-- 分页 -->
      <div class="pagination-container" v-if="imageList.length > 0">
        <el-pagination
          v-model:current-page="pagination.current"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[12, 24, 48, 96]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- 标注详情对话框 -->
    <AnnotationDialog
      ref="annotationDialogRef"
      v-model:visible="detailDialogVisible"
      :current-image="currentImage"
      :annotations="annotations"
      :selected-annotation="selectedAnnotation"
      :available-labels="availableLabels"
      :selected-label-for-new-annotation="selectedLabelForNewAnnotation"
      :image-dimensions="imageDimensions"
      :image-info="imageInfo"
      :get-image-url="getImageUrl"
      :new-annotation-preview="newAnnotationPreview"
      :show-annotation-list="showAnnotationList"
      :selected-model-id="selectedModelId"
      :last-resize-end-time="lastResizeEndTime"
      @close="closeDetailDialog"
      @image-load="handleImageLoad"
      @image-error="handleImageError"
      @select-annotation="selectAnnotation"
      @delete-annotation="deleteAnnotation"
      @create-annotation-start="handleCreateAnnotationStart"
      @annotation-mouse-down="handleAnnotationMouseDown"
      @resize-start="handleResizeStart"
      @update-selected-label="handleUpdateSelectedLabel"
      @clear-selected-label="handleClearSelectedLabel"
      @toggle-annotation-list="handleToggleAnnotationList"
      @toggle-annotation-visibility="handleToggleAnnotationVisibility"
      @toggle-group-visibility="handleToggleGroupVisibility"
      @toggle-label-group-visibility="handleToggleLabelGroupVisibility"
      @load-labels-for-model="handleLoadLabelsForModel"
      @select-model="handleAnnotationListModelSelect"
      @change-label="openLabelSelectDialogForEdit"
      @navigate-image="navigateImage"
      @batch-delete-annotations="handleBatchDeleteAnnotations"
      @add-inference-annotations="handleAddInferenceAnnotations"
    />

    <!-- 导出标注对话框 -->
    <ExportDialog
      v-model:visible="exportDialogVisible"
      :available-labels="availableLabels"
      :export-loading="exportLoading"
      @close="closeExportDialog"
      @export="handleExportWithLabels"
    />

    <!-- 远程训练对话框 -->
    <TrainDialog
      v-model:visible="trainDialogVisible"
      :available-labels="availableLabels"
      :train-loading="trainLoading"
      @close="closeTrainDialog"
      @train="handleTrainWithModel"
    />

    <!-- 标签选择对话框 -->
    <LabelSelectDialog
      v-model:visible="labelSelectDialogVisible"
      :available-labels="availableLabels"
      :current-label-id="
        labelSelectDialogMode === 'edit' ? selectedAnnotation?.yolo_format?.label_id || 0 : selectedLabelForNewAnnotation
      "
      :external-model-id="selectedModelId"
      @confirm="handleLabelSelectConfirm"
      @close="closeLabelSelectDialog"
      @select-model="handleLabelDialogModelSelect"
      @load-labels-for-model="handleLoadLabelsForModelFromDialog"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from "vue";
import { useI18n } from "vue-i18n";

// 国际化
const { t } = useI18n();

import { Grid, List, Delete, RefreshRight } from "@element-plus/icons-vue";
import AnnotationSearch from "./components/lists/AnnotationSearch.vue";
import ImageGridView from "./components/views/ImageGridView.vue";
import ImageTableView from "./components/views/ImageTableView.vue";
import AnnotationDialog from "./components/dialogs/AnnotationDialog.vue";
import ExportDialog from "./components/dialogs/ExportDialog.vue";
import TrainDialog from "./components/dialogs/TrainDialog.vue";
import LabelSelectDialog from "./components/dialogs/LabelSelectDialog.vue";
import { useAnnotationData } from "./composables/useAnnotationData";
import { useKeyboardNavigation } from "./composables/useKeyboardNavigation";
import { exportAnnotationsApi, trainInferenceApi, markImageDeletedApi, systemInferenceApi } from "@/api/modules/annotation";
import { ElMessage, ElLoading, ElMessageBox } from "element-plus";

// 使用组合式函数
const {
  imageList,
  annotations,
  availableLabels,
  currentImage,
  selectedAnnotation,
  imageInfo,
  imageDimensions,
  pagination,
  searchForm,
  getImageUrl,
  fetchImageList,
  fetchAnnotationDetail,
  fetchLabelList,
  saveAnnotation,
  deleteAnnotation,
  batchDeleteAnnotations,
  toggleAnnotationVisibility,
  clearGlobalAnnotationVisibility,
  globalAnnotationVisibility,
  globalLabelGroupVisibility
} = useAnnotationData();

// 状态变量
const viewMode = ref<"grid" | "table">("grid");
const detailDialogVisible = ref(false);
const exportDialogVisible = ref(false);
const trainDialogVisible = ref(false);
const labelSelectDialogVisible = ref(false);
const currentImageIndex = ref(0);
const selectedAnnotationIndex = ref(-1);
const selectedLabelForNewAnnotation = ref<number>(0);
// 标记标签选择对话框的用途：'new' 用于创建新标注，'edit' 用于修改现有标注的标签
const labelSelectDialogMode = ref<"new" | "edit">("new");
const exportLoading = ref(false);
const trainLoading = ref(false);
const showAnnotationList = ref(true); // 控制标注列表显示/隐藏
const selectedModelId = ref<number | null>(null); // 当前选择的模型ID
const selectedImages = ref<any[]>([]); // 选中的图片列表
const annotationDialogRef = ref<InstanceType<typeof AnnotationDialog> | null>(null); // 标注对话框引用

// 同步选中列表，过滤掉已删除或不在当前列表中的图片
const syncSelectedImages = () => {
  // 获取当前图片列表的所有ID
  const currentImageIds = new Set(imageList.value.map(img => img.id));

  // 过滤选中列表，只保留在当前列表中的图片
  selectedImages.value = selectedImages.value.filter(item => {
    if (!item || item.id === null || item.id === undefined) return false;

    // 检查图片是否在当前列表中
    const existsInList = currentImageIds.has(item.id);
    if (!existsInList) return false;

    // 从当前列表中获取完整的图片信息，确保 deleted 状态是最新的
    const fullItem = imageList.value.find(img => img.id === item.id);
    if (fullItem) {
      // 更新选中项的信息，确保状态同步
      Object.assign(item, fullItem);
    }

    return true;
  });
};

// 计算有效的选中数量（只统计在当前列表中的图片）
const validSelectedCount = computed(() => {
  const currentImageIds = new Set(imageList.value.map(img => img.id));
  return selectedImages.value.filter(item => {
    if (!item || item.id === null || item.id === undefined) return false;
    return currentImageIds.has(item.id);
  }).length;
});

// 判断选中的图片是否都是已删除状态
const isAllSelectedDeleted = computed(() => {
  if (selectedImages.value.length === 0) return false;
  // 检查所有选中的图片是否都是已删除状态（deleted === 1）
  return selectedImages.value.every(item => {
    if (!item) return false;
    // 如果 deleted 字段存在，直接判断
    if (item.deleted !== undefined && item.deleted !== null) {
      const deletedValue = item.deleted;
      return deletedValue === 1 || deletedValue === "1" || String(deletedValue) === "1";
    }
    // 如果 deleted 字段不存在，从 imageList 中查找
    const fullItem = imageList.value.find(img => img.id === item.id);
    if (fullItem && fullItem.deleted !== undefined && fullItem.deleted !== null) {
      const deletedValue: any = fullItem.deleted;
      return deletedValue === 1 || deletedValue === "1" || String(deletedValue) === "1";
    }
    return false;
  });
});

// 键盘导航
const { addKeyboardListener } = useKeyboardNavigation();
let removeKeyboardListener: (() => void) | null = null;

// 方法
const handleSizeChange = async (val: number) => {
  pagination.pageSize = val;
  await fetchImageList();
  // 分页变化后同步选中列表，过滤掉不在当前列表中的图片
  syncSelectedImages();
};

const handleCurrentChange = async (val: number) => {
  pagination.current = val;
  await fetchImageList();
  // 分页变化后同步选中列表，过滤掉不在当前列表中的图片
  syncSelectedImages();
};

// 搜索方法
const handleSearch = async () => {
  pagination.current = 1;
  await fetchImageList();
  // 搜索后同步选中列表，过滤掉不在当前列表中的图片
  syncSelectedImages();
};

// 重置方法
const handleReset = async () => {
  searchForm.status = null;
  searchForm.material_id = null;
  searchForm.deleted = 0; // 重置为默认值：只显示未删除的图片
  searchForm.annotation_updated_start = null;
  searchForm.annotation_updated_end = null;
  // 清空选择
  selectedImages.value = [];
  await handleSearch();
};

// 更新搜索表单
const handleUpdateSearchForm = (form: Partial<typeof searchForm>) => {
  Object.assign(searchForm, form);
};

// 格式化日期
const formatDate = (dateString: string) => {
  if (!dateString) return "";
  return new Date(dateString).toLocaleDateString("zh-CN");
};

// 打开详情对话框
const openDetailDialog = async (row: any) => {
  // 创建加载实例
  const loading = ElLoading.service({
    lock: true,
    text: t("annotation.loading"),
    background: "rgba(0, 0, 0, 0.7)"
  });

  try {
    // 处理未标注图片的情况
    if (row.id === null || row.id === undefined) {
      // 未标注图片，直接构建图片数据
      loading.close();

      currentImage.value = {
        id: null,
        file_name: row.file_name,
        file_path: row.file_path,
        width: row.width,
        height: row.height,
        created_at: row.created_at
      };

      // 未标注图片没有标注数据
      annotations.value = [];
      imageInfo.value = { ...currentImage.value };

      // 重置选中标注索引
      selectedAnnotationIndex.value = -1;
      selectedAnnotation.value = null;

      currentImageIndex.value = imageList.value.findIndex(
        item => item.file_path === row.file_path && item.file_name === row.file_name
      );
      detailDialogVisible.value = true;
    } else {
      // 已标注图片，调用API获取详情
      const res = await fetchAnnotationDetail(parseInt(row.id.toString()), showAnnotationList.value, selectedModelId.value);
      loading.close();

      if (res) {
        currentImageIndex.value = imageList.value.findIndex(item => item.id === row.id);

        // 确保图片尺寸信息正确设置
        // 如果当前图片有尺寸信息，直接使用
        if (currentImage.value?.width && currentImage.value?.height) {
          imageDimensions.width = currentImage.value.width;
          imageDimensions.height = currentImage.value.height;

          // 同时更新 imageInfo 的宽高信息
          if (imageInfo.value) {
            imageInfo.value.width = currentImage.value.width;
            imageInfo.value.height = currentImage.value.height;
          }
        }

        detailDialogVisible.value = true;

        // 延迟触发标注框重新计算，确保DOM已经更新
        setTimeout(() => {
          if (annotations.value.length > 0) {
            annotations.value = [...annotations.value];
          }
        }, 100);
      }
    }
  } catch (error) {
    loading.close();
    console.error("获取标注详情失败:", error);
    // 错误处理由拦截器统一处理，这里不需要额外的错误提示
  }
};

// 关闭详情对话框
const closeDetailDialog = () => {
  detailDialogVisible.value = false;

  // 重置相关状态，确保下次打开时能正确计算标注位置
  selectedAnnotation.value = null;
  selectedAnnotationIndex.value = -1;

  // 注意：不要重置图片尺寸信息，保持 imageDimensions 和 imageInfo 的宽高信息
  // 这样第二次打开时标注位置计算会更准确
  // 只有在真正需要重新计算时才重置

  // 重置拖拽相关状态
  isDragging.value = false;
  dragAnnotation.value = null;
  isResizing.value = false;
  resizeHandle.value = "";
  isCreatingAnnotation.value = false;

  // 重置变更检测状态
  hasPositionChanged.value = false;
  hasSizeChanged.value = false;

  // 重置新标注预览状态
  newAnnotationPreview.value.show = false;
  newAnnotationStartPos.x = 0;
  newAnnotationStartPos.y = 0;
  newAnnotationEndPos.x = 0;
  newAnnotationEndPos.y = 0;

  // 清理全局标注可见性状态，避免状态累积
  clearGlobalAnnotationVisibility();
};

// 选择标注
const selectAnnotation = (annotation: any) => {
  selectedAnnotation.value = annotation;
  selectedAnnotationIndex.value = annotations.value.findIndex(ann => ann.id === annotation.id);

  // 选择标注时重置变更检测状态，避免误触发保存
  hasPositionChanged.value = false;
  hasSizeChanged.value = false;
};

// 批量删除标注
const handleBatchDeleteAnnotations = async (annotationsToDelete: any[]) => {
  await batchDeleteAnnotations(annotationsToDelete);
};

// 图片加载事件处理
const handleImageLoad = (event: Event) => {
  const img = event.target as HTMLImageElement;

  // 更新图片尺寸信息
  imageDimensions.width = img.naturalWidth;
  imageDimensions.height = img.naturalHeight;

  // 同时更新 imageInfo 的宽高信息，确保标注位置计算正确
  if (imageInfo.value) {
    imageInfo.value.width = img.naturalWidth;
    imageInfo.value.height = img.naturalHeight;
  } else {
    // 如果 imageInfo 不存在，创建一个基本的图片信息对象
    imageInfo.value = {
      ...currentImage.value,
      width: img.naturalWidth,
      height: img.naturalHeight
    };
  }

  // 强制触发标注框重新计算
  // 通过更新 annotations 数组来触发重新渲染
  if (annotations.value.length > 0) {
    annotations.value = [...annotations.value];
  }
};

const handleImageError = (event: Event) => {
  console.error("图片加载失败:", event);
  // 图片加载失败通常不需要用户提示，静默处理
};

// 拖拽相关状态
const isDragging = ref(false);
const dragAnnotation = ref<any>(null);
const dragStartPos = reactive({ x: 0, y: 0 });
const originalPosition = reactive({ x: 0, y: 0, width: 0, height: 0 });
const isResizing = ref(false);
const resizeHandle = ref<string>("");
const resizeStartPos = reactive({ x: 0, y: 0, width: 0, height: 0, center_x: 0, center_y: 0 });
// 记录 resize 结束的时间戳，用于防止 resize 结束后的点击事件改变选中状态
const lastResizeEndTime = ref<number>(0);

// 变更检测相关状态
const hasPositionChanged = ref(false);
const hasSizeChanged = ref(false);

// 拖拽创建新标注相关状态
const isCreatingAnnotation = ref(false);
const newAnnotationStartPos = reactive({ x: 0, y: 0 });
const newAnnotationEndPos = reactive({ x: 0, y: 0 });
const newAnnotationPreview = ref({
  show: false,
  x: 0,
  y: 0,
  width: 0,
  height: 0
});
// 保存当前创建标注时使用的图片元素引用，避免重复查找
const currentImageElementRef = ref<HTMLImageElement | null>(null);

// 拖拽相关函数
const handleAnnotationMouseDown = (event: MouseEvent | TouchEvent, annotation: any) => {
  // 在所有其他任务开始之前检查图片是否已删除
  if (currentImage.value?.deleted === 1 || currentImage.value?.deleted === "1") {
    event.preventDefault();
    event.stopPropagation();
    ElMessage.warning("图片已删除，无法拖拽标注");
    return;
  }

  event.preventDefault();
  event.stopPropagation();

  if (!annotation || !annotation.yolo_format) return;

  // 获取鼠标位置（用于后续计算和记录）
  const clientX = "touches" in event ? event.touches[0].clientX : event.clientX;
  const clientY = "touches" in event ? event.touches[0].clientY : event.clientY;

  // 获取图片元素引用
  const detailImageRef = annotationDialogRef.value?.annotationCanvasRef?.value?.detailImage;
  if (!detailImageRef?.value) {
    // 如果无法获取图片元素，使用传入的标注框
    selectAnnotation(annotation);
    dragAnnotation.value = annotation;
  } else {
    const imgElement = detailImageRef.value as HTMLImageElement;
    const imageRect = imgElement.getBoundingClientRect();

    // 获取图片的原始尺寸和实际显示尺寸
    const naturalWidth = imageInfo.value?.width || imgElement.naturalWidth || 0;
    const naturalHeight = imageInfo.value?.height || imgElement.naturalHeight || 0;
    const displayWidth = imgElement.clientWidth || imgElement.width || naturalWidth;
    const displayHeight = imgElement.clientHeight || imgElement.height || naturalHeight;

    // 计算鼠标在图片上的相对坐标
    const mouseX = clientX - imageRect.left;
    const mouseY = clientY - imageRect.top;

    if (naturalWidth === 0 || naturalHeight === 0 || displayWidth === 0 || displayHeight === 0) {
      // 如果图片尺寸不可用，使用传入的标注框
      selectAnnotation(annotation);
      dragAnnotation.value = annotation;
    } else {
      // 计算缩放比例
      const scaleX = displayWidth / naturalWidth;
      const scaleY = displayHeight / naturalHeight;

      // 找出所有包含鼠标位置的标注框，并计算中心点到鼠标的距离
      const overlappingAnnotations: Array<{ annotation: any; distance: number }> = [];

      annotations.value.forEach(ann => {
        if (!ann.yolo_format || ann.isVisible === false) return;

        const yolo = ann.yolo_format;

        // 计算标注框在显示图片上的位置和尺寸
        const centerX = yolo.center_x * naturalWidth * scaleX;
        const centerY = yolo.center_y * naturalHeight * scaleY;
        const width = yolo.width * naturalWidth * scaleX;
        const height = yolo.height * naturalHeight * scaleY;

        // 计算左上角坐标
        const left = centerX - width / 2;
        const top = centerY - height / 2;

        // 确保坐标在合理范围内
        const clampedLeft = Math.max(0, Math.min(left, displayWidth - width));
        const clampedTop = Math.max(0, Math.min(top, displayHeight - height));
        const clampedWidth = Math.min(width, displayWidth - clampedLeft);
        const clampedHeight = Math.min(height, displayHeight - clampedTop);

        // 检查鼠标位置是否在标注框内
        if (
          mouseX >= clampedLeft &&
          mouseX <= clampedLeft + clampedWidth &&
          mouseY >= clampedTop &&
          mouseY <= clampedTop + clampedHeight
        ) {
          // 计算标注框中心点到鼠标位置的距离
          const centerDisplayX = clampedLeft + clampedWidth / 2;
          const centerDisplayY = clampedTop + clampedHeight / 2;
          const distance = Math.sqrt(Math.pow(mouseX - centerDisplayX, 2) + Math.pow(mouseY - centerDisplayY, 2));
          overlappingAnnotations.push({ annotation: ann, distance });
        }
      });

      // 选择中心点离鼠标最近的标注框
      if (overlappingAnnotations.length > 0) {
        // 按照距离从小到大排序
        overlappingAnnotations.sort((a, b) => a.distance - b.distance);
        const nearestAnnotation = overlappingAnnotations[0].annotation;
        selectAnnotation(nearestAnnotation);
        dragAnnotation.value = nearestAnnotation;
      } else {
        // 如果没有找到包含鼠标位置的标注框，使用传入的标注框
        selectAnnotation(annotation);
        dragAnnotation.value = annotation;
      }
    }
  }

  isDragging.value = true;

  // 记录鼠标起始位置
  dragStartPos.x = clientX;
  dragStartPos.y = clientY;

  // 记录原始位置和尺寸 - 使用实际要拖拽的标注框
  const actualDragAnnotation = dragAnnotation.value;
  if (!actualDragAnnotation || !actualDragAnnotation.yolo_format) {
    isDragging.value = false;
    return;
  }
  originalPosition.x = actualDragAnnotation.yolo_format.center_x;
  originalPosition.y = actualDragAnnotation.yolo_format.center_y;
  originalPosition.width = actualDragAnnotation.yolo_format.width;
  originalPosition.height = actualDragAnnotation.yolo_format.height;

  // 重置变更检测状态
  hasPositionChanged.value = false;
  hasSizeChanged.value = false;

  // 添加全局鼠标事件监听
  document.addEventListener("mousemove", handleMouseMove, { capture: true });
  document.addEventListener("mouseup", handleMouseUp, { capture: true });

  // 添加拖拽样式
  document.body.style.cursor = "move";
  document.body.style.userSelect = "none";

  // 添加触摸事件支持
  if (event.type === "touchstart") {
    document.addEventListener("touchmove", handleTouchMove, { passive: false });
    document.addEventListener("touchend", handleTouchEnd, { passive: false });
  }
};

const handleMouseMove = (event: MouseEvent) => {
  // 在所有其他任务开始之前检查图片是否已删除
  if (currentImage.value?.deleted === 1 || currentImage.value?.deleted === "1") {
    // 如果图片已删除，立即停止拖拽
    ElMessage.warning("图片已删除，无法拖拽标注");
    handleMouseUp();
    return;
  }

  if (!isDragging.value || !dragAnnotation.value || !imageDimensions.width || !imageDimensions.height) return;

  // 计算鼠标移动距离
  const deltaX = event.clientX - dragStartPos.x;
  const deltaY = event.clientY - dragStartPos.y;

  // 使用更小的移动阈值提高灵敏度
  const moveThreshold = 2;
  if (Math.abs(deltaX) < moveThreshold && Math.abs(deltaY) < moveThreshold) {
    return;
  }

  // 获取图片缩放比例
  const imageScale = annotationDialogRef.value?.annotationCanvasRef?.value?.imageScale || 1;

  // 将像素移动转换为YOLO坐标
  // 需要考虑图片的缩放比例，因为标注框会随着图片一起缩放
  const imageWidth = imageDimensions.width;
  const imageHeight = imageDimensions.height;
  const deltaXNormalized = deltaX / imageWidth / imageScale;
  const deltaYNormalized = deltaY / imageHeight / imageScale;

  // 计算新位置
  const newCenterX = Math.max(0, Math.min(1, originalPosition.x + deltaXNormalized));
  const newCenterY = Math.max(0, Math.min(1, originalPosition.y + deltaYNormalized));

  // 检查位置是否发生变化
  const positionThreshold = 0.001; // 位置变化阈值
  if (
    Math.abs(newCenterX - originalPosition.x) > positionThreshold ||
    Math.abs(newCenterY - originalPosition.y) > positionThreshold
  ) {
    hasPositionChanged.value = true;
  }

  // 更新标注位置
  dragAnnotation.value.yolo_format.center_x = newCenterX;
  dragAnnotation.value.yolo_format.center_y = newCenterY;

  // 强制更新视图
  annotations.value = [...annotations.value];
};

const handleMouseUp = () => {
  // 在所有其他任务开始之前检查图片是否已删除
  if (currentImage.value?.deleted === 1 || currentImage.value?.deleted === "1") {
    // 如果图片已删除，不保存，直接停止拖拽
    isDragging.value = false;
    dragAnnotation.value = null;
    // 移除事件监听
    document.removeEventListener("mousemove", handleMouseMove, { capture: true });
    document.removeEventListener("mouseup", handleMouseUp, { capture: true });
    // 恢复样式
    document.body.style.cursor = "";
    document.body.style.userSelect = "";
    return;
  }

  if (!isDragging.value || !dragAnnotation.value) return;

  // 移除事件监听
  document.removeEventListener("mousemove", handleMouseMove, { capture: true });
  document.removeEventListener("mouseup", handleMouseUp, { capture: true });

  // 恢复样式
  document.body.style.cursor = "";
  document.body.style.userSelect = "";

  // 停止拖拽状态
  isDragging.value = false;

  // 只有在位置真正发生变化时才保存
  if (dragAnnotation.value && hasPositionChanged.value) {
    dragAnnotation.value.isModified = true;
    // 拖拽结束后自动保存
    saveAnnotation(dragAnnotation.value);
  }
  dragAnnotation.value = null;
};

const handleTouchMove = (event: TouchEvent) => {
  // 在所有其他任务开始之前检查图片是否已删除
  if (currentImage.value?.deleted === 1 || currentImage.value?.deleted === "1") {
    event.preventDefault();
    event.stopPropagation();
    ElMessage.warning("图片已删除，无法拖拽标注");
    handleTouchEnd();
    return;
  }

  event.preventDefault();

  if (!isDragging.value || !dragAnnotation.value) return;

  const touch = event.touches[0];
  if (!touch) return;

  // 计算触摸移动距离
  const deltaX = touch.clientX - dragStartPos.x;
  const deltaY = touch.clientY - dragStartPos.y;

  const moveThreshold = 3;
  if (Math.abs(deltaX) < moveThreshold && Math.abs(deltaY) < moveThreshold) {
    return;
  }

  // 获取图片缩放比例
  const imageScale = annotationDialogRef.value?.annotationCanvasRef?.value?.imageScale || 1;

  // 将像素移动转换为YOLO坐标
  // 需要考虑图片的缩放比例，因为标注框会随着图片一起缩放
  const imageWidth = imageDimensions.width;
  const imageHeight = imageDimensions.height;
  const deltaXNormalized = deltaX / imageWidth / imageScale;
  const deltaYNormalized = deltaY / imageHeight / imageScale;

  // 计算新位置
  const newCenterX = Math.max(0, Math.min(1, originalPosition.x + deltaXNormalized));
  const newCenterY = Math.max(0, Math.min(1, originalPosition.y + deltaYNormalized));

  // 检查位置是否发生变化
  const positionThreshold = 0.001; // 位置变化阈值
  if (
    Math.abs(newCenterX - originalPosition.x) > positionThreshold ||
    Math.abs(newCenterY - originalPosition.y) > positionThreshold
  ) {
    hasPositionChanged.value = true;
  }

  // 更新标注位置
  dragAnnotation.value.yolo_format.center_x = newCenterX;
  dragAnnotation.value.yolo_format.center_y = newCenterY;

  // 强制更新视图
  annotations.value = [...annotations.value];
};

const handleTouchEnd = () => {
  handleMouseUp();
  document.removeEventListener("touchmove", handleTouchMove);
  document.removeEventListener("touchend", handleTouchEnd);
};

// 调整大小相关函数
const handleResizeStart = (event: MouseEvent | TouchEvent, annotation: any, handle: string) => {
  // 在所有其他任务开始之前检查图片是否已删除
  if (currentImage.value?.deleted === 1 || currentImage.value?.deleted === "1") {
    event.preventDefault();
    event.stopPropagation();
    ElMessage.warning("图片已删除，无法调整标注大小");
    return;
  }

  event.preventDefault();
  event.stopPropagation();

  // 如果有选中的标注框，优先使用选中的标注框进行调整大小
  // 这样可以确保在重叠标注框的情况下，调整的是用户选中的标注框，而不是DOM层级中最上层的框
  // 重要：如果已经有选中的标注框，使用选中的框进行调整大小，不要改变选中状态
  // 只有在没有选中任何框的情况下，才选中传入的标注框并调整大小
  const annotationToResize = selectedAnnotation.value || annotation;

  if (!annotationToResize || !annotationToResize.yolo_format) return;

  // 只有在没有选中任何标注框时，才选中当前传入的标注框
  // 如果已经有选中的标注框，保持选中状态不变，使用选中的框进行调整大小
  if (!selectedAnnotation.value) {
    // 没有选中任何框，选中传入的框
    selectAnnotation(annotation);
    dragAnnotation.value = annotation;
  } else {
    // 已经有选中的框，使用选中的框，不要改变选中状态
    dragAnnotation.value = selectedAnnotation.value;
  }

  isResizing.value = true;
  resizeHandle.value = handle;

  const clientX = "touches" in event ? event.touches[0].clientX : event.clientX;
  const clientY = "touches" in event ? event.touches[0].clientY : event.clientY;

  resizeStartPos.x = clientX;
  resizeStartPos.y = clientY;
  resizeStartPos.width = annotationToResize.yolo_format.width;
  resizeStartPos.height = annotationToResize.yolo_format.height;
  resizeStartPos.center_x = annotationToResize.yolo_format.center_x;
  resizeStartPos.center_y = annotationToResize.yolo_format.center_y;

  // 重置变更检测状态
  hasPositionChanged.value = false;
  hasSizeChanged.value = false;

  // 添加事件监听，使用捕获阶段确保事件优先处理
  document.addEventListener("mousemove", handleResizeMove, { capture: true });
  document.addEventListener("mouseup", handleResizeEnd, { capture: true });
  document.addEventListener("touchmove", handleResizeMove, { capture: true });
  document.addEventListener("touchend", handleResizeEnd, { capture: true });

  // 阻止文本选择
  document.body.style.userSelect = "none";
};

const handleResizeMove = (event: MouseEvent | TouchEvent) => {
  // 在所有其他任务开始之前检查图片是否已删除
  if (currentImage.value?.deleted === 1 || currentImage.value?.deleted === "1") {
    ElMessage.warning("图片已删除，无法调整标注大小");
    handleResizeEnd(event);
    return;
  }

  if (!isResizing.value || !dragAnnotation.value || !imageDimensions.width || !imageDimensions.height) return;

  const clientX = "touches" in event ? event.touches[0].clientX : event.clientX;
  const clientY = "touches" in event ? event.touches[0].clientY : event.clientY;

  const deltaX = clientX - resizeStartPos.x;
  const deltaY = clientY - resizeStartPos.y;

  // 获取图片缩放比例
  const imageScale = annotationDialogRef.value?.annotationCanvasRef?.value?.imageScale || 1;

  // 获取图片实际显示尺寸（使用实际显示的图片尺寸而不是自然尺寸）
  // 这样可以确保缩放比例计算准确，特别是当图片被缩放显示时
  const imgElement = document.querySelector(".annotation-dialog .image-wrapper img") as HTMLImageElement;
  const displayWidth = imgElement?.clientWidth || imgElement?.width || imageDimensions.width;
  const displayHeight = imgElement?.clientHeight || imgElement?.height || imageDimensions.height;

  // 将像素移动转换为YOLO归一化坐标
  // 需要考虑图片的缩放比例，因为标注框会随着图片一起缩放
  const deltaXNormalized = deltaX / displayWidth / imageScale;
  const deltaYNormalized = deltaY / displayHeight / imageScale;

  const annotation = dragAnnotation.value;
  const handle = resizeHandle.value;

  // 计算边界坐标（固定边）
  const leftX = resizeStartPos.center_x - resizeStartPos.width / 2;
  const rightX = resizeStartPos.center_x + resizeStartPos.width / 2;
  const topY = resizeStartPos.center_y - resizeStartPos.height / 2;
  const bottomY = resizeStartPos.center_y + resizeStartPos.height / 2;

  // 根据不同的调整手柄计算新的尺寸和位置
  // 使用更合理的最小尺寸限制（0.005 约等于图片的 0.5%）
  const MIN_SIZE = 0.005;
  let newWidth = resizeStartPos.width;
  let newHeight = resizeStartPos.height;
  let newCenterX = resizeStartPos.center_x;
  let newCenterY = resizeStartPos.center_y;

  switch (handle) {
    case "se": // 右下角 - 右下角移动，左上角固定
      newWidth = Math.max(MIN_SIZE, Math.min(1 - leftX, resizeStartPos.width + deltaXNormalized));
      newHeight = Math.max(MIN_SIZE, Math.min(1 - topY, resizeStartPos.height + deltaYNormalized));
      newCenterX = leftX + newWidth / 2;
      newCenterY = topY + newHeight / 2;
      // 确保中心点和边界不超出范围
      newCenterX = Math.max(newWidth / 2, Math.min(1 - newWidth / 2, newCenterX));
      newCenterY = Math.max(newHeight / 2, Math.min(1 - newHeight / 2, newCenterY));
      break;
    case "sw": // 左下角 - 左下角移动，右上角固定
      newWidth = Math.max(MIN_SIZE, Math.min(rightX, resizeStartPos.width - deltaXNormalized));
      newHeight = Math.max(MIN_SIZE, Math.min(1 - topY, resizeStartPos.height + deltaYNormalized));
      newCenterX = rightX - newWidth / 2;
      newCenterY = topY + newHeight / 2;
      // 确保中心点和边界不超出范围
      newCenterX = Math.max(newWidth / 2, Math.min(1 - newWidth / 2, newCenterX));
      newCenterY = Math.max(newHeight / 2, Math.min(1 - newHeight / 2, newCenterY));
      break;
    case "ne": // 右上角 - 右上角移动，左下角固定
      newWidth = Math.max(MIN_SIZE, Math.min(1 - leftX, resizeStartPos.width + deltaXNormalized));
      newHeight = Math.max(MIN_SIZE, Math.min(bottomY, resizeStartPos.height - deltaYNormalized));
      newCenterX = leftX + newWidth / 2;
      newCenterY = bottomY - newHeight / 2;
      // 确保中心点和边界不超出范围
      newCenterX = Math.max(newWidth / 2, Math.min(1 - newWidth / 2, newCenterX));
      newCenterY = Math.max(newHeight / 2, Math.min(1 - newHeight / 2, newCenterY));
      break;
    case "nw": // 左上角 - 左上角移动，右下角固定
      newWidth = Math.max(MIN_SIZE, Math.min(rightX, resizeStartPos.width - deltaXNormalized));
      newHeight = Math.max(MIN_SIZE, Math.min(bottomY, resizeStartPos.height - deltaYNormalized));
      newCenterX = rightX - newWidth / 2;
      newCenterY = bottomY - newHeight / 2;
      // 确保中心点和边界不超出范围
      newCenterX = Math.max(newWidth / 2, Math.min(1 - newWidth / 2, newCenterX));
      newCenterY = Math.max(newHeight / 2, Math.min(1 - newHeight / 2, newCenterY));
      break;
    case "e": // 右边 - 右边移动，左边固定
      newWidth = Math.max(MIN_SIZE, Math.min(1 - leftX, resizeStartPos.width + deltaXNormalized));
      newHeight = resizeStartPos.height;
      newCenterX = leftX + newWidth / 2;
      newCenterY = resizeStartPos.center_y;
      // 确保中心点和边界不超出范围
      newCenterX = Math.max(newWidth / 2, Math.min(1 - newWidth / 2, newCenterX));
      newCenterY = Math.max(newHeight / 2, Math.min(1 - newHeight / 2, newCenterY));
      break;
    case "w": // 左边 - 左边移动，右边固定
      newWidth = Math.max(MIN_SIZE, Math.min(rightX, resizeStartPos.width - deltaXNormalized));
      newHeight = resizeStartPos.height;
      newCenterX = rightX - newWidth / 2;
      newCenterY = resizeStartPos.center_y;
      // 确保中心点和边界不超出范围
      newCenterX = Math.max(newWidth / 2, Math.min(1 - newWidth / 2, newCenterX));
      newCenterY = Math.max(newHeight / 2, Math.min(1 - newHeight / 2, newCenterY));
      break;
    case "s": // 下边 - 下边移动，上边固定
      newWidth = resizeStartPos.width;
      newHeight = Math.max(MIN_SIZE, Math.min(1 - topY, resizeStartPos.height + deltaYNormalized));
      newCenterX = resizeStartPos.center_x;
      newCenterY = topY + newHeight / 2;
      // 确保中心点和边界不超出范围
      newCenterX = Math.max(newWidth / 2, Math.min(1 - newWidth / 2, newCenterX));
      newCenterY = Math.max(newHeight / 2, Math.min(1 - newHeight / 2, newCenterY));
      break;
    case "n": // 上边 - 上边移动，下边固定
      newWidth = resizeStartPos.width;
      newHeight = Math.max(MIN_SIZE, Math.min(bottomY, resizeStartPos.height - deltaYNormalized));
      newCenterX = resizeStartPos.center_x;
      newCenterY = bottomY - newHeight / 2;
      // 确保中心点和边界不超出范围
      newCenterX = Math.max(newWidth / 2, Math.min(1 - newWidth / 2, newCenterX));
      newCenterY = Math.max(newHeight / 2, Math.min(1 - newHeight / 2, newCenterY));
      break;
  }

  // 检查尺寸或位置是否发生变化
  const changeThreshold = 0.001;
  if (
    Math.abs(newWidth - resizeStartPos.width) > changeThreshold ||
    Math.abs(newHeight - resizeStartPos.height) > changeThreshold ||
    Math.abs(newCenterX - resizeStartPos.center_x) > changeThreshold ||
    Math.abs(newCenterY - resizeStartPos.center_y) > changeThreshold
  ) {
    hasSizeChanged.value = true;
  }

  // 更新标注
  annotation.yolo_format.width = newWidth;
  annotation.yolo_format.height = newHeight;
  annotation.yolo_format.center_x = newCenterX;
  annotation.yolo_format.center_y = newCenterY;

  // 强制更新视图
  annotations.value = [...annotations.value];
};

const handleResizeEnd = (event?: MouseEvent | TouchEvent) => {
  // 保存当前正在调整大小的标注框引用，确保不会因为后续的事件而改变
  const resizedAnnotation = dragAnnotation.value;

  if (event) {
    // 阻止事件冒泡，防止触发标注框的点击事件导致改变选中对象
    event.preventDefault();
    event.stopPropagation();
    event.stopImmediatePropagation();
  }

  // 记录 resize 结束的时间戳，用于防止后续的点击事件改变选中状态
  lastResizeEndTime.value = Date.now();

  isResizing.value = false;

  // 只有在尺寸真正发生变化时才保存
  if (resizedAnnotation && hasSizeChanged.value) {
    resizedAnnotation.isModified = true;
    saveAnnotation(resizedAnnotation);
  }

  resizeHandle.value = "";

  // 移除事件监听
  document.removeEventListener("mousemove", handleResizeMove, { capture: true });
  document.removeEventListener("mouseup", handleResizeEnd, { capture: true });
  document.removeEventListener("touchmove", handleResizeMove, { capture: true });
  document.removeEventListener("touchend", handleResizeEnd, { capture: true });

  // 恢复样式
  document.body.style.userSelect = "";

  // 延迟清理 dragAnnotation，确保不会触发点击事件改变选中状态
  // 使用 nextTick 确保所有事件处理完成后再清理
  nextTick(() => {
    if (isResizing.value === false) {
      // 只有在 resize 确实结束后才清理，防止与其他操作冲突
      dragAnnotation.value = null;
    }
  });
};

// 拖拽创建新标注相关函数
const handleCreateAnnotationStart = (event: MouseEvent) => {
  // 在所有其他任务开始之前检查图片是否已删除
  if (currentImage.value?.deleted === 1 || currentImage.value?.deleted === "1") {
    event.preventDefault();
    event.stopPropagation();
    ElMessage.warning("图片已删除，无法创建标注");
    return;
  }

  // 检查是否点击在现有标注上
  const target = event.target as HTMLElement;
  if (target.closest(".annotation-box") || target.closest(".resize-handle")) {
    return;
  }

  // 允许未标注图片（包括目录图片）创建标注
  // 注释掉原来的限制代码
  // if (currentImage.value?.id === null || currentImage.value?.id === undefined) {
  //   ElMessage.warning("这是未标注图片，无法在此处创建新标注");
  //   return;
  // }

  event.preventDefault();
  event.stopPropagation();

  isCreatingAnnotation.value = true;

  // 获取图片元素引用，始终使用图片元素而不是 event.target
  // 这样可以避免当鼠标移动到标注框边线时，event.target 变成标注框元素导致坐标计算错误
  let imageElement: HTMLImageElement | null = null;

  // 优先使用 ref 获取图片元素
  const detailImageRef = annotationDialogRef.value?.annotationCanvasRef?.value?.detailImage;
  if (detailImageRef?.value) {
    imageElement = detailImageRef.value as HTMLImageElement;
  } else {
    // 备用方案：从 event.target 向上查找图片元素
    let currentTarget = event.target as HTMLElement;
    while (currentTarget && currentTarget.tagName !== "IMG") {
      currentTarget = currentTarget.parentElement as HTMLElement;
      if (!currentTarget || currentTarget.classList.contains("annotation-detail")) {
        break;
      }
    }
    if (currentTarget && currentTarget.tagName === "IMG") {
      imageElement = currentTarget as HTMLImageElement;
    }
  }

  if (!imageElement) {
    isCreatingAnnotation.value = false;
    return;
  }

  // 保存图片元素引用，供后续移动事件使用
  currentImageElementRef.value = imageElement;

  // 计算相对于图片的坐标
  const imageRect = imageElement.getBoundingClientRect();
  const relativeX = event.clientX - imageRect.left;
  const relativeY = event.clientY - imageRect.top;

  // 转换为归一化坐标 (0-1)
  newAnnotationStartPos.x = relativeX / imageRect.width;
  newAnnotationStartPos.y = relativeY / imageRect.height;
  newAnnotationEndPos.x = newAnnotationStartPos.x;
  newAnnotationEndPos.y = newAnnotationStartPos.y;

  newAnnotationPreview.value.show = true;
  updateNewAnnotationPreview();

  // 添加事件监听
  document.addEventListener("mousemove", handleCreateAnnotationMove);
  document.addEventListener("mouseup", handleCreateAnnotationEnd);
  document.body.style.cursor = "crosshair";
  document.body.style.userSelect = "none";
};

const handleCreateAnnotationMove = (event: MouseEvent) => {
  // 在所有其他任务开始之前检查图片是否已删除
  if (currentImage.value?.deleted === 1 || currentImage.value?.deleted === "1") {
    ElMessage.warning("图片已删除，无法创建标注");
    handleCreateAnnotationEnd();
    return;
  }

  if (!isCreatingAnnotation.value || !currentImage.value) return;

  // 使用保存的图片元素引用，避免重复查找
  // 这样可以避免当鼠标移动到标注框边线时，event.target 变成标注框元素导致坐标计算错误
  const imageElement = currentImageElementRef.value;
  if (!imageElement) {
    return;
  }

  const imageRect = imageElement.getBoundingClientRect();
  const relativeX = event.clientX - imageRect.left;
  const relativeY = event.clientY - imageRect.top;

  newAnnotationEndPos.x = Math.max(0, Math.min(1, relativeX / imageRect.width));
  newAnnotationEndPos.y = Math.max(0, Math.min(1, relativeY / imageRect.height));

  updateNewAnnotationPreview();
};

const handleCreateAnnotationEnd = () => {
  // 在所有其他任务开始之前检查图片是否已删除
  if (currentImage.value?.deleted === 1 || currentImage.value?.deleted === "1") {
    ElMessage.warning("图片已删除，无法创建标注");
    // 清理状态
    isCreatingAnnotation.value = false;
    newAnnotationPreview.value.show = false;
    document.removeEventListener("mousemove", handleCreateAnnotationMove);
    document.removeEventListener("mouseup", handleCreateAnnotationEnd);
    document.body.style.cursor = "";
    document.body.style.userSelect = "";
    // 重置拖拽状态
    newAnnotationStartPos.x = 0;
    newAnnotationStartPos.y = 0;
    newAnnotationEndPos.x = 0;
    newAnnotationEndPos.y = 0;
    currentImageElementRef.value = null;
    return;
  }

  if (!isCreatingAnnotation.value) return;

  document.removeEventListener("mousemove", handleCreateAnnotationMove);
  document.removeEventListener("mouseup", handleCreateAnnotationEnd);
  document.body.style.cursor = "";
  document.body.style.userSelect = "";

  newAnnotationPreview.value.show = false;

  // 计算最终框的大小
  const width = Math.abs(newAnnotationEndPos.x - newAnnotationStartPos.x);
  const height = Math.abs(newAnnotationEndPos.y - newAnnotationStartPos.y);

  // 清除图片元素引用
  currentImageElementRef.value = null;

  // 如果框太小，忽略（降低阈值以支持小区域标注，从0.01改为0.001）
  if (width < 0.001 || height < 0.001) {
    isCreatingAnnotation.value = false;
    return;
  }

  // 检查是否已选择标签
  if (selectedLabelForNewAnnotation.value === 0) {
    // 没有选择标签，保持预览框显示并显示标签选择弹框
    isCreatingAnnotation.value = false;
    // 保持预览框显示状态
    newAnnotationPreview.value.show = true;
    labelSelectDialogMode.value = "new"; // 设置为创建新标注模式
    labelSelectDialogVisible.value = true;
    return;
  }

  // 计算中心点
  const centerX = (newAnnotationStartPos.x + newAnnotationEndPos.x) / 2;
  const centerY = (newAnnotationStartPos.y + newAnnotationEndPos.y) / 2;

  // 创建新标注
  createNewAnnotation(centerX, centerY, width, height);

  isCreatingAnnotation.value = false;
};

const updateNewAnnotationPreview = () => {
  if (!newAnnotationPreview.value.show) return;

  const left = Math.min(newAnnotationStartPos.x, newAnnotationEndPos.x);
  const top = Math.min(newAnnotationStartPos.y, newAnnotationEndPos.y);
  const width = Math.abs(newAnnotationEndPos.x - newAnnotationStartPos.x);
  const height = Math.abs(newAnnotationEndPos.y - newAnnotationStartPos.y);

  newAnnotationPreview.value.x = left;
  newAnnotationPreview.value.y = top;
  newAnnotationPreview.value.width = width;
  newAnnotationPreview.value.height = height;
};

const createNewAnnotation = async (centerX: number, centerY: number, width: number, height: number) => {
  // 在所有其他任务开始之前检查图片是否已删除
  if (currentImage.value?.deleted === 1 || currentImage.value?.deleted === "1") {
    ElMessage.warning("图片已删除，无法创建标注");
    return;
  }

  try {
    const newAnnotation = {
      id: Date.now(), // 临时ID
      label_id: selectedLabelForNewAnnotation.value,
      label_name: availableLabels.value.find(label => label.id === selectedLabelForNewAnnotation.value)?.name || "未知标签",
      label_color: availableLabels.value.find(label => label.id === selectedLabelForNewAnnotation.value)?.color || "#409eff",
      yolo_format: {
        label_id: selectedLabelForNewAnnotation.value,
        center_x: centerX,
        center_y: centerY,
        width: width,
        height: height
      },
      isNew: true, // 保持为true，这样saveAnnotation会调用创建接口
      isModified: true, // 保持为true，表示需要保存
      isVisible: true, // 新创建的标注默认为可见
      is_own: true, // 新创建的标注默认是当前用户的标注
      is_auto: false // 手动创建的标注不是系统自动标注
    };

    // 确保新标注的可见性状态保存到全局状态中
    globalAnnotationVisibility.value.set(newAnnotation.id, true);

    // 添加到标注列表
    annotations.value.push(newAnnotation);

    // 自动选中新创建的标注
    selectedAnnotation.value = newAnnotation;
    selectedAnnotationIndex.value = annotations.value.length - 1;

    // 自动保存标注
    await saveAnnotation(newAnnotation);
    // 保存成功提示由saveAnnotation函数内部处理，这里不需要重复提示
  } catch (error) {
    console.error("创建新标注失败:", error);
    // 如果保存失败，从标注列表中移除临时标注
    const failedAnnotation = annotations.value.find(ann => ann.isNew && ann.isModified);
    if (failedAnnotation) {
      const index = annotations.value.findIndex(ann => ann.id === failedAnnotation.id);
      if (index > -1) {
        annotations.value.splice(index, 1);
      }
      // 如果当前选中的是失败的标注，清除选中状态
      if (selectedAnnotation.value?.id === failedAnnotation.id) {
        selectedAnnotation.value = null;
        selectedAnnotationIndex.value = -1;
      }
    }
    // 错误处理由拦截器统一处理，这里不需要额外的错误提示
  }
};

const createNewAnnotationWithLabel = async (centerX: number, centerY: number, width: number, height: number, labelId: number) => {
  // 在所有其他任务开始之前检查图片是否已删除
  if (currentImage.value?.deleted === 1 || currentImage.value?.deleted === "1") {
    ElMessage.warning("图片已删除，无法创建标注");
    return;
  }

  try {
    const newAnnotation = {
      id: Date.now(), // 临时ID
      label_id: labelId,
      label_name: availableLabels.value.find(label => label.id === labelId)?.name || "未知标签",
      label_color: availableLabels.value.find(label => label.id === labelId)?.color || "#409eff",
      yolo_format: {
        label_id: labelId,
        center_x: centerX,
        center_y: centerY,
        width: width,
        height: height
      },
      isNew: true, // 保持为true，这样saveAnnotation会调用创建接口
      isModified: true, // 保持为true，表示需要保存
      isVisible: true, // 新创建的标注默认为可见
      is_own: true, // 新创建的标注默认是当前用户的标注
      is_auto: false // 手动创建的标注不是系统自动标注
    };

    // 确保新标注的可见性状态保存到全局状态中
    globalAnnotationVisibility.value.set(newAnnotation.id, true);

    // 添加到标注列表
    annotations.value.push(newAnnotation);

    // 自动选中新创建的标注
    selectedAnnotation.value = newAnnotation;
    selectedAnnotationIndex.value = annotations.value.length - 1;

    // 自动保存标注
    await saveAnnotation(newAnnotation);
    // 保存成功提示由saveAnnotation函数内部处理，这里不需要重复提示
  } catch (error) {
    console.error("创建新标注失败:", error);
    // 错误处理由拦截器统一处理，这里不需要额外的错误提示
  }
};

// 清理拖拽事件
const cleanupDragEvents = () => {
  document.removeEventListener("mousemove", handleMouseMove, { capture: true });
  document.removeEventListener("mouseup", handleMouseUp, { capture: true });
  document.removeEventListener("touchmove", handleTouchMove);
  document.removeEventListener("touchend", handleTouchEnd);
  document.removeEventListener("mousemove", handleResizeMove);
  document.removeEventListener("mouseup", handleResizeEnd);
  document.removeEventListener("touchmove", handleResizeMove);
  document.removeEventListener("touchend", handleResizeEnd);
  document.removeEventListener("mousemove", handleCreateAnnotationMove);
  document.removeEventListener("mouseup", handleCreateAnnotationEnd);
  document.body.style.cursor = "";
  document.body.style.userSelect = "";
};

const handleUpdateSelectedLabel = (labelId: number) => {
  selectedLabelForNewAnnotation.value = labelId;
};

// 打开标签选择对话框用于修改选中标注的标签
const openLabelSelectDialogForEdit = () => {
  if (!selectedAnnotation.value) {
    ElMessage.warning("请先选择一个标注");
    return;
  }
  labelSelectDialogMode.value = "edit";
  labelSelectDialogVisible.value = true;
};

// 标签选择弹框相关函数
const handleLabelSelectConfirm = (labelId: number) => {
  labelSelectDialogVisible.value = false;

  // 根据模式决定操作
  if (labelSelectDialogMode.value === "edit") {
    // 修改现有标注的标签
    if (!selectedAnnotation.value) {
      ElMessage.warning("未找到选中的标注");
      return;
    }

    // 更新标注的标签信息
    const annotation = selectedAnnotation.value;
    const selectedLabel = availableLabels.value.find(label => label.id === labelId);

    if (!selectedLabel) {
      ElMessage.error("未找到选中的标签");
      return;
    }

    // 更新标注的标签ID和标签信息
    annotation.yolo_format.label_id = labelId;
    annotation.label_name = selectedLabel.name;
    annotation.label_color = selectedLabel.color;

    // 标记为已修改
    annotation.isModified = true;

    // 保存标注
    saveAnnotation(annotation);
  } else {
    // 原有逻辑：创建新标注
    // 如果是在拖拽完成后选择标签，需要继续完成标注创建
    if (newAnnotationStartPos.x !== 0 || newAnnotationStartPos.y !== 0) {
      const width = Math.abs(newAnnotationEndPos.x - newAnnotationStartPos.x);
      const height = Math.abs(newAnnotationEndPos.y - newAnnotationStartPos.y);

      if (width >= 0.001 && height >= 0.001) {
        // 计算中心点
        const centerX = (newAnnotationStartPos.x + newAnnotationEndPos.x) / 2;
        const centerY = (newAnnotationStartPos.y + newAnnotationEndPos.y) / 2;

        // 创建新标注，使用弹框中选择的标签ID
        createNewAnnotationWithLabel(centerX, centerY, width, height, labelId);

        // 隐藏预览框
        newAnnotationPreview.value.show = false;

        // 重置拖拽状态
        newAnnotationStartPos.x = 0;
        newAnnotationStartPos.y = 0;
        newAnnotationEndPos.x = 0;
        newAnnotationEndPos.y = 0;
      }
    }
  }

  // 重置模式
  labelSelectDialogMode.value = "new";
};

const closeLabelSelectDialog = () => {
  labelSelectDialogVisible.value = false;

  // 重置模式
  labelSelectDialogMode.value = "new";

  // 隐藏预览框
  newAnnotationPreview.value.show = false;

  // 重置拖拽状态
  newAnnotationStartPos.x = 0;
  newAnnotationStartPos.y = 0;
  newAnnotationEndPos.x = 0;
  newAnnotationEndPos.y = 0;
};

// 取消选中标签
const handleClearSelectedLabel = () => {
  selectedLabelForNewAnnotation.value = 0;
  // 移除取消选中标签的提示，用户操作已经很明显
};

// 切换标注列表显示/隐藏
const handleToggleAnnotationList = () => {
  showAnnotationList.value = !showAnnotationList.value;

  // 同步更新所有标注的可见性状态
  annotations.value.forEach(annotation => {
    // 检查全局可见性状态中是否有该标注的记录
    const globalVisibility = globalAnnotationVisibility.value.get(annotation.id);

    if (globalVisibility === undefined) {
      // 如果全局状态中没有记录，说明是现有标注，可以更新其可见性
      annotation.isVisible = showAnnotationList.value;
      // 同时更新全局状态
      globalAnnotationVisibility.value.set(annotation.id, showAnnotationList.value);
    } else {
      // 如果全局状态中有记录，需要区分情况：
      // 1. 如果是新标注（isNew为true），保持其可见性不变
      // 2. 如果是现有标注，更新其可见性
      if (!annotation.isNew) {
        annotation.isVisible = showAnnotationList.value;
        // 同时更新全局状态
        globalAnnotationVisibility.value.set(annotation.id, showAnnotationList.value);
      }
    }
  });

  // 强制更新视图
  annotations.value = [...annotations.value];
};

// 处理单个标注可见性切换
const handleToggleAnnotationVisibility = (annotation: any) => {
  const result = toggleAnnotationVisibility(annotation);
  if (result && result.shouldUpdateGlobalState) {
    // 根据标注的可见性状态更新整体显示状态
    showAnnotationList.value = result.hasVisibleAnnotations;
  }
};

// 处理分组可见性切换
const handleToggleGroupVisibility = (group: any) => {
  // 切换分组内所有标注的可见性
  const newVisibility = !group.isVisible;
  group.annotations.forEach((annotation: any) => {
    annotation.isVisible = newVisibility;
    // 保存到全局可见性状态中
    globalAnnotationVisibility.value.set(annotation.id, newVisibility);
  });

  // 保存标签组级别的可见性状态（按label_id）
  globalLabelGroupVisibility.value.set(group.labelId, newVisibility);

  // 强制更新视图
  annotations.value = [...annotations.value];

  // 检查是否需要更新整体显示状态
  const hasVisibleAnnotations = annotations.value.some(ann => ann.isVisible !== false);
  showAnnotationList.value = hasVisibleAnnotations;
};

// 处理标签类（标签分组）可见性切换
const handleToggleLabelGroupVisibility = (labelGroup: any) => {
  // 切换该标签类下所有标注的可见性
  const newVisibility = !labelGroup.isVisible;
  labelGroup.annotations.forEach((annotation: any) => {
    // 基于全局显示状态和标签组状态来决定标注的可见性
    // 如果全局是隐藏的，标签组隐藏也隐藏；如果全局是显示的，标签组隐藏也隐藏
    annotation.isVisible = showAnnotationList.value && newVisibility;
    // 不保存到单个标注的全局可见性状态，只保存标签组级别的状态
    // 这样切换图片时不会干扰全局显示状态
  });

  // 保存标签组级别的可见性状态（按label_id）
  globalLabelGroupVisibility.value.set(labelGroup.labelId, newVisibility);

  // 强制更新视图
  annotations.value = [...annotations.value];

  // 不更新全局显示状态，标签类的显示/隐藏不影响全局开关
};

// 处理模型标签加载
const handleLoadLabelsForModel = (labels: any[] | null) => {
  if (!labels) {
    // 加载所有标签
    fetchLabelList();
  } else {
    // 加载指定模型的标签
    availableLabels.value = labels;
  }
};

// 处理来自标签选择弹框的标签加载
const handleLoadLabelsForModelFromDialog = (labels: any[] | null) => {
  if (!labels) {
    // 加载所有标签
    fetchLabelList();
  } else {
    // 加载指定模型的标签
    availableLabels.value = labels;
  }
};

// 处理标签选择弹框中的模型选择
const handleLabelDialogModelSelect = async (modelId: number | null) => {
  // 更新模型选择状态，这会同步到AnnotationList组件
  selectedModelId.value = modelId;

  // 如果标注详情对话框是打开的且当前有图片，则重新请求标注详情
  if (detailDialogVisible.value && currentImage.value && currentImage.value.id !== null && currentImage.value.id !== undefined) {
    // 创建加载实例
    const loading = ElLoading.service({
      lock: true,
      text: t("annotation.loading"),
      background: "rgba(0, 0, 0, 0.7)"
    });

    try {
      const res = await fetchAnnotationDetail(parseInt(currentImage.value.id.toString()), showAnnotationList.value, modelId);
      loading.close();

      if (res) {
        // 延迟触发标注框重新计算，确保DOM已经更新
        setTimeout(() => {
          if (annotations.value.length > 0) {
            annotations.value = [...annotations.value];
          }
        }, 100);
      }
    } catch (error) {
      loading.close();
      console.error("重新获取标注详情失败:", error);
    }
  }
};

// 系统推理功能
const handleSystemInference = async () => {
  if (!currentImage.value?.id) {
    ElMessage.warning(t("annotation.selectImageFirst") || "请先选择图片");
    return;
  }

  if (!selectedModelId.value) {
    ElMessage.warning(t("annotation.selectModelFirst") || "请先选择模型");
    return;
  }

  const loading = ElLoading.service({
    lock: true,
    text: t("annotation.systemInferenceLoading") || "正在执行系统推理...",
    background: "rgba(0, 0, 0, 0.7)"
  });

  try {
    const response = await systemInferenceApi({
      image_id: parseInt(currentImage.value.id.toString()),
      model_id: selectedModelId.value
    });

    loading.close();

    if (response && typeof response === "object" && response.code === 200) {
      const responseData = (response as any).data?.data || (response as any).data || {};
      const inferenceAnnotations = (responseData as any).annotations || [];

      if (Array.isArray(inferenceAnnotations) && inferenceAnnotations.length > 0) {
        // 将返回的标注数据转换为AnnotationDetail格式，并设置为系统标注
        const formattedAnnotations: any[] = inferenceAnnotations
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
              label_name: ann.label_name || t("annotation.unknownLabel") || "未知标签",
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
          // 调用处理函数，将推理结果添加到系统分类下
          handleAddInferenceAnnotations(formattedAnnotations);
          ElMessage.success(
            t("annotation.systemInferenceSuccess", { count: formattedAnnotations.length }) ||
              `系统推理完成，已添加 ${formattedAnnotations.length} 个标注到系统分类`
          );
        } else {
          ElMessage.warning(t("annotation.systemInferenceFormatError") || "系统推理完成，但返回的标注数据格式不正确");
        }
      } else {
        ElMessage.info(t("annotation.systemInferenceNoResult") || "系统推理完成，未检测到标注");
      }
    } else {
      ElMessage.error(response?.message || t("annotation.systemInferenceFail") || "系统推理失败");
    }
  } catch (error: any) {
    loading.close();
    console.error("系统推理失败:", error);
    ElMessage.error(error?.message || t("annotation.systemInferenceFail") || "系统推理失败，请稍后重试");
  }
};

// 处理系统推理返回的标注
const handleAddInferenceAnnotations = (newAnnotations: any[]) => {
  if (!newAnnotations || newAnnotations.length === 0) {
    console.warn("handleAddInferenceAnnotations: 没有新标注数据");
    return;
  }

  // 为每个新标注设置可见性状态，确保能够正确显示
  newAnnotations.forEach(ann => {
    // 设置可见性状态，默认为可见
    if (ann.isVisible !== false) {
      globalAnnotationVisibility.value.set(ann.id, true);
    } else {
      globalAnnotationVisibility.value.set(ann.id, false);
    }
  });

  // 将推理结果添加到annotations列表中
  annotations.value.push(...newAnnotations);

  // 使用 nextTick 确保 DOM 更新后触发响应式更新
  nextTick(() => {
    // 触发响应式更新，确保标注能够正确显示在画布上
    // 创建新数组引用，确保 Vue 能够检测到变化
    const updatedAnnotations = [...annotations.value];
    annotations.value = updatedAnnotations;
  });
};

// 处理标注列表中的模型选择
const handleAnnotationListModelSelect = async (modelId: number | null) => {
  // 更新模型选择状态，这会同步到LabelSelectDialog组件
  selectedModelId.value = modelId;

  // 如果标注详情对话框是打开的且当前有图片，则重新请求标注详情
  if (detailDialogVisible.value && currentImage.value && currentImage.value.id !== null && currentImage.value.id !== undefined) {
    // 创建加载实例
    const loading = ElLoading.service({
      lock: true,
      text: t("annotation.loading"),
      background: "rgba(0, 0, 0, 0.7)"
    });

    try {
      const res = await fetchAnnotationDetail(parseInt(currentImage.value.id.toString()), showAnnotationList.value, modelId);
      loading.close();

      if (res) {
        // 延迟触发标注框重新计算，确保DOM已经更新
        setTimeout(() => {
          if (annotations.value.length > 0) {
            annotations.value = [...annotations.value];
          }
        }, 100);
      }
    } catch (error) {
      loading.close();
      console.error("重新获取标注详情失败:", error);
    }
  }
};

// 图片导航函数
const navigateImage = async (direction: "prev" | "next") => {
  if (imageList.value.length === 0) return;

  if (direction === "prev") {
    // 向左切换
    if (currentImageIndex.value > 0) {
      // 当前页内还有上一张图片
      currentImageIndex.value--;
      const targetImage = imageList.value[currentImageIndex.value];
      if (targetImage && detailDialogVisible.value) {
        await openDetailDialog(targetImage);
      }
    } else {
      // 当前页第一张图片，尝试切换到上一页
      if (pagination.current > 1) {
        pagination.current--;
        await fetchImageList();
        // 切换到新页面的最后一张图片
        currentImageIndex.value = imageList.value.length - 1;
        const targetImage = imageList.value[currentImageIndex.value];
        if (targetImage && detailDialogVisible.value) {
          await openDetailDialog(targetImage);
        }
        // 提示当前页码
        ElMessage.info(t("annotation.switchedToPage", { page: pagination.current }));
      } else {
        // 已经是第一页第一张图片
        ElMessage.info(t("annotation.alreadyFirstImage"));
      }
    }
  } else {
    // 向右切换
    if (currentImageIndex.value < imageList.value.length - 1) {
      // 当前页内还有下一张图片
      currentImageIndex.value++;
      const targetImage = imageList.value[currentImageIndex.value];
      if (targetImage && detailDialogVisible.value) {
        await openDetailDialog(targetImage);
      }
    } else {
      // 当前页最后一张图片，尝试切换到下一页
      const totalPages = Math.ceil(pagination.total / pagination.pageSize);
      if (pagination.current < totalPages) {
        pagination.current++;
        await fetchImageList();
        // 切换到新页面的第一张图片
        currentImageIndex.value = 0;
        const targetImage = imageList.value[currentImageIndex.value];
        if (targetImage && detailDialogVisible.value) {
          await openDetailDialog(targetImage);
        }
        // 提示当前页码
        ElMessage.info(t("annotation.switchedToPage", { page: pagination.current }));
      } else {
        // 已经是最后一页最后一张图片
        ElMessage.info(t("annotation.alreadyLastImage"));
      }
    }
  }
};

// 标注导航函数
const navigateAnnotation = (direction: "prev" | "next") => {
  if (annotations.value.length === 0) return;

  let newIndex;
  if (selectedAnnotation.value) {
    const currentIndex = annotations.value.findIndex(ann => ann.id === selectedAnnotation.value!.id);
    if (direction === "prev") {
      newIndex = currentIndex > 0 ? currentIndex - 1 : annotations.value.length - 1;
    } else {
      newIndex = currentIndex < annotations.value.length - 1 ? currentIndex + 1 : 0;
    }
  } else {
    // 如果没有选中标注，默认选择第一个
    newIndex = 0;
  }

  selectedAnnotation.value = annotations.value[newIndex];
  selectedAnnotationIndex.value = newIndex;
};

// 导出标注功能 - 打开导出对话框
const handleExportAnnotations = () => {
  exportDialogVisible.value = true;
};

// 关闭导出对话框
const closeExportDialog = () => {
  exportDialogVisible.value = false;
};

// 远程训练功能 - 打开训练对话框
const handleTrainAnnotations = () => {
  trainDialogVisible.value = true;
};

// 关闭训练对话框
const closeTrainDialog = () => {
  trainDialogVisible.value = false;
};

// 导出功能
const handleExportWithLabels = async (modelId: number) => {
  try {
    exportLoading.value = true;
    const loading = ElLoading.service({
      lock: true,
      text: t("annotation.exportLoading"),
      background: "rgba(0, 0, 0, 0.7)"
    });

    // 传递model_id
    const res = await exportAnnotationsApi({ format: "yolo", model_id: modelId });

    // 关闭加载提示
    loading.close();

    // 检查响应结构并处理

    if (res && typeof res === "object") {
      // 处理不同的响应结构
      const responseData = (res as any).data || res;

      // 检查是否有下载地址
      if (responseData.download_url || responseData.file_url || responseData.url) {
        const downloadUrl = responseData.download_url || responseData.file_url || responseData.url;
        const filename = responseData.filename || responseData.file_name || `annotations_${new Date().getTime()}.zip`;

        // 构建完整的下载URL
        let fullDownloadUrl = downloadUrl;

        // 确保以 / 开头的路径可以直接访问
        if (!downloadUrl.startsWith("http")) {
          // 去掉开头的斜杠（如果有的话），因为下载应该直接使用路径
          fullDownloadUrl = downloadUrl;
        }

        // 尝试下载文件
        const link = document.createElement("a");
        link.href = fullDownloadUrl;
        link.download = filename;
        link.style.display = "none";
        link.target = "_blank";
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        ElMessage.success(responseData.message || t("annotation.exportSuccess"));
      } else if (responseData.file_path) {
        // 如果返回的是文件路径，构建完整URL
        const fullUrl = getImageUrl(responseData.file_path);
        const filename = responseData.filename || `annotations_${new Date().getTime()}.zip`;

        // 尝试下载文件
        const link = document.createElement("a");
        link.href = fullUrl;
        link.download = filename;
        link.style.display = "none";
        link.target = "_blank";
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        ElMessage.success(t("annotation.exportSuccess"));
      } else {
        // 没有下载地址，只显示提示信息
        ElMessage.info(responseData.message || t("annotation.exportNoData"));
      }
    } else {
      // 错误处理由拦截器统一处理，这里不需要额外的错误提示
    }
  } catch (error: any) {
    console.error("导出标注内容失败:", error);
    // HTTP拦截器已经处理了错误提示，这里不需要重复提示
    // 只有在非HTTP错误的情况下才显示提示
    if (!error.response) {
      ElMessage.error(t("annotation.exportFail"));
    }
  } finally {
    exportLoading.value = false;
    closeExportDialog();
  }
};

// 标记图片删除状态的通用方法
const markImageDeletedStatus = async (imageId: number, deleted: number) => {
  const loading = ElLoading.service({
    lock: true,
    text: deleted === 1 ? t("annotation.markDeleted") : t("annotation.markNormal"),
    background: "rgba(0, 0, 0, 0.7)"
  });

  try {
    const res = await markImageDeletedApi({
      image_id: imageId,
      deleted: deleted
    });

    loading.close();

    if (res && typeof res === "object") {
      ElMessage.success(deleted === 1 ? t("annotation.markDeletedSuccess") : t("annotation.markNormalSuccess"));

      // 刷新图片列表
      await fetchImageList();

      // 如果当前图片被标记为删除，关闭详情对话框
      if (deleted === 1 && currentImage.value && currentImage.value.id === imageId) {
        closeDetailDialog();
      }
    }
  } catch (error: any) {
    loading.close();
    console.error("标记删除状态失败:", error);
    if (!error.response) {
      ElMessage.error(t("annotation.markDeletedFail"));
    }
  }
};

// 从详情对话框标记删除状态（快捷键r）
const handleMarkImageDeleted = async () => {
  if (!currentImage.value || currentImage.value.id === null || currentImage.value.id === undefined) {
    ElMessage.warning("当前图片无法标记删除状态");
    return;
  }

  const imageId = parseInt(currentImage.value.id.toString());
  // 获取当前图片的删除状态（如果有的话，从列表中找到）
  const currentImageInList = imageList.value.find(item => item.id === imageId);
  // 切换删除状态：如果当前是已删除(1)，则恢复为正常(0)；如果当前是正常(0)或未设置，则标记为已删除(1)
  const newDeletedStatus = currentImageInList && (currentImageInList as any).deleted === 1 ? 0 : 1;

  await markImageDeletedStatus(imageId, newDeletedStatus);
};

// 从表格视图标记删除状态
const handleMarkImageDeletedFromTable = async (item: any) => {
  if (!item || item.id === null || item.id === undefined) {
    ElMessage.warning("当前图片无法标记删除状态");
    return;
  }

  const imageId = parseInt(item.id.toString());
  // 获取当前图片的删除状态
  const currentDeletedStatus = item.deleted === 1 ? 1 : 0;
  // 切换删除状态：如果当前是已删除(1)，则恢复为正常(0)；如果当前是正常(0)或未设置，则标记为已删除(1)
  const newDeletedStatus = currentDeletedStatus === 1 ? 0 : 1;

  await markImageDeletedStatus(imageId, newDeletedStatus);
};

// 处理表格视图的选择变化
const handleTableSelectionChange = (selectedItems: any[]) => {
  // 确保选中的项目包含完整的 deleted 字段
  selectedImages.value = selectedItems.map(item => {
    // 如果 item 已经有 deleted 字段，直接返回
    if (item.deleted !== undefined) {
      return item;
    }
    // 否则从 imageList 中查找完整的数据
    const fullItem = imageList.value.find(img => img.id === item.id);
    return fullItem || item;
  });

  // 同步选中列表，确保数量准确
  syncSelectedImages();
};

// 处理网格视图的选择变化
const handleGridSelectionChange = (selectedItems: any[]) => {
  // 确保选中的项目包含完整的 deleted 字段
  selectedImages.value = selectedItems.map(item => {
    // 如果 item 已经有 deleted 字段，直接返回
    if (item.deleted !== undefined) {
      return item;
    }
    // 否则从 imageList 中查找完整的数据
    const fullItem = imageList.value.find(img => img.id === item.id);
    return fullItem || item;
  });

  // 同步选中列表，确保数量准确
  syncSelectedImages();
};

// 批量删除功能
const handleBatchDelete = async () => {
  // 先同步选中列表，确保数量准确
  syncSelectedImages();

  if (validSelectedCount.value === 0) {
    ElMessage.warning(t("annotation.selectImages"));
    return;
  }

  try {
    await ElMessageBox.confirm(
      t("annotation.confirmBatchDelete", { count: validSelectedCount.value }),
      t("annotation.batchDelete"),
      {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning"
      }
    );

    // 获取有效的选中图片ID（只统计在当前列表中的图片）
    const currentImageIds = new Set(imageList.value.map(img => img.id));
    const imageIds = selectedImages.value
      .filter(item => item && item.id !== null && item.id !== undefined && currentImageIds.has(item.id))
      .map(item => item.id)
      .map(id => parseInt(id.toString()));

    if (imageIds.length === 0) {
      ElMessage.warning(t("annotation.selectImages"));
      return;
    }

    const loading = ElLoading.service({
      lock: true,
      text: t("annotation.markDeleted"),
      background: "rgba(0, 0, 0, 0.7)"
    });

    try {
      const res = await markImageDeletedApi({
        image_ids: imageIds,
        deleted: 1
      });

      loading.close();

      if (res && typeof res === "object") {
        ElMessage.success(t("annotation.batchDeleteSuccess", { count: imageIds.length }));

        // 刷新图片列表
        await fetchImageList();

        // 同步选中列表，过滤掉已删除的图片
        syncSelectedImages();
      }
    } catch (error: any) {
      loading.close();
      console.error("批量删除失败:", error);
      if (!error.response) {
        ElMessage.error(t("annotation.batchDeleteFail"));
      }
    }
  } catch (error: any) {
    // 用户取消操作，不需要处理
    if (error !== "cancel") {
      console.error("批量删除确认失败:", error);
    }
  }
};

// 批量恢复功能
const handleBatchRestore = async () => {
  // 先同步选中列表，确保数量准确
  syncSelectedImages();

  if (validSelectedCount.value === 0) {
    ElMessage.warning(t("annotation.selectImagesToRestore"));
    return;
  }

  try {
    await ElMessageBox.confirm(
      t("annotation.confirmBatchRestore", { count: validSelectedCount.value }),
      t("annotation.batchRestore"),
      {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning"
      }
    );

    // 获取有效的选中图片ID（只统计在当前列表中的图片）
    const currentImageIds = new Set(imageList.value.map(img => img.id));
    const imageIds = selectedImages.value
      .filter(item => item && item.id !== null && item.id !== undefined && currentImageIds.has(item.id))
      .map(item => item.id)
      .map(id => parseInt(id.toString()));

    if (imageIds.length === 0) {
      ElMessage.warning(t("annotation.selectImagesToRestore"));
      return;
    }

    const loading = ElLoading.service({
      lock: true,
      text: t("annotation.markNormal"),
      background: "rgba(0, 0, 0, 0.7)"
    });

    try {
      const res = await markImageDeletedApi({
        image_ids: imageIds,
        deleted: 0
      });

      loading.close();

      if (res && typeof res === "object") {
        ElMessage.success(t("annotation.batchRestoreSuccess", { count: imageIds.length }));

        // 刷新图片列表
        await fetchImageList();

        // 同步选中列表，更新恢复的图片状态
        syncSelectedImages();
      }
    } catch (error: any) {
      loading.close();
      console.error("批量恢复失败:", error);
      if (!error.response) {
        ElMessage.error(t("annotation.batchRestoreFail"));
      }
    }
  } catch (error: any) {
    // 用户取消操作，不需要处理
    if (error !== "cancel") {
      console.error("批量恢复确认失败:", error);
    }
  }
};

// 远程训练功能
const handleTrainWithModel = async (modelId: number) => {
  try {
    trainLoading.value = true;
    const loading = ElLoading.service({
      lock: true,
      text: t("annotation.trainLoading") || "正在启动远程训练...",
      background: "rgba(0, 0, 0, 0.7)"
    });

    // 调用远程训练接口
    const res = await trainInferenceApi({ model_id: modelId });

    // 关闭加载提示
    loading.close();

    // 检查响应结构并处理

    if (res && typeof res === "object") {
      // 处理不同的响应结构
      const responseData = (res as any).data || res;

      // 显示成功提示
      ElMessage.success(responseData.message || t("annotation.trainSuccess") || "远程训练任务已启动");
    } else {
      // 错误处理由拦截器统一处理，这里不需要额外的错误提示
    }
  } catch (error: any) {
    console.error("启动远程训练失败:", error);
    // HTTP拦截器已经处理了错误提示，这里不需要重复提示
    // 只有在非HTTP错误的情况下才显示提示
    if (!error.response) {
      ElMessage.error(t("annotation.trainFail") || "启动远程训练失败");
    }
  } finally {
    trainLoading.value = false;
    closeTrainDialog();
  }
};

// 组件挂载和卸载
onMounted(() => {
  // 直接加载图片列表和标签列表
  fetchImageList();
  fetchLabelList();

  // 添加键盘事件监听器
  removeKeyboardListener = addKeyboardListener({
    detailDialogVisible,
    selectedAnnotation,
    saveAnnotation,
    closeDetailDialog,
    navigateImage,
    navigateAnnotation,
    deleteAnnotation,
    openLabelSelectDialog: openLabelSelectDialogForEdit,
    toggleAnnotationList: handleToggleAnnotationList,
    markImageDeleted: handleMarkImageDeleted,
    systemInference: handleSystemInference
  });
});

onUnmounted(() => {
  // 清理拖拽事件
  cleanupDragEvents();

  // 清理键盘事件监听器
  if (removeKeyboardListener) {
    removeKeyboardListener();
  }
});
</script>

<style lang="scss" scoped>
// 样式已移动到 styles/modules/annotation.scss
</style>
