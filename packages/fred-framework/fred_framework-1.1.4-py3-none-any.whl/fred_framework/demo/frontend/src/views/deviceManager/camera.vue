<template>
  <div class="camera-list-container">
    <div class="layout-wrapper">
      <!-- 左侧门店筛选器 -->
      <StoreFilter v-model="currentStoreId" @change="handleStoreChange" />

      <!-- 右侧摄像头列表 -->
      <div class="table-box">
        <ProTable
          :key="$i18n.locale.value"
          ref="proTable"
          :title="t('camera.cameraList')"
          row-key="id"
          :columns="columns"
          :request-api="getTableList"
          :data-callback="dataCallback"
          :request-error="error => handleError(error, t('camera.loadListFailed'))"
          :pagination="true"
          :request-auto="false"
        >
          <!-- 表格 header 按钮 -->
          <template #tableHeader>
            <el-button type="primary" :icon="CirclePlus" @click="openDrawer('新增')"> {{ t("camera.addCamera") }} </el-button>
            <el-button type="success" :icon="Setting" @click="openBrandDrawer"> {{ t("camera.brandManagement") }} </el-button>
          </template>

          <!-- 摄像头类型 -->
          <template #type="scope">
            <el-tag :type="scope.row.type === 'nvr' ? 'success' : 'primary'">
              {{ scope.row.type === "nvr" ? "NVR" : "摄像头" }}
            </el-tag>
          </template>

          <!-- 通道信息 -->
          <template #channels="scope">
            <div class="channels-display">
              <div class="channel-stats">
                <span class="total">{{ t("camera.totalChannels") }}: {{ scope.row.channel_count || 0 }}</span>
                <span class="active">{{ t("camera.availableChannels") }}: {{ scope.row.active_channel_count || 0 }}</span>
              </div>
            </div>
          </template>

          <!-- 摄像头操作 -->
          <template #operation="scope">
            <div class="operation-buttons">
              <el-tooltip :content="t('camera.viewCameraDetail')" placement="top">
                <el-button type="info" link :icon="View" @click="openViewDialog(scope.row)" size="small">
                  {{ t("camera.view") }}
                </el-button>
              </el-tooltip>

              <el-tooltip :content="t('camera.editCameraInfo')" placement="top">
                <el-button type="primary" link :icon="EditPen" @click="openDrawer('编辑', scope.row)" size="small">
                  {{ t("camera.edit") }}
                </el-button>
              </el-tooltip>

              <el-tooltip :content="t('camera.manageChannel')" placement="top">
                <el-button type="success" link :icon="Setting" @click="openChannelDrawer(scope.row)" size="small">
                  {{ t("camera.channel") }}
                </el-button>
              </el-tooltip>

              <el-tooltip :content="t('camera.deleteCamera')" placement="top">
                <el-button type="danger" link @click="handleDelete(scope.row)" size="small">
                  <el-icon><Delete /></el-icon>
                  {{ t("camera.delete") }}
                </el-button>
              </el-tooltip>
            </div>
          </template>
        </ProTable>
      </div>
    </div>

    <!-- 新增/编辑摄像头抽屉 -->
    <CameraDrawer ref="drawerRef" />

    <!-- 通道管理抽屉 -->
    <ChannelDrawer ref="channelDrawerRef" />

    <!-- 品牌管理抽屉 -->
    <CameraBrandDrawer ref="brandDrawerRef" />

    <!-- 查看摄像头弹框 -->
    <el-dialog
      v-model="viewDialogVisible"
      :title="t('camera.cameraDetail')"
      :width="dialogWidth"
      :close-on-click-modal="false"
      :destroy-on-close="true"
      :center="false"
      :align-center="true"
      class="camera-detail-dialog"
    >
      <div v-if="currentCamera.id" class="camera-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item :label="t('camera.cameraId')">{{ currentCamera.id }}</el-descriptions-item>
          <el-descriptions-item :label="t('camera.ip')">{{ currentCamera.ip }}</el-descriptions-item>
          <el-descriptions-item :label="t('camera.account')">{{ currentCamera.user }}</el-descriptions-item>
          <el-descriptions-item :label="t('camera.password')">{{ currentCamera.pwd }}</el-descriptions-item>
          <el-descriptions-item :label="t('camera.brand')">{{ currentCamera.brand_name || "-" }}</el-descriptions-item>
          <el-descriptions-item :label="t('camera.type')">
            <el-tag :type="currentCamera.type === 'nvr' ? 'success' : 'primary'">
              {{ currentCamera.type === "nvr" ? "NVR" : t("camera.type") }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item :label="t('camera.store')">{{ currentCamera.store_name || "-" }}</el-descriptions-item>
          <el-descriptions-item :label="t('device.province')">{{ currentCamera.province_name || "-" }}</el-descriptions-item>
          <el-descriptions-item :label="t('device.city')">{{ currentCamera.city_name || "-" }}</el-descriptions-item>
          <el-descriptions-item :label="t('device.district')">{{ currentCamera.district_name || "-" }}</el-descriptions-item>
          <el-descriptions-item :label="t('camera.channelCount')" :span="2">
            {{ currentCamera.channel_count || 0 }} 个通道 (可用: {{ currentCamera.active_channel_count || 0 }})
          </el-descriptions-item>
        </el-descriptions>

        <!-- 通道详情 -->
        <div class="channels-section">
          <h4>{{ t("camera.channelDetail") }}</h4>
          <div v-if="currentCamera.channels && currentCamera.channels.length > 0" class="channels-list">
            <div v-for="(channel, index) in currentCamera.channels" :key="index" class="channel-item">
              <div class="channel-header">
                <span class="channel-name">{{ t("camera.channelNumber") }}</span>
                <el-tag :type="channel.status === 1 ? 'success' : 'danger'" size="small">
                  {{ channel.status === 1 ? t("camera.available") : t("camera.unavailable") }}
                </el-tag>
              </div>
              <div v-if="channel.image" class="channel-image">
                <img :src="channel.image" alt="通道截图" />
              </div>
            </div>
          </div>
          <div v-else class="no-data">{{ t("camera.noChannelInfo") }}</div>
        </div>
      </div>

      <template #footer>
        <el-button @click="viewDialogVisible = false">{{ t("camera.close") }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, nextTick } from "vue";
import { useI18n } from "vue-i18n";
import { ElMessage, ElMessageBox } from "element-plus";
import { EditPen, CirclePlus, View, Delete, Setting } from "@element-plus/icons-vue";
import ProTable from "@/components/ProTable/index.vue";
import { ProTableInstance } from "@/components/ProTable/interface";
import StoreFilter from "@/components/StoreFilter/index.vue";
import { getCameraList, saveCamera, updateCamera, deleteCamera } from "@/api/modules/camera";
import { type CameraInfo, type CameraSaveParams, type StoreInfo } from "@/api/model/cameraModel";
import { getAllCameraBrands } from "@/api/modules/cameraBrand";
import { getStoreList } from "@/api/modules/store";
import CameraDrawer from "./components/camera/CameraDrawer.vue";
import ChannelDrawer from "./components/camera/ChannelDrawer.vue";
import CameraBrandDrawer from "./components/common/CameraBrandDrawer.vue";

// 国际化
const { t } = useI18n();

// 响应式数据
const drawerRef = ref();
const channelDrawerRef = ref();
const brandDrawerRef = ref();

// ProTable 实例
const proTable = ref<ProTableInstance>();

// 门店选择相关
const currentStoreId = ref<number | null>(null);
const storeList = ref<StoreInfo[]>([]); // 用于新增/编辑弹框

// 品牌选择相关
const brandList = ref<any[]>([]);

// 查看弹框相关
const viewDialogVisible = ref(false);
const currentCamera = ref<CameraInfo>({} as CameraInfo);

// 计算弹框宽度 - 自适应
const dialogWidth = computed(() => {
  const windowWidth = window.innerWidth;
  if (windowWidth <= 768) {
    return "95%";
  } else if (windowWidth <= 1024) {
    return "80%";
  } else if (windowWidth <= 1440) {
    return "70%";
  } else {
    return "min(1200px, 60%)";
  }
});

// 处理门店选择变化
const handleStoreChange = (store: StoreInfo | null) => {
  if (store) {
    currentStoreId.value = store.id;
    // 触发表格刷新
    if (proTable.value) {
      proTable.value.searchParam = {
        ...proTable.value.searchParam,
        store_id: store.id
      };
      proTable.value.getTableList();
    }
  }
};

// 表格列定义
const columns = computed(() => [
  { prop: "id", label: t("camera.id"), width: 50 },
  {
    prop: "ip",
    label: t("camera.ip"),
    width: 180,
    search: { el: "input" as any, props: { placeholder: t("camera.inputCameraIp") } }
  },
  { prop: "user", label: t("camera.user"), width: 100 },
  {
    prop: "brand_id",
    label: t("camera.brand"),
    width: 100,
    enum: brandList,
    fieldNames: { label: "label", value: "value" },
    search: {
      el: "select" as any,
      key: "brand_id",
      props: {
        placeholder: t("camera.selectBrand"),
        clearable: true
      },
      fieldNames: { label: "label", value: "value" }
    }
  },
  { prop: "type", label: t("camera.type"), width: 100 },
  { prop: "channels", label: t("camera.channels"), width: 300 },
  { prop: "store_name", label: t("camera.store") },
  { prop: "operation", label: t("camera.operation"), width: 250, fixed: "right" }
]);

// 加载门店列表（用于新增/编辑弹框）
const loadStoreList = async () => {
  try {
    const response = await getStoreList({ page: 1, limit: 1000 });
    storeList.value = response.data.records || [];
  } catch (error) {
    handleError(error, "加载门店列表失败");
  }
};

// 加载品牌列表
const loadBrandList = async () => {
  try {
    const response = await getAllCameraBrands();
    const brands = response.data || response || [];
    // 确保数据结构符合ProTable enum的要求
    brandList.value = brands.map(brand => ({
      label: brand.name,
      value: brand.id,
      ...brand
    }));
  } catch (error) {
    handleError(error, "加载品牌列表失败");
  }
};

// 统一错误处理
const handleError = (error: any, defaultMessage: string = "操作失败") => {
  console.error("操作失败:", error);
  const errorMessage = error?.response?.data?.message || error?.message || defaultMessage;
  ElMessage.error(errorMessage);
};

// 获取摄像头列表
const getTableList = (params: any) => {
  const queryParams: any = {
    pageNum: params.pageNum,
    pageSize: params.pageSize
  };

  // 如果有选中的门店，传递门店ID
  if (currentStoreId.value) {
    queryParams.store_id = currentStoreId.value;
  }

  // 如果有IP，传递IP
  if (params.ip) {
    queryParams.ip = params.ip;
  }

  // 如果有品牌ID，传递品牌ID
  if (params.brand_id) {
    queryParams.brand_id = params.brand_id;
  }

  return getCameraList(queryParams);
};

// dataCallback 是对于返回的表格数据做处理
const dataCallback = (data: any) => {
  // 如果返回的是数组，直接使用
  if (Array.isArray(data)) {
    return {
      records: data,
      total: data.length
    };
  }
  // 如果返回的是对象，使用 records 和 total
  return {
    records: data.records || [],
    total: data.total || 0
  };
};

// 打开查看弹框
const openViewDialog = (row: CameraInfo) => {
  currentCamera.value = { ...row };
  viewDialogVisible.value = true;
};

// 打开抽屉
const openDrawer = (title: string, row: CameraInfo = {} as CameraInfo) => {
  const params = {
    title,
    row: { ...row },
    api: title === "新增" ? saveCamera : (data: CameraSaveParams) => updateCamera(row.id, data),
    getTableList: async () => {
      if (proTable.value) {
        await proTable.value.getTableList();
      }
    },
    storeList: storeList.value,
    currentStoreId: currentStoreId.value
  };

  drawerRef.value?.acceptParams(params);
};

// 打开通道管理抽屉
const openChannelDrawer = (row: CameraInfo) => {
  const params = {
    cameraInfo: row,
    getTableList: async () => {
      if (proTable.value) {
        await proTable.value.getTableList();
      }
    }
  };
  channelDrawerRef.value?.acceptParams(params);
};

// 打开品牌管理抽屉
const openBrandDrawer = () => {
  brandDrawerRef.value?.openDrawer();
};

// 删除摄像头
const handleDelete = (row: CameraInfo) => {
  ElMessageBox.confirm("确定要删除该摄像头吗？", "提示", {
    type: "warning"
  })
    .then(async () => {
      try {
        await deleteCamera(row.id);
        ElMessage.success("删除成功");

        // 刷新门店列表
        await loadStoreList();
        if (proTable.value) {
          await proTable.value.getTableList();
        }
      } catch (error) {
        handleError(error, "删除失败");
      }
    })
    .catch(() => {
      // 用户取消删除
    });
};

// 组件挂载时初始化
onMounted(() => {
  // 延迟加载门店列表（用于新增/编辑弹框），避免与 StoreFilter 的自动加载冲突
  nextTick(() => {
    setTimeout(() => {
      loadStoreList();
    }, 100);
  });

  // 加载品牌列表
  loadBrandList();
});
</script>

<style scoped lang="scss">
@import "@/styles/table-optimization.scss";

.camera-list-container {
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
</style>
