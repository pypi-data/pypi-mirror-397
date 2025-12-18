<template>
  <el-drawer v-model="drawerVisible" title="未绑定设备列表" :size="1000" :close-on-click-modal="false" :destroy-on-close="true">
    <div class="unbound-devices-content">
      <!-- 搜索区域 -->
      <div class="search-area">
        <el-input
          v-model="searchForm.name"
          placeholder="请输入设备名称"
          style="width: 200px; margin-right: 10px"
          clearable
          @keyup.enter="handleSearch"
        />
        <el-input
          v-model="searchForm.sn"
          placeholder="请输入序列号"
          style="width: 200px; margin-right: 10px"
          clearable
          @keyup.enter="handleSearch"
        />
        <el-button type="primary" @click="handleSearch">搜索</el-button>
        <el-button @click="handleReset">重置</el-button>
      </div>

      <!-- 未绑定设备表格 -->
      <el-table :data="unboundDevicesList" v-loading="loading" style="width: 100%; margin-top: 20px" :row-key="row => row.id">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="设备名称" width="150" show-overflow-tooltip />
        <el-table-column prop="sn" label="序列号" width="200" show-overflow-tooltip />
        <el-table-column prop="device_type" label="设备类型" width="100" />
        <el-table-column prop="cpu" label="CPU" width="120" show-overflow-tooltip />
        <el-table-column prop="mem" label="内存" width="100" />
        <el-table-column prop="os" label="系统" width="120" show-overflow-tooltip />
        <el-table-column prop="created" label="创建时间" width="150" />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="scope">
            <el-button type="primary" size="small" @click="handleBindToStore(scope.row)"> 绑定门店 </el-button>
          </template>
        </el-table-column>
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

    <template #footer>
      <div class="drawer-footer">
        <el-button @click="drawerVisible = false">关闭</el-button>
      </div>
    </template>
  </el-drawer>

  <!-- 门店选择弹框 -->
  <StoreSelectionDialog ref="storeSelectionDialogRef" @confirm="handleStoreSelectionConfirm" />
</template>

<script setup lang="ts">
import { ref, reactive } from "vue";
import { ElMessage } from "element-plus";
import { getTerminalList, bindDeviceToStore, type TerminalInfo, type TerminalListParams } from "@/api/modules/device";
import StoreSelectionDialog from "../common/StoreSelectionDialog.vue";

// 定义事件
const emit = defineEmits<{
  refresh: [];
}>();

// 响应式数据
const drawerVisible = ref(false);
const loading = ref(false);
const storeSelectionDialogRef = ref();

// 搜索表单
const searchForm = reactive({
  name: "",
  sn: ""
});

// 未绑定设备列表
const unboundDevicesList = ref<TerminalInfo[]>([]);

// 分页信息
const pagination = reactive({
  pageNum: 1,
  pageSize: 10,
  total: 0
});

// 当前选中的设备
const currentSelectedDevice = ref<TerminalInfo | null>(null);

// 获取未绑定设备列表
const getUnboundDevicesList = async () => {
  loading.value = true;
  try {
    const params: TerminalListParams = {
      page: pagination.pageNum,
      limit: pagination.pageSize,
      name: searchForm.name,
      sn: searchForm.sn
    };

    const response = await getTerminalList(params);

    // 根据API返回的数据结构，数据在data字段中
    let data;
    if (response.code !== undefined) {
      data = response.data;
    } else {
      data = response;
    }

    // 直接使用返回的数据，因为 /device/terminal/list 接口已经返回未绑定的设备
    unboundDevicesList.value = data.records || [];
    pagination.total = data.total || 0;
  } catch (error) {
    ElMessage.error("获取未绑定设备列表失败");
    console.error("获取未绑定设备列表失败:", error);
  } finally {
    loading.value = false;
  }
};

// 搜索
const handleSearch = () => {
  pagination.pageNum = 1;
  getUnboundDevicesList();
};

// 重置搜索
const handleReset = () => {
  searchForm.name = "";
  searchForm.sn = "";
  pagination.pageNum = 1;
  getUnboundDevicesList();
};

// 分页大小变化
const handleSizeChange = (size: number) => {
  pagination.pageSize = size;
  pagination.pageNum = 1;
  getUnboundDevicesList();
};

// 页码变化
const handleCurrentChange = (page: number) => {
  pagination.pageNum = page;
  getUnboundDevicesList();
};

// 绑定到门店
const handleBindToStore = (device: TerminalInfo) => {
  currentSelectedDevice.value = device;
  storeSelectionDialogRef.value?.open(device);
};

// 门店选择确认
const handleStoreSelectionConfirm = async (storeId: number) => {
  if (!currentSelectedDevice.value) {
    ElMessage.error("未选择设备");
    return;
  }

  try {
    await bindDeviceToStore({
      terminal_id: currentSelectedDevice.value.id,
      store_id: storeId
    });

    ElMessage.success("设备绑定到门店成功");

    // 刷新未绑定设备列表
    await getUnboundDevicesList();

    // 通知父组件刷新设备列表
    emit("refresh");

    // 关闭门店选择弹框
    storeSelectionDialogRef.value?.close();
  } catch (error) {
    ElMessage.error("绑定失败");
    console.error("绑定设备到门店失败:", error);
  }
};

// 打开抽屉
const open = () => {
  drawerVisible.value = true;

  // 重置数据
  searchForm.name = "";
  searchForm.sn = "";
  pagination.pageNum = 1;
  pagination.pageSize = 10;
  currentSelectedDevice.value = null;

  // 加载未绑定设备列表
  getUnboundDevicesList();
};

// 暴露方法
defineExpose({
  open
});
</script>

<style scoped lang="scss">
.unbound-devices-content {
  padding: 20px;
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

.drawer-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

:deep(.el-drawer__body) {
  padding: 0;
}

:deep(.el-table) {
  .el-table__row {
    transition: background-color 0.2s ease;
  }

  .el-table__row:hover {
    background-color: #f0f9ff !important;
  }
}
</style>
