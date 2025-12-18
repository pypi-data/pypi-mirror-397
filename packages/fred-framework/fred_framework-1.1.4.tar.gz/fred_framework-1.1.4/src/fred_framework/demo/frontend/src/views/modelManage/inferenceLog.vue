<template>
  <div class="inference-log-container">
    <div class="layout-wrapper">
      <!-- 左侧门店筛选器 -->
      <StoreFilter v-model="currentStoreId" @change="handleStoreChange" />

      <!-- 右侧表格 -->
      <div class="table-box">
        <ProTable
          ref="proTable"
          :columns="columns"
          :request-api="getInferenceLogList"
          :data-callback="dataCallback"
          :request-auto="false"
          :use-computed-total="false"
        >
        </ProTable>

        <!-- 图片查看对话框 -->
        <el-dialog v-model="imageDialogVisible" :title="imageDialogTitle" width="80%" destroy-on-close>
          <template #header>
            <div class="dialog-header">
              <span>{{ imageDialogTitle }}</span>
              <el-button
                v-if="currentImageUrl && currentRowData && currentRowData.bbox"
                type="primary"
                size="small"
                @click="toggleAnnotationVisibility"
              >
                {{ showAnnotation ? t("inferenceLog.hideAnnotation") : t("inferenceLog.showAnnotation") }}
              </el-button>
            </div>
          </template>
          <div class="image-viewer">
            <template v-if="currentImageUrl">
              <div class="image-wrapper" ref="imageWrapperRef">
                <img
                  :src="currentImageUrl"
                  alt="图片"
                  class="viewer-image"
                  ref="viewerImageRef"
                  @error="handleImageError"
                  @load="handleImageLoad"
                />
                <!-- 标注框 -->
                <div
                  v-show="showAnnotation && currentRowData && currentRowData.bbox && imageLoaded"
                  class="annotation-box"
                  :style="getAnnotationStyle(currentRowData.bbox, currentRowData.image_info)"
                >
                  <div class="annotation-label">
                    {{ currentRowData.label || currentRowData.label_name || "-" }}
                  </div>
                </div>
              </div>
            </template>
            <div v-else class="no-image">{{ t("inferenceLog.noImage") }}</div>
            <div v-if="imageLoading" class="image-loading">{{ t("inferenceLog.loadingImage") }}</div>
            <div v-if="imageError" class="image-error">{{ t("inferenceLog.imageLoadError") }}</div>
          </div>
        </el-dialog>
      </div>
    </div>
  </div>
</template>

<script setup lang="tsx" name="inferenceLog">
import { getInferenceLogListApi } from "@/api/modules/inferenceLog";
import { getAllLabelsApi } from "@/api/modules/label";
import { getModelListApi } from "@/api/modules/model";
import { getStoreCameraChannels, type CameraChannelInfo, type StoreInfo } from "@/api/modules/store";
import ProTable from "@/components/ProTable/index.vue";
import { ColumnProps, ProTableInstance } from "@/components/ProTable/interface";
import StoreFilter from "@/components/StoreFilter/index.vue";
import { View } from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";
import { computed, nextTick, onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";

// 国际化
const { t } = useI18n();

// ProTable 实例
const proTable = ref<ProTableInstance>();

// 图片查看对话框
const imageDialogVisible = ref(false);
const imageDialogTitle = ref("");
const currentImageUrl = ref("");
const imageLoading = ref(false);
const imageError = ref(false);
const imageLoaded = ref(false);
const showAnnotation = ref(true);
const currentRowData = ref<any>(null);
const imageWrapperRef = ref<HTMLElement | null>(null);
const viewerImageRef = ref<HTMLImageElement | null>(null);

// 标签列表和模型列表（用于 render 函数显示）
const labelList = ref<Array<{ id: number; name: string }>>([]);
const modelList = ref<Array<{ id: number; name: string }>>([]);

// 门店选择相关
const currentStoreId = ref<number | null>(null);

// 摄像头通道列表（根据选中的门店加载）
const cameraChannelList = ref<CameraChannelInfo[]>([]);
const cameraChannelMap = computed(() => {
  const map = new Map<number, CameraChannelInfo>();
  cameraChannelList.value.forEach(channel => {
    map.set(channel.id, channel);
  });
  return map;
});

// 模型映射表（用于快速查找模型名称）
const modelMap = computed(() => {
  const map = new Map<number, string>();
  modelList.value.forEach(model => {
    map.set(model.id, model.name);
  });
  return map;
});

// 处理门店选择变化
const handleStoreChange = async (store: StoreInfo | null) => {
  if (store) {
    currentStoreId.value = store.id;
    // 清空摄像头通道列表
    cameraChannelList.value = [];
    // 加载该门店的摄像头通道列表（必须等待加载完成）
    await loadCameraChannels(store.id);
    // 清空搜索结果和搜索条件
    if (proTable.value) {
      // 清空搜索表单中的条件
      const searchForm = proTable.value.searchParam;
      if (searchForm) {
        // 清空标签选择
        if (searchForm.label_id !== undefined) {
          searchForm.label_id = undefined;
        }
        // 清空时间范围
        if (searchForm.frame_stamp !== undefined) {
          searchForm.frame_stamp = undefined;
        }
        if (searchForm.start_time !== undefined) {
          searchForm.start_time = undefined;
        }
        if (searchForm.end_time !== undefined) {
          searchForm.end_time = undefined;
        }
        // 自动选中第一个摄像头（如果存在）
        if (cameraChannelList.value.length > 0) {
          const firstCameraId = cameraChannelList.value[0].id;
          searchForm.camera_id = firstCameraId;
        } else {
          searchForm.camera_id = undefined;
        }
      }
      // 清除 camera_id 的 enum 缓存，强制重新加载
      if (proTable.value.enumMap) {
        proTable.value.enumMap.delete("camera_id");
      }
      // 重置分页信息，将总数设为0，使表格显示为空
      if (proTable.value.pageable) {
        proTable.value.pageable.pageNum = 1;
        proTable.value.pageable.total = 0;
      }
      // 清空表格数据，避免显示错误的数据
      // 由于 tableData 是计算属性，通过清空数组来清空表格显示
      if (proTable.value.tableData && Array.isArray(proTable.value.tableData)) {
        proTable.value.tableData.splice(0, proTable.value.tableData.length);
      }
      // 等待摄像头数据加载完成后，如果有摄像头，自动调用推理日志接口
      // 确保在摄像头通道接口调用成功后再调用推理日志接口
      if (cameraChannelList.value.length > 0 && searchForm.camera_id) {
        // 使用 nextTick 确保响应式更新完成后再调用接口
        await nextTick();
        // 再次确认 camera_id 已设置，然后触发表格刷新
        if (searchForm.camera_id) {
          // 使用 search() 方法，它会自动更新 totalParam 并调用接口
          // 这样可以确保 searchParam 中的 camera_id 被正确传递
          proTable.value.search();
        }
      }
    }
  }
};

// 加载摄像头通道列表
const loadCameraChannels = async (storeId: number) => {
  try {
    const response = await getStoreCameraChannels(storeId);

    // 根据 axios 拦截器的处理，response 可能是 { code: 200, data: [...] } 或直接是数组
    let channels: CameraChannelInfo[] = [];

    if (response && response.data) {
      // 如果 response.data 是数组，直接使用
      if (Array.isArray(response.data)) {
        channels = response.data;
      } else if (response.data.data && Array.isArray(response.data.data)) {
        // 嵌套结构
        channels = response.data.data;
      }
    } else if (Array.isArray(response)) {
      // 如果 response 本身就是数组
      channels = response;
    }

    cameraChannelList.value = channels;
  } catch (error) {
    console.error("加载摄像头通道列表失败:", error);
    cameraChannelList.value = [];
  }
};

// 注意：标签和模型列表通过 enum 异步加载，enum 函数会在 ProTable 初始化时自动调用

// 获取图片URL
const getImageUrl = (filePath: string | undefined) => {
  if (!filePath) return "";

  // 如果已经是完整URL，直接返回
  if (filePath.startsWith("http://") || filePath.startsWith("https://")) {
    return filePath;
  }

  // 直接使用后端返回的路径，不做任何拼接处理
  // 后端返回的路径格式应该是完整的访问路径，如：/raw/sn/camera_id/...
  let path = filePath.replace(/\\/g, "/");

  // 确保路径以 / 开头
  if (!path.startsWith("/")) {
    path = "/" + path;
  }

  // 使用完整的API地址
  const baseUrl = import.meta.env.VITE_API_URL || "/api";
  let fullUrl;
  if (baseUrl.startsWith("http")) {
    fullUrl = `${baseUrl.replace(/\/$/, "")}${path}`;
  } else {
    // 对于相对路径，直接使用路径
    fullUrl = path;
  }

  return fullUrl;
};

// 处理图片加载错误
const handleImageError = () => {
  imageLoading.value = false;
  imageError.value = true;
  imageLoaded.value = false;
  ElMessage.error(t("inferenceLog.imageLoadError"));
};

// 处理图片加载成功
const handleImageLoad = () => {
  imageLoading.value = false;
  imageError.value = false;
  imageLoaded.value = true;
  // 等待 DOM 更新后重新计算标注框位置
  nextTick(() => {
    // 触发响应式更新
    if (currentRowData.value) {
      currentRowData.value = { ...currentRowData.value };
    }
  });
};

// 查看原图
const viewRawImage = (row: any) => {
  // 重置状态
  imageLoading.value = true;
  imageError.value = false;
  imageLoaded.value = false;
  currentImageUrl.value = "";
  showAnnotation.value = true;
  currentRowData.value = null;

  // 保存当前行的数据（包括 bbox 和 image_info）
  currentRowData.value = {
    bbox: row.bbox,
    image_info: row.image_info,
    label: row.label,
    label_name: row.label_name
  };

  // 优先使用后端返回的 image_path
  if (row.image_path) {
    currentImageUrl.value = getImageUrl(row.image_path);
    imageDialogTitle.value = t("inferenceLog.viewRawImage");
    imageDialogVisible.value = true;
    return;
  }

  // 降级处理：使用 image_names.raw_image
  const imageNames = row.image_names;
  if (!imageNames || !imageNames.raw_image) {
    imageLoading.value = false;
    ElMessage.warning(t("inferenceLog.noRawImage"));
    return;
  }
  currentImageUrl.value = getImageUrl(imageNames.raw_image);
  imageDialogTitle.value = t("inferenceLog.viewRawImage");
  imageDialogVisible.value = true;
};

// 切换标注显示/隐藏
const toggleAnnotationVisibility = () => {
  showAnnotation.value = !showAnnotation.value;
};

// 获取标注框样式
const getAnnotationStyle = (bbox: number[] | null | undefined, imageInfo: any) => {
  if (!bbox || !Array.isArray(bbox) || bbox.length !== 4 || !imageLoaded.value) {
    return { display: "none" };
  }

  const imgElement = viewerImageRef.value;
  if (!imgElement || !imgElement.naturalWidth || !imgElement.naturalHeight) {
    return { display: "none" };
  }

  // bbox 格式是 YOLO 格式 [center_x, center_y, width, height]（归一化的中心点坐标和宽高）
  const [centerXNormalized, centerYNormalized, widthNormalized, heightNormalized] = bbox;

  // 获取图片的原始尺寸和显示尺寸
  const imgRect = imgElement.getBoundingClientRect();
  const imgNaturalWidth = imageInfo?.width || imgElement.naturalWidth || 0;
  const imgNaturalHeight = imageInfo?.height || imgElement.naturalHeight || 0;
  const displayWidth = imgElement.clientWidth || imgElement.width || imgRect.width;
  const displayHeight = imgElement.clientHeight || imgElement.height || imgRect.height;

  if (imgNaturalWidth === 0 || imgNaturalHeight === 0) {
    return { display: "none" };
  }

  // 计算缩放比例
  const scaleX = displayWidth / imgNaturalWidth;
  const scaleY = displayHeight / imgNaturalHeight;

  // 将归一化的 YOLO 坐标转换为像素坐标
  const centerX = centerXNormalized * imgNaturalWidth * scaleX;
  const centerY = centerYNormalized * imgNaturalHeight * scaleY;
  const width = widthNormalized * imgNaturalWidth * scaleX;
  const height = heightNormalized * imgNaturalHeight * scaleY;

  // 计算左上角坐标
  const left = centerX - width / 2;
  const top = centerY - height / 2;

  // 确保标注框不超出图片边界
  const clampedLeft = Math.max(0, Math.min(left, displayWidth - width));
  const clampedTop = Math.max(0, Math.min(top, displayHeight - height));
  const clampedWidth = Math.min(width, displayWidth - clampedLeft);
  const clampedHeight = Math.min(height, displayHeight - clampedTop);

  return {
    position: "absolute" as const,
    left: `${clampedLeft}px`,
    top: `${clampedTop}px`,
    width: `${clampedWidth}px`,
    height: `${clampedHeight}px`,
    border: "2px solid #409EFF",
    backgroundColor: "rgba(64, 158, 255, 0.1)",
    pointerEvents: "none" as const,
    zIndex: 10
  };
};

// dataCallback 是对于返回的表格数据做处理
const dataCallback = (data: any) => {
  // 如果返回的是数组，说明后端没有返回分页信息，使用数组长度作为总记录数（这种情况不应该发生，但为了兼容性保留）
  if (Array.isArray(data)) {
    return {
      records: data,
      total: data.length
    };
  }
  // 如果返回的是对象，使用 records 和 total
  // 注意：后端返回的 total 可能为 0（不查询总记录数），但 inferenceLog 页面使用 useComputedTotal: false，直接使用 pageable.total
  const records = data.records || [];
  const total = data.total || 0;

  return {
    records: records,
    total: total
  };
};

// 获取推理日志列表
const getInferenceLogList = (params: any) => {
  const queryParams: any = {
    pageNum: params.pageNum,
    pageSize: params.pageSize
  };

  // 如果有选中的门店，传递门店ID
  if (currentStoreId.value) {
    queryParams.store_id = currentStoreId.value;
  }

  // 如果有camera_id，传递camera_id（转换为数字，因为后端Schema要求Int类型）
  // 注意：必须要有 camera_id 才能查询，如果没有则返回空结果
  if (params.camera_id) {
    const cameraId = Number(params.camera_id);
    if (!isNaN(cameraId)) {
      queryParams.camera_id = cameraId;
    } else {
      // 如果 camera_id 无效，返回空结果，避免参数错误
      return Promise.resolve({ records: [], total: 0 });
    }
  } else {
    // 如果没有 camera_id，返回空结果，避免参数不够
    return Promise.resolve({ records: [], total: 0 });
  }

  // 处理帧时间（frame_stamp）的时间区间查询
  if (params.frame_stamp && Array.isArray(params.frame_stamp) && params.frame_stamp.length === 2) {
    queryParams.start_time = params.frame_stamp[0];
    queryParams.end_time = params.frame_stamp[1];
  } else {
    // 兼容原有的start_time和end_time参数
    if (params.start_time) {
      queryParams.start_time = params.start_time;
    }
    if (params.end_time) {
      queryParams.end_time = params.end_time;
    }
  }

  // 如果有label_id或cloud_label，传递label_id（cloud_label是前端显示的列名，实际对应label_id）
  if (params.label_id) {
    queryParams.label_id = params.label_id;
  } else if (params.cloud_label) {
    queryParams.label_id = params.cloud_label;
  }

  return getInferenceLogListApi(queryParams);
};

// 表格配置项 - 使用 computed 确保语言切换时能够响应更新
const columns = computed<ColumnProps<any>[]>(() => [
  {
    prop: "camera_id",
    label: t("inferenceLog.camera"),
    width: 200,
    isFilterEnum: false,
    search: {
      el: "select",
      props: {
        placeholder: currentStoreId.value ? t("inferenceLog.selectCamera") : t("inferenceLog.selectStoreFirst"),
        clearable: true,
        filterable: true,
        disabled: !currentStoreId.value
      }
    },
    enum: async () => {
      // 如果没有选中门店，返回空列表
      if (!currentStoreId.value) {
        return { data: [] };
      }

      try {
        // 确保摄像头通道列表已加载
        if (cameraChannelList.value.length === 0) {
          await loadCameraChannels(currentStoreId.value);
        }

        // 如果加载后仍然为空，返回空列表
        if (cameraChannelList.value.length === 0) {
          return { data: [] };
        }

        // 构建下拉选项，显示格式：通道:1,id:1
        const options = cameraChannelList.value.map((channel: CameraChannelInfo) => ({
          label: `通道:${channel.channel_id || channel.id},id:${channel.id}`,
          value: channel.id
        }));

        return { data: options };
      } catch (error) {
        console.error("获取摄像头通道列表失败:", error);
        return { data: [] };
      }
    },
    render: (scope: any) => {
      const cameraId = scope.row.camera_id;
      if (cameraId != null && cameraId !== undefined) {
        const cameraIdNum = typeof cameraId === "string" ? parseInt(cameraId, 10) : Number(cameraId);
        if (!isNaN(cameraIdNum) && cameraChannelMap.value.size > 0) {
          const channel = cameraChannelMap.value.get(cameraIdNum);
          if (channel) {
            return (
              <span>
                通道:{channel.channel_id || channel.id},id:{channel.id}
              </span>
            );
          }
        }
        // 如果找不到，显示ID
        return <span>{cameraIdNum}</span>;
      }
      return <span>-</span>;
    }
  },
  {
    prop: "recognized_label",
    label: t("inferenceLog.recognizedLabel"),
    width: 200,
    render: (scope: any) => {
      const tagId = scope.row.tag_id;
      const label = scope.row.label;

      // 如果有标签名字，显示：标签名字(ID:tag_id)
      if (label && typeof label === "string" && label.trim() !== "") {
        if (tagId != null && tagId !== undefined) {
          return <span>{`${label}(ID:${tagId})`}</span>;
        }
        return <span>{label}</span>;
      }

      // 如果只有tag_id，显示：ID:tag_id
      if (tagId != null && tagId !== undefined) {
        return <span>{`ID:${tagId}`}</span>;
      }

      return <span>-</span>;
    }
  },
  {
    prop: "cloud_label",
    label: t("inferenceLog.cloudLabel"),
    width: 200,
    isFilterEnum: false,
    search: {
      el: "select",
      props: {
        placeholder: t("inferenceLog.selectLabel"),
        clearable: true,
        filterable: true
      }
    },
    enum: async () => {
      try {
        const response: any = await getAllLabelsApi();
        let records: any[] = [];
        if (response && typeof response === "object") {
          if (response.data && response.data.records && Array.isArray(response.data.records)) {
            records = response.data.records;
          } else if (response.records && Array.isArray(response.records)) {
            records = response.records;
          } else if (Array.isArray(response.data)) {
            records = response.data;
          }
        }
        // 同步更新 labelList，供 render 函数使用
        labelList.value = records.map((item: any) => ({
          id: item.id,
          name: item.name
        }));
        return {
          data: records.map((item: any) => ({
            label: item.name,
            value: item.id
          }))
        };
      } catch (error) {
        console.error("获取标签列表失败:", error);
        labelList.value = [];
        return { data: [] };
      }
    },
    render: (scope: any) => {
      const labelId = scope.row.label_id;
      const labelName = scope.row.label_name;

      // 如果有标签名字，显示：标签名字(ID:label_id)
      if (labelName && typeof labelName === "string" && labelName.trim() !== "") {
        if (labelId != null && labelId !== undefined) {
          return <span>{`${labelName}(ID:${labelId})`}</span>;
        }
        return <span>{labelName}</span>;
      }

      // 如果找不到实际标签名字，用红色显示 ID:label_id
      if (labelId != null && labelId !== undefined) {
        return <span style={{ color: "red" }}>{`ID:${labelId}`}</span>;
      }

      return <span>-</span>;
    }
  },
  {
    prop: "model",
    label: t("inferenceLog.model"),
    width: 250,
    render: (scope: any) => {
      // 优先级：优先从 /api/admin/model/list 接口返回的数据中匹配模型名称
      // 这样可以确保显示的是最新的模型名称，而不是后端推理日志中可能过时的 model_name
      const modelId = scope.row.model_id;
      let modelName: string | null = null;

      if (modelId != null && modelId !== undefined) {
        // 确保类型匹配（将modelId转换为数字进行比较）
        let modelIdNum: number;
        if (typeof modelId === "string") {
          modelIdNum = parseInt(modelId, 10);
        } else {
          modelIdNum = Number(modelId);
        }

        if (!isNaN(modelIdNum)) {
          // 第一优先级：从 modelMap 中查找（数据来源：/api/admin/model/list 接口）
          // modelMap 是基于 modelList 构建的，modelList 在 enum 函数中从 /api/admin/model/list 加载
          if (modelMap.value.size > 0) {
            const name = modelMap.value.get(modelIdNum);
            if (name) {
              modelName = name;
            }
          }

          // 第二优先级：从 modelList 中查找（兼容处理，数据来源：/api/admin/model/list 接口）
          if (!modelName && modelList.value.length > 0) {
            const model = modelList.value.find(item => item.id === modelIdNum);
            if (model) {
              modelName = model.name;
            }
          }
        }
      }

      // 第三优先级：使用后端返回的 model_name（降级处理，可能不是最新的）
      // 只有在 /api/admin/model/list 接口数据未加载或找不到匹配项时才使用
      if (!modelName && scope.row.model_name) {
        modelName = scope.row.model_name;
      }

      // 获取模型版本
      const modelVersion = scope.row.model_version;

      // 如果有模型名称和版本，显示：模型名称（模型版本）
      if (modelName && modelVersion) {
        return <span>{`${modelName}(${modelVersion})`}</span>;
      }

      // 如果只有模型名称，显示模型名称
      if (modelName) {
        return <span>{modelName}</span>;
      }

      // 如果只有模型版本，显示版本
      if (modelVersion) {
        return <span>{`(${modelVersion})`}</span>;
      }

      return <span>-</span>;
    }
  },
  {
    prop: "frame_stamp",
    label: t("inferenceLog.frameTime"),
    width: 180,
    search: {
      el: "date-picker",
      span: 2,
      props: {
        type: "datetimerange",
        valueFormat: "YYYY-MM-DD HH:mm:ss",
        rangeSeparator: t("inferenceLog.to"),
        startPlaceholder: t("inferenceLog.startTime"),
        endPlaceholder: t("inferenceLog.endTime"),
        clearable: true
      }
    },
    render: (scope: any) => {
      const frameStamp = scope.row.frame_stamp;
      if (frameStamp) {
        return <span>{frameStamp}</span>;
      }
      return <span>-</span>;
    }
  },
  {
    prop: "inference_time",
    label: t("inferenceLog.inferenceTime"),
    width: 180,
    render: (scope: any) => {
      const inferenceTime = scope.row.inference_time;
      if (inferenceTime) {
        return <span>{inferenceTime}</span>;
      }
      return <span>-</span>;
    }
  },
  {
    prop: "operation",
    label: t("inferenceLog.operation"),
    fixed: "right",
    render: (scope: any) => {
      return (
        <div>
          <el-button type="primary" link size="small" icon={View} onClick={() => viewRawImage(scope.row)}>
            {t("inferenceLog.viewRawImage")}
          </el-button>
        </div>
      );
    }
  }
]);

// 加载模型列表（供 render 函数使用）
const loadModelList = async () => {
  try {
    const response: any = await getModelListApi({
      pageNum: 1,
      pageSize: 1000
    });
    let records: any[] = [];
    if (response && typeof response === "object") {
      if (response.data && response.data.records && Array.isArray(response.data.records)) {
        records = response.data.records;
      } else if (response.records && Array.isArray(response.records)) {
        records = response.records;
      } else if (Array.isArray(response.data)) {
        records = response.data;
      }
    }
    // 同步更新 modelList，供 render 函数使用
    modelList.value = records.map((item: any) => ({
      id: item.id,
      name: item.name
    }));
  } catch (error) {
    console.error("获取模型列表失败:", error);
    modelList.value = [];
  }
};

// 组件挂载时初始化
onMounted(() => {
  // 加载模型列表
  loadModelList();
});
</script>

<style scoped lang="scss">
@import "@/styles/table-optimization.scss";

.inference-log-container {
  @extend .layout-table-container;
  height: 100%;
  overflow: hidden;
}

// 避免在没有数据的情况下出现滚动条
:deep(.el-table) {
  .el-table__body-wrapper {
    // 当表格为空时，隐藏滚动条
    &:has(.el-table__empty-block) {
      overflow: hidden !important;
    }
  }

  .el-table__empty-block {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
  }
}

.image-viewer {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: 400px;
  position: relative;
}

.image-wrapper {
  position: relative;
  display: inline-block;
  max-width: 100%;
}

.viewer-image {
  max-width: 100%;
  max-height: 70vh;
  object-fit: contain;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: block;
}

.annotation-box {
  position: absolute;
  border: 2px solid #409eff;
  background-color: rgba(64, 158, 255, 0.1);
  pointer-events: none;
  z-index: 10;

  .annotation-label {
    position: absolute;
    top: -22px;
    left: 0;
    background-color: #409eff;
    color: white;
    padding: 2px 6px;
    font-size: 12px;
    border-radius: 2px;
    white-space: nowrap;
    line-height: 1.2;
  }
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding-right: 80px; // 为关闭按钮留出足够空间，避免重叠
  position: relative;

  > span {
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    padding-right: 12px; // 与按钮保持间距
  }

  .el-button {
    margin-right: 20px; // 增加右边距，让按钮向左移动，避免与关闭按钮重叠
    flex-shrink: 0;
  }
}

.no-image {
  text-align: center;
  color: #909399;
  font-size: 14px;
  padding: 20px;
}

.image-loading {
  text-align: center;
  color: #409eff;
  font-size: 14px;
  padding: 20px;
}

.image-error {
  text-align: center;
  color: #f56c6c;
  font-size: 14px;
  padding: 20px;
}
</style>
