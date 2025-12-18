<template>
  <div class="inference-config-container">
    <div class="layout-wrapper">
      <!-- 左侧门店筛选器 -->
      <StoreFilter v-model="currentStoreId" @change="handleStoreChange" />

      <!-- 右侧表格 -->
      <div class="table-box">
        <ProTable
          ref="proTable"
          :title="t('inference.configList')"
          row-key="id"
          :columns="columns"
          :request-api="getTableList"
          :data-callback="dataCallback"
          :request-error="error => handleError(error, t('inference.getConfigListFailed'))"
          :pagination="true"
          :request-auto="false"
        >
          <!-- 表格 header 按钮 -->
          <template #tableHeader>
            <el-button v-if="!currentStoreHasConfig" type="primary" :icon="CirclePlus" @click="openAddDialog">
              {{ t("inference.addConfig") }}
            </el-button>
          </template>
          <!-- 配置内容预览 -->
          <template #content="scope">
            <div class="content-preview">
              <span class="content-text">{{
                scope.row.content.length > 50 ? scope.row.content.substring(0, 50) + "..." : scope.row.content
              }}</span>
            </div>
          </template>

          <!-- 操作按钮 -->
          <template #operation="scope">
            <div class="operation-buttons">
              <el-tooltip :content="t('inference.viewConfig')" placement="top">
                <el-button type="info" link :icon="View" @click="openViewDialog(scope.row)" size="small">
                  {{ t("inference.view") }}
                </el-button>
              </el-tooltip>

              <el-tooltip :content="t('inference.updateConfig')" placement="top">
                <el-button type="primary" link :icon="Edit" @click="openUpdateDialog(scope.row)" size="small">
                  {{ t("inference.update") }}
                </el-button>
              </el-tooltip>

              <el-tooltip :content="t('inference.deleteConfig')" placement="top">
                <el-button type="danger" link @click="handleDelete(scope.row)" size="small">
                  <el-icon><Delete /></el-icon>
                  {{ t("inference.delete") }}
                </el-button>
              </el-tooltip>
            </div>
          </template>
        </ProTable>
      </div>
    </div>

    <!-- 查看配置抽屉 -->
    <el-drawer
      v-model="viewDialogVisible"
      :title="t('inference.configDetail')"
      :size="drawerSize"
      :close-on-click-modal="false"
      :destroy-on-close="true"
      direction="rtl"
      class="inference-config-view-drawer"
    >
      <div v-if="currentConfig.id" class="config-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item :label="t('inference.configId')">{{ currentConfig.id }}</el-descriptions-item>
          <el-descriptions-item :label="t('inference.storeName')">{{ currentConfig.store_name || "-" }}</el-descriptions-item>
          <el-descriptions-item :label="t('inference.version')">{{ currentConfig.version || "-" }}</el-descriptions-item>
          <el-descriptions-item :label="t('inference.created')" :span="2">{{
            currentConfig.created || "-"
          }}</el-descriptions-item>
        </el-descriptions>

        <!-- 配置内容详情 -->
        <div class="content-section">
          <JsonViewer
            :content="currentConfig.content || ''"
            :title="t('inference.configContent')"
            :height="'calc(100vh - 400px)'"
            :show-stats="true"
            :show-actions="true"
            :show-expand-all="true"
            :show-collapse-all="true"
            :show-copy="true"
            :show-download="true"
            :download-file-name="`inference-config-${currentConfig.version || 'config'}.json`"
          />
        </div>
      </div>

      <template #footer>
        <div class="drawer-footer">
          <el-button @click="viewDialogVisible = false">{{ t("inference.close") }}</el-button>
        </div>
      </template>
    </el-drawer>

    <!-- 新增配置弹框组件 -->
    <AddInferenceConfigDialog
      v-model:visible="addDialogVisible"
      :store-list="storeList"
      :default-store-id="currentStoreId"
      @success="handleAddSuccess"
    />

    <!-- 更新配置组件 -->
    <UpdateInferenceConfigDialog
      v-model:visible="updateDialogVisible"
      :update-config="updateConfig"
      @success="handleUpdateSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, nextTick } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { View, Delete, CirclePlus, Edit } from "@element-plus/icons-vue";
import { useI18n } from "vue-i18n";
import ProTable from "@/components/ProTable/index.vue";
import { ColumnProps, ProTableInstance } from "@/components/ProTable/interface";
import StoreFilter from "@/components/StoreFilter/index.vue";
import { getInferenceConfigList, deleteInferenceConfig } from "./api/inference.api";
import { type InferenceConfigInfo, type StoreInfo } from "./types/inference.types";
import { getStoreList } from "@/api/modules/store";
import { AddInferenceConfigDialog, UpdateInferenceConfigDialog } from "./components";
import JsonViewer from "@/components/JsonViewer/index.vue";

const { t } = useI18n();

// ProTable 实例
const proTable = ref<ProTableInstance>();

// 门店选择相关
const storeList = ref<StoreInfo[]>([]);
const currentStoreId = ref<number | null>(null);

// 查看弹框相关
const viewDialogVisible = ref(false);
const currentConfig = ref<InferenceConfigInfo>({} as InferenceConfigInfo);

// 新增配置相关
const addDialogVisible = ref(false);
const currentStoreHasConfig = ref(false);

// 更新配置相关
const updateDialogVisible = ref(false);
const updateConfig = ref<InferenceConfigInfo>({} as InferenceConfigInfo);

// 计算抽屉宽度 - 自适应
const drawerSize = computed(() => {
  const windowWidth = window.innerWidth;
  if (windowWidth <= 768) return "90%";
  if (windowWidth <= 1024) return "60%";
  if (windowWidth <= 1440) return "50%";
  return "40%";
});

// 表格列定义 - 使用 computed 确保语言切换时能够响应更新
const columns = computed<ColumnProps<InferenceConfigInfo>[]>(() => [
  { prop: "id", label: t("inference.id"), width: 80 },
  { prop: "store_name", label: t("inference.store"), width: 150 },
  { prop: "content", label: t("inference.content"), minWidth: 200 },
  {
    prop: "version",
    label: t("inference.version"),
    width: 120,
    search: { el: "input", props: { placeholder: t("inference.versionPlaceholder") } }
  },
  { prop: "created", label: t("inference.created"), width: 200 },
  {
    prop: "modified",
    label: t("inference.modified"),
    width: 200,
    render: (scope: any) => {
      return scope.row.modified ? scope.row.modified : "---";
    }
  },
  { prop: "operation", label: t("inference.operation"), width: 230, fixed: "right" }
]);

// 加载门店列表（用于新增配置弹框）
const loadStoreList = async () => {
  try {
    const response = await getStoreList({ page: 1, limit: 1000 });
    storeList.value = response.data.records || [];
  } catch (error) {
    handleError(error, "加载门店列表失败");
  }
};

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

// 检查门店是否已有配置
const checkStoreHasConfig = async (storeId: number) => {
  try {
    const response = await getInferenceConfigList({ store_id: storeId, page: 1, limit: 1 });
    currentStoreHasConfig.value = response.data.records && response.data.records.length > 0;
  } catch (error) {
    console.error("检查门店配置状态失败:", error);
    currentStoreHasConfig.value = false;
  }
};

// 统一错误处理
const handleError = (error: any, defaultMessage?: string) => {
  console.error("操作失败:", error);
  const errorMessage = error?.response?.data?.message || error?.message || defaultMessage || t("inference.getConfigListFailed");
  ElMessage.error(errorMessage);
};

// 获取推理配置列表
const getTableList = (params: any) => {
  const queryParams: any = {
    pageNum: params.pageNum,
    pageSize: params.pageSize
  };

  // 如果有选中的门店，传递门店ID
  if (currentStoreId.value) {
    queryParams.store_id = currentStoreId.value;
  }

  // 如果有版本号，传递版本号
  if (params.version) {
    queryParams.version = params.version;
  }

  return getInferenceConfigList(queryParams);
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
const openViewDialog = (row: InferenceConfigInfo) => {
  currentConfig.value = { ...row };
  viewDialogVisible.value = true;
};

// 删除配置
const handleDelete = (row: InferenceConfigInfo) => {
  ElMessageBox.confirm(t("inference.deleteConfirm"), t("common.tip"), {
    type: "warning"
  })
    .then(async () => {
      try {
        await deleteInferenceConfig(row.id);
        ElMessage.success(t("inference.deleteSuccess"));

        // 刷新门店列表
        await loadStoreList();
        if (proTable.value) {
          await proTable.value.getTableList();
        }

        // 更新当前门店配置状态
        if (currentStoreId.value) {
          await checkStoreHasConfig(currentStoreId.value);
        }
      } catch (error) {
        handleError(error, t("inference.deleteFailed"));
      }
    })
    .catch(() => {
      // 用户取消删除
    });
};

// 处理更新配置成功
const handleUpdateSuccess = async () => {
  // 刷新表格数据
  if (proTable.value) {
    await proTable.value.getTableList();
  }

  // 刷新门店列表
  await loadStoreList();

  // 更新当前门店配置状态
  if (currentStoreId.value) {
    await checkStoreHasConfig(currentStoreId.value);
  }
};

// 打开新增配置弹框
const openAddDialog = () => {
  addDialogVisible.value = true;
};

// 打开更新配置抽屉
const openUpdateDialog = (row: InferenceConfigInfo) => {
  updateConfig.value = { ...row };
  updateDialogVisible.value = true;
};

// 处理新增配置成功
const handleAddSuccess = async () => {
  // 刷新表格数据
  if (proTable.value) {
    await proTable.value.getTableList();
  }

  // 刷新门店列表
  await loadStoreList();

  // 更新当前门店配置状态
  if (currentStoreId.value) {
    await checkStoreHasConfig(currentStoreId.value);
  }
};

// 组件挂载时初始化
onMounted(() => {
  // 延迟加载门店列表（用于新增配置弹框），避免与 StoreFilter 的自动加载冲突
  nextTick(() => {
    setTimeout(() => {
      loadStoreList();
    }, 100);
  });
});
</script>

<style scoped lang="scss">
@import "@/styles/table-optimization.scss";

.inference-config-container {
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

.content-preview {
  .content-text {
    font-family: "Courier New", monospace;
    font-size: 12px;
    color: #606266;
    word-break: break-all;
  }
}

.operation-buttons {
  display: flex;
  gap: 8px;
}

.config-detail {
  .content-section {
    margin-top: 20px;
  }
}

// 抽屉样式
.inference-config-view-drawer {
  .drawer-footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    padding: 16px 0;
    border-top: 1px solid #e4e7ed;
    margin-top: 20px;
  }
}
</style>
