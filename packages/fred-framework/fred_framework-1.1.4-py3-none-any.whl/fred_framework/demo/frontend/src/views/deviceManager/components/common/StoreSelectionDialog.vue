<template>
  <el-dialog
    v-model="dialogVisible"
    title="选择门店"
    :width="dialogWidth"
    :close-on-click-modal="false"
    :destroy-on-close="true"
    :center="false"
    :align-center="true"
    class="store-selection-dialog"
  >
    <div v-if="currentDevice.id" class="store-selection-content">
      <!-- 当前设备信息 -->
      <div class="current-device-info">
        <h4>当前设备信息</h4>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="设备ID">{{ currentDevice.id }}</el-descriptions-item>
          <el-descriptions-item label="设备名称">{{ currentDevice.name }}</el-descriptions-item>
          <el-descriptions-item label="序列号">{{ currentDevice.sn }}</el-descriptions-item>
          <el-descriptions-item label="设备类型">{{ currentDevice.device_type || "-" }}</el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- 门店列表 -->
      <div class="store-list">
        <h4>选择要绑定的门店</h4>
        <div class="selection-tip">
          <el-icon><InfoFilled /></el-icon>
          <span>点击任意行选中该门店进行绑定</span>
        </div>

        <!-- 搜索区域 -->
        <div class="search-area">
          <el-input
            v-model="searchForm.name"
            placeholder="请输入门店名称"
            style="width: 200px; margin-right: 10px"
            clearable
            @keyup.enter="handleSearch"
          />
          <el-input
            v-model="searchForm.address"
            placeholder="请输入门店地址"
            style="width: 200px; margin-right: 10px"
            clearable
            @keyup.enter="handleSearch"
          />
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </div>

        <!-- 门店表格 -->
        <el-table
          :data="storeList"
          v-loading="loading"
          @row-click="handleRowClick"
          highlight-current-row
          style="width: 100%; margin-top: 20px"
          title="点击选中该门店"
        >
          <el-table-column prop="id" label="ID" width="60" />
          <el-table-column prop="name" label="门店名称" width="150" show-overflow-tooltip />
          <el-table-column prop="address" label="门店地址" show-overflow-tooltip />
          <el-table-column prop="province_name" label="省份" width="100" />
          <el-table-column prop="city_name" label="城市" width="100" />
          <el-table-column prop="district_name" label="区县" width="100" />
          <el-table-column prop="created" label="创建时间" width="150" />
        </el-table>

        <!-- 分页 -->
        <div class="pagination-wrapper">
          <el-pagination
            v-model:current-page="pagination.pageNum"
            v-model:page-size="pagination.pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="pagination.total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="close">取消</el-button>
        <el-button type="primary" :disabled="!selectedStore" @click="handleConfirm">确认绑定</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from "vue";
import { ElMessage } from "element-plus";
import { InfoFilled } from "@element-plus/icons-vue";
import { getUnboundStores, type StoreInfo, type DeviceListParams, type TerminalInfo } from "@/api/modules/device";

// 定义事件
const emit = defineEmits<{
  confirm: [storeId: number];
  close: [];
}>();

// 响应式数据
const dialogVisible = ref(false);
const loading = ref(false);
const currentDevice = ref<TerminalInfo>({} as TerminalInfo);
const selectedStore = ref<StoreInfo | null>(null);

// 搜索表单接口
interface SearchForm {
  name: string;
  address: string;
}

// 搜索表单
const searchForm = reactive<SearchForm>({
  name: "",
  address: ""
});

// 门店列表
const storeList = ref<StoreInfo[]>([]);

// 分页信息接口
interface PaginationInfo {
  pageNum: number;
  pageSize: number;
  total: number;
}

// 分页信息
const pagination = reactive<PaginationInfo>({
  pageNum: 1,
  pageSize: 10,
  total: 0
});

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
    return "min(1000px, 60%)";
  }
});

// 处理API响应数据
const processApiResponse = (response: any) => {
  return response.code !== undefined ? response.data : response;
};

// 获取门店列表
const getStoreListData = async () => {
  loading.value = true;
  try {
    const params: DeviceListParams = {
      page: pagination.pageNum,
      limit: pagination.pageSize,
      name: searchForm.name,
      address: searchForm.address
    };

    const response = await getUnboundStores(params);
    const data = processApiResponse(response);

    storeList.value = data.records || [];
    pagination.total = data.total || 0;
  } catch (error) {
    ElMessage.error("获取门店列表失败");
    console.error("获取门店列表失败:", error);
  } finally {
    loading.value = false;
  }
};

// 搜索
const handleSearch = () => {
  pagination.pageNum = 1;
  getStoreListData();
};

// 重置搜索
const handleReset = () => {
  searchForm.name = "";
  searchForm.address = "";
  pagination.pageNum = 1;
  getStoreListData();
};

// 分页大小变化
const handleSizeChange = (size: number) => {
  pagination.pageSize = size;
  pagination.pageNum = 1;
  getStoreListData();
};

// 页码变化
const handleCurrentChange = (page: number) => {
  pagination.pageNum = page;
  getStoreListData();
};

// 行点击处理
const handleRowClick = (row: StoreInfo) => {
  selectedStore.value = row;
};

// 确认绑定
const handleConfirm = () => {
  if (!selectedStore.value) {
    ElMessage.warning("请选择要绑定的门店");
    return;
  }

  emit("confirm", selectedStore.value.id);
  close();
};

// 打开弹框
const open = (device: TerminalInfo) => {
  currentDevice.value = { ...device };
  selectedStore.value = null;
  dialogVisible.value = true;

  // 重置搜索条件
  resetSearchForm();

  // 加载门店列表
  getStoreListData();
};

// 关闭弹框
const close = () => {
  dialogVisible.value = false;
  selectedStore.value = null;
  emit("close");
};

// 重置搜索条件
const resetSearchForm = () => {
  searchForm.name = "";
  searchForm.address = "";
  pagination.pageNum = 1;
  pagination.pageSize = 10;
};

// 暴露方法
defineExpose({
  open,
  close
});
</script>

<style scoped lang="scss">
.store-selection-content {
  padding: 20px;
}

.current-device-info {
  margin-bottom: 30px;

  h4 {
    margin: 0 0 15px 0;
    color: #303133;
    font-size: 16px;
    font-weight: 600;
  }
}

.store-list {
  h4 {
    margin: 0 0 15px 0;
    color: #303133;
    font-size: 16px;
    font-weight: 600;
  }
}

.selection-tip {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 15px;
  padding: 8px 12px;
  background-color: #f0f9ff;
  border: 1px solid #bae6fd;
  border-radius: 6px;
  color: #0369a1;
  font-size: 13px;

  .el-icon {
    font-size: 14px;
  }
}

.search-area {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

:deep(.el-dialog__body) {
  padding: 0;
  max-height: 70vh;
  overflow-y: auto;
}

:deep(.el-table) {
  .el-table__row {
    cursor: pointer;
    transition: background-color 0.2s ease;
  }

  .el-table__row:hover {
    background-color: #f0f9ff !important;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  .el-table__row.current-row {
    background-color: #e6f7ff !important;
    border-left: 3px solid #1890ff;
  }

  .el-table__row.current-row:hover {
    background-color: #bae7ff !important;
  }
}

/* 响应式布局 */
@media (max-width: 768px) {
  .store-selection-content {
    padding: 15px;
  }

  .search-area {
    flex-direction: column;
    gap: 10px;
    align-items: stretch;

    .el-input {
      width: 100% !important;
      margin-right: 0 !important;
      margin-bottom: 10px;
    }
  }

  :deep(.el-dialog__body) {
    max-height: 60vh;
  }
}
</style>
