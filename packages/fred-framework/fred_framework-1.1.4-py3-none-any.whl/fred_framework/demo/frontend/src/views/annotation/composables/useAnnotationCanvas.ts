import { ref, reactive, onUnmounted } from "vue";

export interface AnnotationDetail {
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

export interface Label {
  id: number;
  name: string;
  color: string;
}

export function useAnnotationCanvas() {
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
  const newAnnotationPreview = ref({
    show: false,
    x: 0,
    y: 0,
    width: 0,
    height: 0
  });

  // 拖拽相关函数
  const handleAnnotationMouseDown = (event: MouseEvent | TouchEvent, annotation: AnnotationDetail) => {
    event.preventDefault();
    event.stopPropagation();

    if (!annotation || !annotation.yolo_format) return;

    isDragging.value = true;
    dragAnnotation.value = annotation;

    // 记录鼠标起始位置
    const clientX = "touches" in event ? event.touches[0].clientX : event.clientX;
    const clientY = "touches" in event ? event.touches[0].clientY : event.clientY;

    dragStartPos.x = clientX;
    dragStartPos.y = clientY;

    // 记录原始位置和尺寸
    originalPosition.x = annotation.yolo_format.center_x;
    originalPosition.y = annotation.yolo_format.center_y;
    originalPosition.width = annotation.yolo_format.width;
    originalPosition.height = annotation.yolo_format.height;
    originalPosition.annotationId = annotation.id;

    // 添加全局鼠标事件监听，使用捕获阶段提高响应性
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
    if (!isDragging.value || !dragAnnotation.value) return;

    // 计算鼠标移动距离
    const deltaX = event.clientX - dragStartPos.x;
    const deltaY = event.clientY - dragStartPos.y;

    // 使用更小的移动阈值提高灵敏度
    const moveThreshold = 2; // 像素阈值从默认的10降低到2
    if (Math.abs(deltaX) < moveThreshold && Math.abs(deltaY) < moveThreshold) {
      return; // 忽略微小移动
    }

    // 这里需要图片尺寸信息，由父组件传入
    // 将像素移动转换为YOLO坐标的逻辑应该在父组件中处理
  };

  const handleMouseUp = () => {
    if (!isDragging.value || !dragAnnotation.value) return;

    // 移除事件监听
    document.removeEventListener("mousemove", handleMouseMove);
    document.removeEventListener("mouseup", handleMouseUp);

    // 恢复样式
    document.body.style.cursor = "";
    document.body.style.userSelect = "";

    // 停止拖拽状态，但不调用API
    isDragging.value = false;

    // 标记标注为已修改状态
    if (dragAnnotation.value) {
      dragAnnotation.value.isModified = true;
    }
    dragAnnotation.value = null;
  };

  const handleTouchMove = (event: TouchEvent) => {
    event.preventDefault();
    if (!isDragging.value || !dragAnnotation.value) return;

    const touch = event.touches[0];
    if (!touch) return;

    // 计算触摸移动距离
    const deltaX = touch.clientX - dragStartPos.x;
    const deltaY = touch.clientY - dragStartPos.y;

    // 使用更小的移动阈值提高灵敏度
    const moveThreshold = 3; // 触摸阈值稍大一些，避免误触
    if (Math.abs(deltaX) < moveThreshold && Math.abs(deltaY) < moveThreshold) {
      return; // 忽略微小移动
    }

    // 这里需要图片尺寸信息，由父组件传入
  };

  const handleTouchEnd = () => {
    handleMouseUp();
    document.removeEventListener("touchmove", handleTouchMove);
    document.removeEventListener("touchend", handleTouchEnd);
  };

  // 开始调整大小
  const handleResizeStart = (event: MouseEvent | TouchEvent, annotation: AnnotationDetail, handle: string) => {
    event.preventDefault();
    event.stopPropagation();

    isResizing.value = true;
    resizeHandle.value = handle;
    dragAnnotation.value = annotation;

    const clientX = "touches" in event ? event.touches[0].clientX : event.clientX;
    const clientY = "touches" in event ? event.touches[0].clientY : event.clientY;

    resizeStartPos.x = clientX;
    resizeStartPos.y = clientY;
    resizeStartPos.width = annotation.yolo_format.width;
    resizeStartPos.height = annotation.yolo_format.height;
    resizeStartPos.center_x = annotation.yolo_format.center_x;
    resizeStartPos.center_y = annotation.yolo_format.center_y;

    // 添加事件监听
    document.addEventListener("mousemove", handleResizeMove);
    document.addEventListener("mouseup", handleResizeEnd);
    document.addEventListener("touchmove", handleResizeMove);
    document.addEventListener("touchend", handleResizeEnd);

    // 阻止文本选择
    document.body.style.userSelect = "none";
  };

  // 调整大小移动 - 以左上角为固定点
  const handleResizeMove = () => {
    if (!isResizing.value || !dragAnnotation.value) return;

    // 获取鼠标/触摸位置（暂时未使用，等待父组件实现具体逻辑）
    // const clientX = "touches" in event ? event.touches[0].clientX : event.clientX;
    // const clientY = "touches" in event ? event.touches[0].clientY : event.clientY;

    // 计算调整大小的偏移量（暂时未使用，等待父组件实现具体逻辑）
    // const deltaX = clientX - resizeStartPos.x;
    // const deltaY = clientY - resizeStartPos.y;

    // 这里需要图片尺寸信息，由父组件传入
    // 调整大小的逻辑应该在父组件中处理
  };

  // 调整大小结束
  const handleResizeEnd = () => {
    isResizing.value = false;
    resizeHandle.value = "";
    dragAnnotation.value = null;

    // 移除事件监听
    document.removeEventListener("mousemove", handleResizeMove);
    document.removeEventListener("mouseup", handleResizeEnd);
    document.removeEventListener("touchmove", handleResizeMove);
    document.removeEventListener("touchend", handleResizeEnd);

    // 恢复样式
    document.body.style.userSelect = "";
  };

  // 拖拽创建新标注相关函数
  const handleCreateAnnotationStart = (event: MouseEvent) => {
    // 检查是否点击在现有标注上
    const target = event.target as HTMLElement;
    if (target.closest(".annotation-box") || target.closest(".resize-handle")) {
      return; // 如果点击在现有标注上，不创建新标注
    }

    event.preventDefault();
    event.stopPropagation();

    isCreatingAnnotation.value = true;

    // 这里需要图片元素信息，由父组件传入
    // 创建新标注的逻辑应该在父组件中处理
  };

  const handleCreateAnnotationMove = (event: MouseEvent) => {
    if (!isCreatingAnnotation.value) return;

    // 这里需要图片元素信息，由父组件传入
    // 暂时忽略event参数，避免未使用警告
    void event;
  };

  const handleCreateAnnotationEnd = () => {
    if (!isCreatingAnnotation.value) return;

    document.removeEventListener("mousemove", handleCreateAnnotationMove);
    document.removeEventListener("mouseup", handleCreateAnnotationEnd);
    document.body.style.cursor = "";
    document.body.style.userSelect = "";

    newAnnotationPreview.value.show = false;

    // 计算最终框的大小
    const width = Math.abs(newAnnotationEndPos.x - newAnnotationStartPos.x);
    const height = Math.abs(newAnnotationEndPos.y - newAnnotationStartPos.y);

    // 如果框太小，忽略（降低阈值以支持小区域标注，从0.01改为0.001）
    if (width < 0.001 || height < 0.001) {
      isCreatingAnnotation.value = false;
      return;
    }

    // 计算中心点（暂时注释掉，等待父组件实现）
    // const centerX = (newAnnotationStartPos.x + newAnnotationEndPos.x) / 2;
    // const centerY = (newAnnotationStartPos.y + newAnnotationEndPos.y) / 2;

    // 创建新标注的逻辑应该在父组件中处理
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

  // 组件卸载时清理事件
  onUnmounted(() => {
    cleanupDragEvents();
  });

  return {
    // 状态
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
    newAnnotationPreview,

    // 方法
    handleAnnotationMouseDown,
    handleResizeStart,
    handleCreateAnnotationStart,
    updateNewAnnotationPreview,
    cleanupDragEvents
  };
}
