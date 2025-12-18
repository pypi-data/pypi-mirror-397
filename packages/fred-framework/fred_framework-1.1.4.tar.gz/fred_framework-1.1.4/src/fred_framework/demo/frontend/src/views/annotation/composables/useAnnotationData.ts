import { ref, reactive } from "vue";
import { ElMessage, ElLoading } from "element-plus";
import { getAnnotationListApi, getAnnotationDetailApi, updateAnnotationApi, createAnnotationApi } from "@/api/modules/annotation";
import { getAllLabelsApi } from "@/api/modules/label";
import { deleteAnnotationApi } from "@/api/modules/annotation";

export interface AnnotationItem {
  id: number | null;
  file_name: string;
  file_path: string;
  project_name: string;
  creator_name: string;
  created_at: string;
  annotation_count: number;
  width?: number;
  height?: number;
  deleted?: number; // 删除状态：0-正常，1-已删除
}

export interface AnnotationDetail {
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
  isVisible?: boolean; // 单个标注的可见性状态
  is_own?: boolean; // 是否是当前用户的标注
  is_auto?: boolean; // 是否是系统自动标注
}

export interface Label {
  id: number;
  name: string;
  color: string;
}

export interface SceneOption {
  id: number;
  name: string;
  image_count?: number;
}

export interface SearchForm {
  status: number | null;
  material_id: number | null;
  deleted: number | null;
  annotation_updated_start: string | null;
  annotation_updated_end: string | null;
}

export function useAnnotationData() {
  // 状态变量
  const imageList = ref<AnnotationItem[]>([]);
  // 删除标注的请求状态，防止重复请求
  const deletingAnnotationIds = ref<Set<number>>(new Set());
  const annotations = ref<AnnotationDetail[]>([]);
  const availableLabels = ref<Label[]>([]);
  const currentImage = ref<any>(null);
  const selectedAnnotation = ref<AnnotationDetail | null>(null);
  const imageInfo = ref<any>(null);
  const imageDimensions = reactive({
    width: 0,
    height: 0
  });

  const pagination = reactive({
    current: 1,
    pageSize: 48,
    total: 0
  });

  const searchForm = reactive<SearchForm>({
    status: null,
    material_id: null,
    deleted: 0, // 默认只显示未删除的图片（正常状态）
    annotation_updated_start: null,
    annotation_updated_end: null
  });

  // 全局标注可见性状态管理
  // 使用 Map 来存储每个标注ID的可见性状态
  const globalAnnotationVisibility = ref<Map<number, boolean>>(new Map());

  // 标签组级别的可见性状态管理（按label_id）
  const globalLabelGroupVisibility = ref<Map<number, boolean>>(new Map());

  // 获取完整图片URL的函数
  const getImageUrl = (filePath: string) => {
    if (!filePath) {
      console.warn("图片路径为空");
      return "";
    }

    // 如果已经是完整URL，直接返回
    if (filePath.startsWith("http://") || filePath.startsWith("https://")) {
      return filePath;
    }

    // 处理相对路径
    let path = filePath.replace(/\\/g, "/");

    // 确保路径格式正确，移除开头的斜杠避免重复
    path = path.replace(/^\/+/g, "");

    // 使用完整的API地址或相对路径
    const baseUrl = import.meta.env.VITE_API_URL || "/api";

    // 构建完整的图片URL
    let fullUrl;
    if (baseUrl.startsWith("http")) {
      // 如果baseUrl是绝对地址
      fullUrl = `${baseUrl.replace(/\/$/, "")}/${path}`;
    } else {
      // 如果baseUrl是相对路径（如/api）
      fullUrl = `${baseUrl.replace(/\/$/, "")}/${path}`;
    }

    // 确保URL格式正确
    fullUrl = fullUrl.replace(/([^:])\/\/+/g, "$1/");

    return fullUrl;
  };

  // 获取图片列表
  const fetchImageList = async () => {
    try {
      // 统一使用图片列表接口
      const params: any = {
        pageNum: pagination.current,
        pageSize: pagination.pageSize
      };

      // 只有当status不为null时才添加到参数中
      if (searchForm.status !== null) {
        params.status = searchForm.status;
      }

      // 只有当material_id不为null时才添加到参数中
      if (searchForm.material_id !== null) {
        params.material_id = searchForm.material_id;
      }

      // 添加删除状态参数（包括0，表示正常状态）
      if (searchForm.deleted !== null && searchForm.deleted !== undefined) {
        params.deleted = searchForm.deleted;
      }

      // 添加标注更新时间范围参数
      if (searchForm.annotation_updated_start) {
        params.annotation_updated_start = searchForm.annotation_updated_start;
      }
      if (searchForm.annotation_updated_end) {
        params.annotation_updated_end = searchForm.annotation_updated_end;
      }

      const res = await getAnnotationListApi(params);

      // 检查响应结构并处理
      if (res && typeof res === "object") {
        // 正确处理后端返回的数据结构
        const data = res.data || res; // 兼容两种可能的数据结构
        const list = data.records || [];

        // 处理数据，确保字段兼容
        const processedList = list.map((item: any) => ({
          ...item,
          id: item.id !== undefined ? item.id : null,
          project_name: item.project_name || "",
          creator_name: item.creator_name || "",
          created_at: item.created_at || null,
          is_directory_image: item.is_directory_image || false, // 标记是否为目录图片
          deleted: item.deleted !== undefined ? item.deleted : 0 // 删除状态，默认为0（正常）
        }));

        imageList.value = processedList;
        pagination.total = data.total || 0;

        if (processedList.length === 0) {
          ElMessage.info("暂无符合条件的数据");
        }
      } else {
        ElMessage.error("获取图片列表失败");
      }
    } catch (error: any) {
      console.error("获取图片列表失败:", error);
      // HTTP拦截器已经处理了错误提示，这里不需要重复提示
      // 只有在非HTTP错误的情况下才显示提示
      if (!error.response) {
        ElMessage.error("获取图片列表失败，请稍后重试");
      }
    }
  };

  // 获取标注详情
  const fetchAnnotationDetailData = async (imageId: number, globalShowState: boolean = true, modelId?: number | null) => {
    try {
      const params: { image_id: number; model_id?: number } = { image_id: imageId };
      // 如果提供了 model_id，则添加到请求参数中
      if (modelId !== undefined && modelId !== null) {
        params.model_id = modelId;
      }

      const res = await getAnnotationDetailApi(params);

      if (res && typeof res === "object" && res.data && res.data.image) {
        currentImage.value = res.data.image;
        // 初始化标注的可见性状态，优先使用全局状态，其次使用全局状态
        annotations.value = (res.data.annotations || []).map((annotation: AnnotationDetail) => {
          // 检查全局可见性状态中是否有该标注的记录
          const globalVisibility = globalAnnotationVisibility.value.get(annotation.id);
          let isVisible: boolean;

          // 1. 优先检查单个标注的全局可见性状态
          if (globalVisibility !== undefined) {
            // 如果全局状态中有记录，使用全局状态
            isVisible = globalVisibility;
          } else if (annotation.isVisible !== undefined) {
            // 如果标注本身有可见性状态，使用标注的状态
            isVisible = annotation.isVisible;
          } else {
            // 否则使用全局显示状态
            // 标签组的可见性基于全局显示状态来应用，即：如果全局隐藏，标签组隐藏也隐藏；如果全局显示，标签组隐藏也隐藏
            const labelGroupVisibility = globalLabelGroupVisibility.value.get(annotation.label_id);
            if (labelGroupVisibility !== undefined) {
              // 标签组有可见性设置，基于全局显示状态和标签组状态来决定
              isVisible = globalShowState && labelGroupVisibility;
            } else {
              // 没有标签组设置，使用全局显示状态
              isVisible = globalShowState;
            }
          }

          return {
            ...annotation,
            isVisible
          };
        });
        imageInfo.value = res.data.image;
        return res.data;
      } else {
        ElMessage.error("获取标注详情失败，返回数据格式不正确");
        return null;
      }
    } catch (error: any) {
      console.error("获取标注详情失败:", error);
      // HTTP拦截器已经处理了错误提示，这里不需要重复提示
      // 只有在非HTTP错误的情况下才显示提示
      if (!error.response) {
        ElMessage.error("获取标注详情失败，请稍后重试");
      }
      return null;
    }
  };

  // 获取标签列表
  const fetchLabelListData = async () => {
    try {
      // 使用getAllLabelsApi获取所有标签，不分页
      const res: any = await getAllLabelsApi();
      // 检查响应结构并处理
      if (res && typeof res === "object") {
        // 正确处理后端返回的数据结构，使用records字段
        availableLabels.value = res.records || res.data?.records || res.data || [];
      } else {
        ElMessage.error("获取标签列表失败");
      }
    } catch (error: any) {
      console.error("获取标签列表失败:", error);
      // HTTP拦截器已经处理了错误提示，这里不需要重复提示
      // 只有在非HTTP错误的情况下才显示提示
      if (!error.response) {
        ElMessage.error("获取标签列表失败，请稍后重试");
      }
    }
  };

  // 保存标注
  const saveAnnotation = async (annotation: AnnotationDetail) => {
    if (!annotation?.yolo_format) {
      ElMessage.error("标注数据不完整");
      return;
    }

    // 检查是否为未标注图片（包括目录图片）
    if (currentImage.value?.id === null || currentImage.value?.id === undefined) {
      // 调用创建图片和标注的API
      try {
        const validatedData = {
          yolo_format: {
            center_x: Math.max(0, Math.min(1, Number(annotation.yolo_format.center_x.toFixed(6)))),
            center_y: Math.max(0, Math.min(1, Number(annotation.yolo_format.center_y.toFixed(6)))),
            width: Math.max(0.001, Math.min(1, Number(annotation.yolo_format.width.toFixed(6)))),
            height: Math.max(0.001, Math.min(1, Number(annotation.yolo_format.height.toFixed(6)))),
            label_id: Number(annotation.yolo_format.label_id)
          }
        };

        const createData = {
          operation_type: "create_image_and_annotation",
          file_name: currentImage.value?.file_name || "",
          file_path: currentImage.value?.file_path || "",
          ...validatedData
        };

        const response = await createAnnotationApi(createData);

        // 检查响应结构并处理
        if (response && typeof response === "object" && response.code === 200) {
          ElMessage.success(response.message || "图片已入库并创建标注成功");
          // 更新当前图片ID和文件路径，并添加时间戳以强制刷新图片
          if (response.data) {
            if (response.data.image_id) {
              currentImage.value.id = response.data.image_id;
            } else if (response.data.data && response.data.data.image_id) {
              // 处理嵌套data结构
              currentImage.value.id = response.data.data.image_id;
            }

            // 更新图片路径（如果图片被移动了）
            if (response.data.file_path) {
              // 添加时间戳参数以绕过浏览器缓存
              currentImage.value.file_path = response.data.file_path + "?t=" + Date.now();

              // 同时更新 imageInfo 的路径
              if (imageInfo.value) {
                imageInfo.value.file_path = response.data.file_path + "?t=" + Date.now();
              }
            }

            // 更新标注ID
            if (response.data.annotation_id) {
              annotation.id = response.data.annotation_id;
            } else if (response.data.data && response.data.data.annotation_id) {
              // 处理嵌套data结构
              annotation.id = response.data.data.annotation_id;
            }

            annotation.isNew = false;
            annotation.isModified = false;

            // 刷新图片列表以显示更新后的图片信息
            // 延迟刷新，确保数据库已更新
            setTimeout(() => {
              fetchImageList();
            }, 500);
          }
        } else {
          console.error("API返回错误:", response);
          ElMessage.error(response?.message || "保存失败");
        }
      } catch (error: any) {
        console.error("创建图片和标注失败:", error);
        ElMessage.error(error.message || "创建图片和标注失败");
      }
      return;
    }

    // 已标注图片的保存逻辑
    try {
      const validatedData = {
        yolo_format: {
          center_x: Math.max(0, Math.min(1, Number(annotation.yolo_format.center_x.toFixed(6)))),
          center_y: Math.max(0, Math.min(1, Number(annotation.yolo_format.center_y.toFixed(6)))),
          width: Math.max(0.001, Math.min(1, Number(annotation.yolo_format.width.toFixed(6)))),
          height: Math.max(0.001, Math.min(1, Number(annotation.yolo_format.height.toFixed(6)))),
          label_id: Number(annotation.yolo_format.label_id)
        }
      };

      let response;
      if (annotation.isNew) {
        // 新标注 - 使用创建API
        const createData = {
          operation_type: "create_annotation",
          image_id: Number(currentImage.value?.id),
          ...validatedData
        };

        try {
          response = await createAnnotationApi(createData);

          // 检查响应结构并处理
          if (response && typeof response === "object" && response.code === 200) {
            // 更新标注ID为数据库返回的真实ID
            const responseData = response.data?.data || response.data;
            if (responseData) {
              if (responseData.id !== undefined) {
                annotation.id = responseData.id;
              }
              // 更新 is_own 和 is_auto 字段（如果后端返回了这些字段）
              if (responseData.is_own !== undefined) {
                annotation.is_own = responseData.is_own;
              } else {
                // 如果后端没有返回 is_own，默认设置为 true（新创建的标注应该是当前用户的）
                annotation.is_own = true;
              }
              if (responseData.is_auto !== undefined) {
                annotation.is_auto = responseData.is_auto;
              } else {
                // 如果后端没有返回 is_auto，默认设置为 false（手动创建的标注）
                annotation.is_auto = false;
              }
            }
            annotation.isNew = false;
            ElMessage.success(response.message || "新标注已创建");
          } else {
            console.error("API返回错误:", response);
            // 错误消息由拦截器统一处理，这里不需要重复提示
            // 如果创建失败，从标注列表中移除临时标注
            const index = annotations.value.findIndex(ann => ann.id === annotation.id);
            if (index > -1) {
              annotations.value.splice(index, 1);
            }
            // 如果当前选中的是失败的标注，清除选中状态
            if (selectedAnnotation.value?.id === annotation.id) {
              selectedAnnotation.value = null;
              selectedAnnotationIndex.value = -1;
            }
          }
        } catch (error: any) {
          console.error("创建标注API调用失败:", error);
          // 错误消息由拦截器统一处理，这里不需要重复提示
          // 如果创建失败，从标注列表中移除临时标注
          const index = annotations.value.findIndex(ann => ann.id === annotation.id);
          if (index > -1) {
            annotations.value.splice(index, 1);
          }
          // 如果当前选中的是失败的标注，清除选中状态
          if (selectedAnnotation.value?.id === annotation.id) {
            selectedAnnotation.value = null;
            selectedAnnotationIndex.value = -1;
          }
          return;
        }
      } else {
        // 已存在的标注 - 使用更新API
        // 记录更新前是否是系统标注
        const wasSystemAnnotation = annotation.is_auto === true;

        const updateData = {
          id: Number(annotation.id),
          ...validatedData
        };

        try {
          response = await updateAnnotationApi(updateData);

          // 检查响应结构并处理
          if (response && typeof response === "object" && response.code === 200) {
            ElMessage.success(response.message || "标注已更新");
            // 清除修改标记
            annotation.isModified = false;

            // 更新 is_own 和 is_auto 字段（如果后端返回了这些字段）
            const responseData = response.data?.data || response.data;
            if (responseData) {
              if (responseData.is_own !== undefined) {
                annotation.is_own = responseData.is_own;
              }
              if (responseData.is_auto !== undefined) {
                annotation.is_auto = responseData.is_auto;
              }
            } else if (wasSystemAnnotation) {
              // 如果后端没有返回这些字段，但更新前是系统标注，则默认设置为我的标注
              annotation.is_own = true;
              annotation.is_auto = false;
            }
          } else {
            console.error("API返回错误:", response);
            // 错误消息由拦截器统一处理，这里不需要重复提示
          }
        } catch (error: any) {
          console.error("更新标注API调用失败:", error);
          // 错误消息由拦截器统一处理，这里不需要重复提示
          return;
        }
      }

      // 检查响应结构并处理
      if (response && typeof response === "object" && response.code === 200) {
        // 清除修改标记
        annotation.isModified = false;
      }
    } catch (error: any) {
      console.error("保存标注失败:", error);
      // 错误消息由拦截器统一处理，这里不需要重复提示
    }
  };

  // 删除标注
  const deleteAnnotation = async (annotation: AnnotationDetail) => {
    const isNewAnnotation =
      annotation.isNew || !annotation.id || annotation.id.toString().startsWith(Date.now().toString().substring(0, 8));

    if (isNewAnnotation) {
      // 新增未保存的标注，直接从本地删除
      const index = annotations.value.findIndex(ann => ann.id === annotation.id);
      if (index !== -1) {
        annotations.value.splice(index, 1);

        // 如果删除的是当前选中的标注，清除选中状态
        if (selectedAnnotation.value?.id === annotation.id) {
          selectedAnnotation.value = null;
        }

        ElMessage.success("标注已删除");
      }
    } else {
      // 已保存的标注，调用API删除
      const annotationId = Number(annotation.id);

      // 检查是否正在删除该标注，避免重复请求
      if (deletingAnnotationIds.value.has(annotationId)) {
        console.warn("该标注正在删除中，请勿重复操作");
        return;
      }

      // 标记为正在删除
      deletingAnnotationIds.value.add(annotationId);

      try {
        const response = await deleteAnnotationApi({ id: annotationId });

        if (response.code === 200) {
          const index = annotations.value.findIndex(ann => ann.id === annotation.id);
          if (index !== -1) {
            annotations.value.splice(index, 1);

            // 如果删除的是当前选中的标注，清除选中状态
            if (selectedAnnotation.value?.id === annotation.id) {
              selectedAnnotation.value = null;
            }

            ElMessage.success("标注已删除");
          }
        }
        // 错误处理由拦截器统一处理，这里不需要额外的错误提示
      } catch (error) {
        // 错误已经被拦截器处理并显示，这里只需要静默捕获，避免错误被抛出导致遮罩层无法关闭
        console.error("删除标注失败:", error);
        // 确保错误不会继续传播，避免影响其他操作
      } finally {
        // 无论成功还是失败，都要清除删除状态
        deletingAnnotationIds.value.delete(annotationId);
      }
    }
  };

  // 切换单个标注的可见性
  const toggleAnnotationVisibility = (annotation: AnnotationDetail) => {
    annotation.isVisible = !annotation.isVisible;

    // 保存到全局可见性状态中
    globalAnnotationVisibility.value.set(annotation.id, annotation.isVisible);

    // 强制更新视图
    annotations.value = [...annotations.value];

    // 检查是否需要更新整体显示状态
    const hasVisibleAnnotations = annotations.value.some(ann => ann.isVisible !== false);
    // 如果当前整体显示状态与标注可见性不匹配，需要触发整体状态更新
    // 这里我们通过返回一个标志来通知父组件是否需要更新整体状态
    return {
      annotation,
      hasVisibleAnnotations,
      shouldUpdateGlobalState: true
    };
  };

  // 批量删除标注
  const batchDeleteAnnotations = async (annotationsToDelete: AnnotationDetail[]) => {
    if (!annotationsToDelete || annotationsToDelete.length === 0) {
      ElMessage.warning("请选择要删除的标注");
      return;
    }

    // 分离新标注和已保存的标注
    const newAnnotations: AnnotationDetail[] = [];
    const savedAnnotations: AnnotationDetail[] = [];

    annotationsToDelete.forEach(annotation => {
      const isNewAnnotation =
        annotation.isNew || !annotation.id || annotation.id.toString().startsWith(Date.now().toString().substring(0, 8));
      if (isNewAnnotation) {
        newAnnotations.push(annotation);
      } else {
        savedAnnotations.push(annotation);
      }
    });

    // 先删除本地的新标注
    newAnnotations.forEach(annotation => {
      const index = annotations.value.findIndex(ann => ann.id === annotation.id);
      if (index !== -1) {
        annotations.value.splice(index, 1);
      }
    });

    // 如果有已保存的标注，调用批量删除API
    if (savedAnnotations.length > 0) {
      const annotationIds = savedAnnotations
        .map(ann => ann.id)
        .filter(id => id !== null && id !== undefined)
        .map(id => Number(id));

      if (annotationIds.length > 0) {
        const loading = ElLoading.service({
          lock: true,
          text: "正在删除标注...",
          background: "rgba(0, 0, 0, 0.7)"
        });

        try {
          const response = await deleteAnnotationApi({ ids: annotationIds });

          if (response.code === 200) {
            // 从列表中移除已删除的标注
            savedAnnotations.forEach(annotation => {
              const index = annotations.value.findIndex(ann => ann.id === annotation.id);
              if (index !== -1) {
                annotations.value.splice(index, 1);
              }
            });

            // 如果删除的标注中包含当前选中的标注，清除选中状态
            if (selectedAnnotation.value && savedAnnotations.some(ann => ann.id === selectedAnnotation.value?.id)) {
              selectedAnnotation.value = null;
            }

            ElMessage.success(`成功删除 ${annotationIds.length} 个标注`);
          }
          // 错误处理由拦截器统一处理，这里不需要额外的错误提示
        } catch (error) {
          console.error("批量删除标注失败:", error);
          // 错误处理由拦截器统一处理，这里不需要额外的错误提示
        } finally {
          loading.close();
        }
      }
    } else if (newAnnotations.length > 0) {
      // 只删除新标注的情况
      ElMessage.success(`成功删除 ${newAnnotations.length} 个标注`);
    }
  };

  // 清理全局标注可见性状态
  const clearGlobalAnnotationVisibility = () => {
    globalAnnotationVisibility.value.clear();
  };

  return {
    // 状态
    imageList,
    annotations,
    availableLabels,
    currentImage,
    selectedAnnotation,
    imageInfo,
    imageDimensions,
    pagination,
    searchForm,
    globalAnnotationVisibility,
    globalLabelGroupVisibility,

    // 方法
    getImageUrl,
    fetchImageList,
    fetchAnnotationDetail: fetchAnnotationDetailData,
    fetchLabelList: fetchLabelListData,
    saveAnnotation,
    deleteAnnotation,
    batchDeleteAnnotations,
    toggleAnnotationVisibility,
    clearGlobalAnnotationVisibility
  };
}
