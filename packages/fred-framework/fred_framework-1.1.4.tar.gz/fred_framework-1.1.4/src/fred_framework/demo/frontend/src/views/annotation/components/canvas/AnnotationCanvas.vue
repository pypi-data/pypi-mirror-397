<template>
  <div class="image-container">
    <div class="image-wrapper" ref="imageWrapper" :style="imageWrapperStyle" @wheel="handleWheel">
      <img
        :src="getImageUrl(currentImage?.file_path)"
        :alt="currentImage?.file_name"
        class="detail-image"
        :class="{ 'image-deleted': isImageDeleted }"
        ref="detailImage"
        @load="handleImageLoad"
        @error="handleImageError"
        @mousedown="handleCreateAnnotationStartWrapper"
      />
      <!-- 拖拽创建新标注的预览框 -->
      <div
        v-if="props.newAnnotationPreview?.show"
        class="new-annotation-preview"
        :style="{
          left: `${(props.newAnnotationPreview?.x || 0) * 100}%`,
          top: `${(props.newAnnotationPreview?.y || 0) * 100}%`,
          width: `${(props.newAnnotationPreview?.width || 0) * 100}%`,
          height: `${(props.newAnnotationPreview?.height || 0) * 100}%`
        }"
      >
        <span
          class="preview-label"
          :style="{
            backgroundColor: availableLabels.find(label => label.id === selectedLabelForNewAnnotation)?.color || '#409eff'
          }"
        >
          {{ availableLabels.find(label => label.id === selectedLabelForNewAnnotation)?.name || "未知标签" }}
        </span>
      </div>
      <!-- 标注框 -->
      <!-- 先渲染未选中的标注框，再渲染选中的标注框，确保选中的标注框在最上层 -->
      <template v-for="annotation in sortedAnnotations" :key="`${annotation.id}-${annotationStyleKey}`">
        <div
          v-show="annotation.isVisible === true"
          class="annotation-box"
          :style="getAnnotationStyle(annotation, selectedAnnotation?.id === annotation.id)"
          :class="{
            active: selectedAnnotation?.id === annotation.id,
            dragging: isDragging && dragAnnotation?.id === annotation.id,
            resizing: isResizing && selectedAnnotation?.id === annotation.id
          }"
          @click.stop="handleAnnotationClick($event, annotation)"
          @mousedown="e => handleAnnotationMouseDownWrapper(e, annotation)"
          @touchstart="e => handleAnnotationMouseDownWrapper(e, annotation)"
        >
          <span
            v-show="props.showLabelName !== false"
            class="annotation-label"
            :style="{ backgroundColor: annotation.label_color || '#409eff' }"
          >
            {{ annotation.label_name }}
          </span>
          <!-- 调整大小的手柄 -->
          <template v-if="selectedAnnotation?.id === annotation.id">
            <div
              v-if="!isImageDeleted"
              class="resize-handle resize-handle-nw"
              data-handle="nw"
              @mousedown.stop="e => handleResizeStartWrapper(e, annotation, 'nw')"
            ></div>
            <div
              v-if="!isImageDeleted"
              class="resize-handle resize-handle-ne"
              data-handle="ne"
              @mousedown.stop="e => handleResizeStartWrapper(e, annotation, 'ne')"
            ></div>
            <div
              v-if="!isImageDeleted"
              class="resize-handle resize-handle-sw"
              data-handle="sw"
              @mousedown.stop="e => handleResizeStartWrapper(e, annotation, 'sw')"
            ></div>
            <div
              v-if="!isImageDeleted"
              class="resize-handle resize-handle-se"
              data-handle="se"
              @mousedown.stop="e => handleResizeStartWrapper(e, annotation, 'se')"
            ></div>
            <div
              v-if="!isImageDeleted"
              class="resize-handle resize-handle-n"
              data-handle="n"
              @mousedown.stop="e => handleResizeStartWrapper(e, annotation, 'n')"
            ></div>
            <div
              v-if="!isImageDeleted"
              class="resize-handle resize-handle-s"
              data-handle="s"
              @mousedown.stop="e => handleResizeStartWrapper(e, annotation, 's')"
            ></div>
            <div
              v-if="!isImageDeleted"
              class="resize-handle resize-handle-w"
              data-handle="w"
              @mousedown.stop="e => handleResizeStartWrapper(e, annotation, 'w')"
            ></div>
            <div
              v-if="!isImageDeleted"
              class="resize-handle resize-handle-e"
              data-handle="e"
              @mousedown.stop="e => handleResizeStartWrapper(e, annotation, 'e')"
            ></div>
          </template>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch, onMounted, onUnmounted, nextTick, computed } from "vue";

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
  deleted?: number; // 删除状态：0-正常，1-已删除
}

interface Props {
  currentImage: ImageInfo | null;
  annotations: AnnotationDetail[];
  selectedAnnotation: AnnotationDetail | null;
  availableLabels: Label[];
  selectedLabelForNewAnnotation: number;
  getImageUrl: (filePath: string) => string;
  imageDimensions: { width: number; height: number };
  imageInfo: ImageInfo | null;
  newAnnotationPreview?: {
    show: boolean;
    x: number;
    y: number;
    width: number;
    height: number;
  };
  lastResizeEndTime?: number;
  showLabelName?: boolean;
}

const props = defineProps<Props>();

// 计算属性：对标注框进行排序，确保选中的标注框最后渲染（在DOM中最后，这样即使z-index相同也会显示在最上层）
const sortedAnnotations = computed(() => {
  if (!props.selectedAnnotation) {
    return props.annotations;
  }

  // 将选中的标注框移到最后
  const selectedId = props.selectedAnnotation.id;
  const unselected = props.annotations.filter(ann => ann.id !== selectedId);
  const selected = props.annotations.filter(ann => ann.id === selectedId);

  return [...unselected, ...selected];
});

const emit = defineEmits<{
  imageLoad: [event: Event];
  imageError: [event: Event];
  selectAnnotation: [annotation: AnnotationDetail];
  createAnnotationStart: [event: MouseEvent];
  annotationMouseDown: [event: MouseEvent | TouchEvent, annotation: AnnotationDetail];
  resizeStart: [event: MouseEvent | TouchEvent, annotation: AnnotationDetail, handle: string];
  imageHeightChange: [height: number];
}>();

// 判断图片是否已删除
const isImageDeleted = computed(() => {
  return props.currentImage?.deleted === 1;
});

// 模板引用
const imageWrapper = ref<HTMLElement>();
const detailImage = ref<HTMLImageElement>();

// 图片缩放相关变量
const imageScale = ref(1);
const imageTranslateX = ref(0);
const imageTranslateY = ref(0);
const minScale = 1; // 最小缩放比例（不能小于原始大小）
const maxScale = 5; // 最大缩放比例
const scaleStep = 0.1; // 每次滚轮的缩放步长

// 计算图片容器的样式
const imageWrapperStyle = computed(() => {
  return {
    transform: `translate(${imageTranslateX.value}px, ${imageTranslateY.value}px) scale(${imageScale.value})`,
    transformOrigin: "center center" // 以中心为变换原点，配合 flexbox 居中对齐
  };
});

// 拖拽相关变量
const isDragging = ref(false);
const dragAnnotation = ref<AnnotationDetail | null>(null);
const dragStartPos = reactive({ x: 0, y: 0 });
const originalPosition = reactive({ x: 0, y: 0, width: 0, height: 0, annotationId: null });
const isResizing = ref(false);
const resizeHandle = ref<string>("");
const resizeStartPos = reactive({ x: 0, y: 0, width: 0, height: 0, center_x: 0, center_y: 0 });

// 拖拽创建新标注相关变量
const isCreatingAnnotation = ref(false);
const newAnnotationStartPos = reactive({ x: 0, y: 0 });
const newAnnotationEndPos = reactive({ x: 0, y: 0 });

// 强制重新计算标注框样式的触发器
const annotationStyleKey = ref(0);

// 窗口缩放处理函数
const handleWindowResize = () => {
  // 当窗口尺寸变化时，强制重新计算标注框样式
  annotationStyleKey.value++;

  // 重新获取图片实际显示高度
  nextTick(() => {
    const imgElement = detailImage.value;
    if (imgElement) {
      const displayHeight = imgElement.clientHeight || imgElement.height || 0;
      if (displayHeight > 0) {
        emit("imageHeightChange", displayHeight);
      }
    }
  });
};

// 监听图片尺寸变化，强制重新计算标注框样式
watch(
  () => [props.imageDimensions.width, props.imageDimensions.height, props.imageInfo?.width, props.imageInfo?.height],
  () => {
    // 当图片尺寸信息更新时，强制重新计算标注框样式
    annotationStyleKey.value++;
  },
  { deep: true }
);

// 监听当前图片变化，强制重新渲染并重置缩放
watch(
  () => props.currentImage?.file_path,
  (newPath, oldPath) => {
    if (newPath !== oldPath) {
      // 强制重新计算标注框样式
      annotationStyleKey.value++;
      // 重置缩放和平移
      imageScale.value = 1;
      imageTranslateX.value = 0;
      imageTranslateY.value = 0;
    }
  }
);

// 监听缩放比例，当缩放回到1时，确保平移也回到0
watch(
  () => imageScale.value,
  newScale => {
    // 使用小的误差范围来处理浮点数精度问题
    if (Math.abs(newScale - 1) < 0.001) {
      // 当缩放回到1时，重置平移为0，确保图片回到中心位置
      imageScale.value = 1; // 确保缩放值精确为1
      imageTranslateX.value = 0;
      imageTranslateY.value = 0;
    }
  }
);

// 处理鼠标滚轮事件，实现 Ctrl + 滚轮缩放
const handleWheel = (event: WheelEvent) => {
  // 只在按住 Ctrl 键时进行缩放
  if (!event.ctrlKey && !event.metaKey) {
    return;
  }

  // 阻止默认行为（页面滚动）
  event.preventDefault();
  event.stopPropagation();

  const wrapper = imageWrapper.value;
  const img = detailImage.value;
  if (!wrapper || !img) {
    return;
  }

  // 获取容器的边界信息
  const containerRect = wrapper.getBoundingClientRect();

  // 计算容器中心位置
  const containerCenterX = containerRect.width / 2;
  const containerCenterY = containerRect.height / 2;

  // 计算鼠标相对于容器的位置（相对于容器左上角）
  const mouseX = event.clientX - containerRect.left;
  const mouseY = event.clientY - containerRect.top;

  // 计算鼠标相对于容器中心的偏移
  const offsetX = mouseX - containerCenterX;
  const offsetY = mouseY - containerCenterY;

  // 计算鼠标在未缩放坐标系中相对于中心的位置
  // 由于 transformOrigin 是 center center，需要先减去当前的平移，再除以缩放
  const scaleBefore = imageScale.value;
  const pointX = (offsetX - imageTranslateX.value) / scaleBefore;
  const pointY = (offsetY - imageTranslateY.value) / scaleBefore;

  // 计算新的缩放比例
  const delta = event.deltaY > 0 ? -scaleStep : scaleStep;
  const newScale = Math.max(minScale, Math.min(maxScale, imageScale.value + delta));

  // 如果缩放比例没有变化，直接返回
  if (newScale === imageScale.value) {
    return;
  }

  // 计算缩放后的平移量，使鼠标指向的点位置保持不变
  // 缩放后，鼠标指向的点应该还在鼠标位置（相对于容器中心）
  const scaleAfter = newScale;
  let newTranslateX = offsetX - pointX * scaleAfter;
  let newTranslateY = offsetY - pointY * scaleAfter;

  // 如果缩放回到1（原始大小）或接近1，重置平移为0，确保图片回到中心位置
  // 使用小的误差范围来处理浮点数精度问题
  if (Math.abs(newScale - 1) < 0.001) {
    newTranslateX = 0;
    newTranslateY = 0;
  }

  // 更新缩放和平移值
  imageScale.value = newScale;
  imageTranslateX.value = newTranslateX;
  imageTranslateY.value = newTranslateY;

  // 强制重新计算标注框样式
  annotationStyleKey.value++;
};

// 图片加载事件处理
const handleImageLoad = (event: Event) => {
  emit("imageLoad", event);

  // 获取图片实际显示高度，用于限制右侧列表高度
  nextTick(() => {
    const imgElement = detailImage.value;
    if (imgElement) {
      const displayHeight = imgElement.clientHeight || imgElement.height || 0;
      emit("imageHeightChange", displayHeight);
    }
  });
};

const handleImageError = (event: Event) => {
  emit("imageError", event);
};

// 处理标注框点击，支持重叠标注框的循环切换
const handleAnnotationClick = (event: MouseEvent | TouchEvent, clickedAnnotation: AnnotationDetail) => {
  const imgElement = detailImage.value;
  if (!imgElement) return;

  // 如果正在调整大小，忽略点击事件，避免改变选中对象
  if (isResizing.value) {
    return;
  }

  // 如果 resize 刚结束（300ms 内），忽略点击事件，防止 resize 结束后的点击改变选中状态
  if (props.lastResizeEndTime && Date.now() - props.lastResizeEndTime < 300) {
    return;
  }

  // 获取点击坐标（相对于图片，考虑缩放和平移）
  const wrapper = imageWrapper.value;
  if (!wrapper) return;

  const wrapperRect = wrapper.getBoundingClientRect();
  const containerCenterX = wrapperRect.width / 2;
  const containerCenterY = wrapperRect.height / 2;
  let clickX: number, clickY: number;

  if (event instanceof MouseEvent) {
    // 计算相对于容器中心的位置
    const relativeX = event.clientX - wrapperRect.left;
    const relativeY = event.clientY - wrapperRect.top;
    const offsetX = relativeX - containerCenterX;
    const offsetY = relativeY - containerCenterY;
    // 考虑缩放和平移，转换为相对于图片原始显示尺寸的位置
    // 由于 transformOrigin 是 center center，需要先减去平移，再除以缩放，最后加上中心偏移
    clickX = (offsetX - imageTranslateX.value) / imageScale.value + containerCenterX;
    clickY = (offsetY - imageTranslateY.value) / imageScale.value + containerCenterY;
  } else {
    // TouchEvent
    const touch = event.touches[0] || event.changedTouches[0];
    const relativeX = touch.clientX - wrapperRect.left;
    const relativeY = touch.clientY - wrapperRect.top;
    const offsetX = relativeX - containerCenterX;
    const offsetY = relativeY - containerCenterY;
    clickX = (offsetX - imageTranslateX.value) / imageScale.value + containerCenterX;
    clickY = (offsetY - imageTranslateY.value) / imageScale.value + containerCenterY;
  }

  // 获取图片的原始尺寸和实际显示尺寸
  const naturalWidth = props.imageInfo?.width || imgElement.naturalWidth || 0;
  const naturalHeight = props.imageInfo?.height || imgElement.naturalHeight || 0;
  const displayWidth = imgElement.clientWidth || imgElement.width || naturalWidth;
  const displayHeight = imgElement.clientHeight || imgElement.height || naturalHeight;

  if (naturalWidth === 0 || naturalHeight === 0 || displayWidth === 0 || displayHeight === 0) {
    // 如果图片尺寸不可用，直接选中点击的标注框
    emit("selectAnnotation", clickedAnnotation);
    return;
  }

  // 计算缩放比例
  const scaleX = displayWidth / naturalWidth;
  const scaleY = displayHeight / naturalHeight;

  // 找出所有包含点击位置的标注框
  const overlappingAnnotations: Array<{ annotation: AnnotationDetail; area: number }> = [];

  props.annotations.forEach(annotation => {
    if (!annotation.yolo_format || annotation.isVisible === false) return;

    const yolo = annotation.yolo_format;

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

    // 检查点击位置是否在标注框内
    if (
      clickX >= clampedLeft &&
      clickX <= clampedLeft + clampedWidth &&
      clickY >= clampedTop &&
      clickY <= clampedTop + clampedHeight
    ) {
      // 计算标注框的面积，用于排序（较小的标注框通常是更具体的）
      const area = clampedWidth * clampedHeight;
      overlappingAnnotations.push({ annotation, area });
    }
  });

  if (overlappingAnnotations.length === 0) {
    // 没有找到重叠的标注框，选中点击的标注框
    emit("selectAnnotation", clickedAnnotation);
    return;
  }

  // 按照面积从小到大排序（优先选择较小的标注框）
  overlappingAnnotations.sort((a, b) => a.area - b.area);

  // 提取标注框数组
  const overlappingList = overlappingAnnotations.map(item => item.annotation);

  // 获取当前选中的标注框
  const currentSelected = props.selectedAnnotation;

  // 在同一位置点击时，总是选中最小的（最里面的）标注框，而不是循环切换
  // 这样可以避免在同一位置不停点击时，选中对象不断改变的问题
  const smallestAnnotation = overlappingList[0]; // 已经按面积从小到大排序，第一个就是最小的

  if (!currentSelected) {
    // 如果没有选中的标注框，选择最小的（第一个）
    emit("selectAnnotation", smallestAnnotation);
    return;
  }

  // 查找当前选中标注框在重叠列表中的位置
  const currentIndex = overlappingList.findIndex(ann => ann.id === currentSelected.id);

  if (currentIndex === -1) {
    // 当前选中的标注框不在重叠列表中，选择最小的（第一个）
    emit("selectAnnotation", smallestAnnotation);
    return;
  }

  // 如果当前选中的就是最小的，保持不变；否则，选中最小的
  // 这样在同一位置点击时，总是选中最里面的标注框
  if (currentIndex === 0) {
    // 已经选中最小的，保持选中状态不变
    return;
  } else {
    // 选中最小的标注框
    emit("selectAnnotation", smallestAnnotation);
    return;
  }
};

// 标注框样式计算
const getAnnotationStyle = (annotation: AnnotationDetail, isSelected: boolean = false) => {
  if (!annotation?.yolo_format) {
    console.warn("Annotation missing yolo_format:", {
      annotationId: annotation?.id,
      hasYoloFormat: !!annotation?.yolo_format,
      yoloFormat: annotation?.yolo_format
    });
    return {};
  }

  const imgElement = detailImage.value;
  if (!imgElement) {
    console.warn("Image element not found");
    return {};
  }

  // 获取图片的原始尺寸和实际显示尺寸
  const naturalWidth = props.imageInfo?.width || imgElement.naturalWidth || 0;
  const naturalHeight = props.imageInfo?.height || imgElement.naturalHeight || 0;
  const displayWidth = imgElement.clientWidth || imgElement.width || naturalWidth;
  const displayHeight = imgElement.clientHeight || imgElement.height || naturalHeight;

  // 如果图片尺寸信息不可用，返回一个占位样式，避免标注框完全不显示
  if (naturalWidth === 0 || naturalHeight === 0) {
    console.warn("Image dimensions not available, using fallback style");
    // 返回一个基于YOLO坐标的临时样式，等图片加载完成后再重新计算
    const yolo = annotation.yolo_format;
    return {
      position: "absolute",
      left: `${yolo.center_x * 100}%`,
      top: `${yolo.center_y * 100}%`,
      width: `${yolo.width * 100}%`,
      height: `${yolo.height * 100}%`,
      border: `2px solid ${annotation.label_color || "#ff0000"}`,
      backgroundColor: "transparent",
      zIndex: isSelected ? 25 : 10,
      pointerEvents: "auto",
      transform: "translate(-50%, -50%)", // 使用transform来居中
      opacity: 0.7 // 降低透明度表示这是临时样式
    };
  }

  // 计算缩放比例
  const scaleX = displayWidth / naturalWidth;
  const scaleY = displayHeight / naturalHeight;

  const yolo = annotation.yolo_format;

  // 根据缩放比例计算实际显示位置的像素坐标
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

  return {
    position: "absolute",
    left: `${clampedLeft}px`,
    top: `${clampedTop}px`,
    width: `${width}px`,
    height: `${height}px`,
    border: `2px solid ${annotation.label_color || "#ff0000"}`,
    backgroundColor: "transparent",
    zIndex: isSelected ? 25 : 10, // 选中的标注框使用更高的 z-index，确保缩放手柄不被遮挡
    pointerEvents: "auto"
  };
};

// 拖拽相关函数
const handleAnnotationMouseDownWrapper = (event: MouseEvent | TouchEvent, annotation: AnnotationDetail) => {
  // 如果图片已删除，阻止拖拽
  if (isImageDeleted.value) {
    event.preventDefault();
    event.stopPropagation();
    return;
  }
  handleAnnotationMouseDown(event, annotation);
};

const handleAnnotationMouseDown = (event: MouseEvent | TouchEvent, annotation: AnnotationDetail) => {
  emit("annotationMouseDown", event, annotation);
};

const handleResizeStartWrapper = (event: MouseEvent | TouchEvent, annotation: AnnotationDetail, handle: string) => {
  // 如果图片已删除，阻止调整大小
  if (isImageDeleted.value) {
    event.preventDefault();
    event.stopPropagation();
    return;
  }
  handleResizeStart(event, annotation, handle);
};

const handleResizeStart = (event: MouseEvent | TouchEvent, annotation: AnnotationDetail, handle: string) => {
  emit("resizeStart", event, annotation, handle);
};

const handleCreateAnnotationStartWrapper = (event: MouseEvent) => {
  // 如果图片已删除，不处理事件
  if (isImageDeleted.value) {
    event.preventDefault();
    event.stopPropagation();
    return;
  }
  emit("createAnnotationStart", event);
};

// 组件挂载和卸载
onMounted(() => {
  // 添加窗口缩放事件监听
  window.addEventListener("resize", handleWindowResize);
});

onUnmounted(() => {
  // 移除窗口缩放事件监听
  window.removeEventListener("resize", handleWindowResize);
});

// 暴露方法给父组件
defineExpose({
  imageWrapper,
  detailImage,
  isDragging,
  dragAnnotation,
  dragStartPos,
  originalPosition,
  isResizing,
  resizeHandle,
  resizeStartPos,
  isCreatingAnnotation,
  newAnnotationStartPos,
  newAnnotationEndPos,
  imageScale,
  imageTranslateX,
  imageTranslateY
});
</script>

<style lang="scss" scoped>
.image-container {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #f5f5f5;
  position: relative;
  overflow: auto; // 允许滚动查看缩放后的内容
  min-height: 0;
  min-width: 0;

  .image-wrapper {
    position: relative;
    max-width: 100%;
    max-height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    overflow: visible; // 允许缩放时超出容器
    will-change: transform; // 优化性能

    .detail-image {
      max-width: 100%;
      max-height: 100%;
      width: auto;
      height: auto;
      object-fit: contain;
      user-select: none;
      cursor: crosshair;

      &.image-deleted {
        cursor: not-allowed;
        opacity: 0.6;
      }
    }

    .new-annotation-preview {
      position: absolute;
      border: 2px dashed #409eff;
      background: rgba(64, 158, 255, 0.1);
      pointer-events: none;
      z-index: 5;

      .preview-label {
        position: absolute;
        top: -20px;
        left: 0;
        padding: 2px 6px;
        font-size: 12px;
        color: white;
        border-radius: 2px;
        white-space: nowrap;
      }
    }

    .annotation-box {
      position: absolute;
      border: 2px solid #ff0000;
      background: transparent;
      cursor: move;
      user-select: none;
      // 默认 z-index，选中时会通过内联样式设置为 25

      &.active {
        border-color: #409eff;
        box-shadow: 0 0 0 1px #409eff;
      }

      &.dragging {
        opacity: 0.8;
        z-index: 26 !important; // 拖拽时使用更高的 z-index
      }

      &.resizing {
        z-index: 26 !important; // 缩放时使用更高的 z-index

        // 缩放时，缩放手柄区域应该可以穿透其他标注框接收点击
        .resize-handle {
          pointer-events: auto !important;
        }
      }

      .annotation-label {
        position: absolute;
        top: -20px;
        left: 0;
        padding: 2px 6px;
        font-size: 12px;
        color: white;
        border-radius: 2px;
        white-space: nowrap;
        max-width: 100px;
        overflow: hidden;
        text-overflow: ellipsis;
      }

      .resize-handle {
        position: absolute;
        width: 6px;
        height: 6px;
        background: #f971f7;
        border: 1px solid white;
        border-radius: 50%;
        cursor: pointer;
        z-index: 30; // 缩放手柄的 z-index 应该比选中的标注框更高，确保始终可点击
        pointer-events: auto; // 确保缩放手柄可以接收点击事件
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
        transition:
          transform 0.1s ease,
          background-color 0.1s ease;

        // 扩大点击区域，在视觉大小周围增加 6px 的点击区域
        // 这样即使标注框重叠，也更容易点击到缩放手柄
        &::before {
          content: "";
          position: absolute;
          top: -6px;
          left: -6px;
          right: -6px;
          bottom: -6px;
          pointer-events: auto;
        }

        &:hover {
          transform: scale(1.2);
          background-color: #66b1ff;
        }

        &:active {
          transform: scale(1.1);
          background-color: #337ecc;
        }

        &.resize-handle-nw {
          top: -2px;
          left: -2px;
          cursor: nw-resize;
        }

        &.resize-handle-ne {
          top: -2px;
          right: -2px;
          cursor: ne-resize;
        }

        &.resize-handle-sw {
          bottom: -2px;
          left: -2px;
          cursor: sw-resize;
        }

        &.resize-handle-se {
          bottom: -2px;
          right: -2px;
          cursor: se-resize;
        }

        &.resize-handle-n {
          top: -2px;
          left: 50%;
          transform: translateX(-50%);
          cursor: ns-resize;
        }

        &.resize-handle-s {
          bottom: -2px;
          left: 50%;
          transform: translateX(-50%);
          cursor: ns-resize;
        }

        &.resize-handle-w {
          top: 50%;
          left: -2px;
          transform: translateY(-50%);
          cursor: ew-resize;
        }

        &.resize-handle-e {
          top: 50%;
          right: -2px;
          transform: translateY(-50%);
          cursor: ew-resize;
        }
      }
    }
  }
}
</style>
