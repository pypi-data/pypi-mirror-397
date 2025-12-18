// 移除未使用的导入
import { Ref } from "vue";

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

export function useKeyboardNavigation() {
  // 键盘事件处理
  const handleGlobalKeyDown = (
    event: KeyboardEvent,
    options: {
      detailDialogVisible: boolean;
      selectedAnnotation: AnnotationDetail | null;
      saveAnnotation: (annotation: AnnotationDetail) => void;
      closeDetailDialog: () => void;
      navigateImage: (direction: "prev" | "next") => void;
      navigateAnnotation: (direction: "prev" | "next") => void;
      deleteAnnotation: (annotation: AnnotationDetail) => void;
      openLabelSelectDialog: () => void;
      toggleAnnotationList: () => void;
      markImageDeleted: () => void;
      systemInference: () => void;
    }
  ) => {
    // 只在详情对话框打开时响应
    if (!options.detailDialogVisible) return;

    switch (event.key) {
      case "Escape":
        options.closeDetailDialog();
        break;
      case "a":
      case "A":
        event.preventDefault();
        options.navigateImage("prev");
        break;
      case "d":
      case "D":
        event.preventDefault();
        options.navigateImage("next");
        break;
      case "c":
      case "C":
        event.preventDefault();
        if (options.selectedAnnotation) {
          options.deleteAnnotation(options.selectedAnnotation);
        }
        break;
      case "w":
      case "W":
        event.preventDefault();
        options.navigateAnnotation("prev");
        break;
      case "s":
      case "S":
        event.preventDefault();
        options.navigateAnnotation("next");
        break;
      case "x":
      case "X":
        event.preventDefault();
        if (options.selectedAnnotation) {
          options.openLabelSelectDialog();
        }
        break;
      case "q":
      case "Q":
        event.preventDefault();
        options.toggleAnnotationList();
        break;
      case "r":
      case "R":
        event.preventDefault();
        options.markImageDeleted();
        break;
      case "f":
      case "F":
        event.preventDefault();
        options.systemInference();
        break;
    }
  };

  // 添加键盘事件监听
  const addKeyboardListener = (options: {
    detailDialogVisible: Ref<boolean>;
    selectedAnnotation: Ref<AnnotationDetail | null>;
    saveAnnotation: (annotation: AnnotationDetail) => void;
    closeDetailDialog: () => void;
    navigateImage: (direction: "prev" | "next") => void;
    navigateAnnotation: (direction: "prev" | "next") => void;
    deleteAnnotation: (annotation: AnnotationDetail) => void;
    openLabelSelectDialog: () => void;
    toggleAnnotationList: () => void;
    markImageDeleted: () => void;
    systemInference: () => void;
  }) => {
    const handler = (event: KeyboardEvent) =>
      handleGlobalKeyDown(event, {
        detailDialogVisible: options.detailDialogVisible.value,
        selectedAnnotation: options.selectedAnnotation.value,
        saveAnnotation: options.saveAnnotation,
        closeDetailDialog: options.closeDetailDialog,
        navigateImage: options.navigateImage,
        navigateAnnotation: options.navigateAnnotation,
        deleteAnnotation: options.deleteAnnotation,
        openLabelSelectDialog: options.openLabelSelectDialog,
        toggleAnnotationList: options.toggleAnnotationList,
        markImageDeleted: options.markImageDeleted,
        systemInference: options.systemInference
      });
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  };

  return {
    handleGlobalKeyDown,
    addKeyboardListener
  };
}
