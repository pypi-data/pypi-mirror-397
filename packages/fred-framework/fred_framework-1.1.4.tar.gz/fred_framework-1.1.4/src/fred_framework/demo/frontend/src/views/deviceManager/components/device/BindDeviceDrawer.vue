<template>
  <el-drawer v-model="drawerVisible" title="选择终端设备" :size="800" :close-on-click-modal="false" :destroy-on-close="true">
    <div class="bind-drawer-content">
      <!-- 当前设备信息 -->
      <div class="current-device-info">
        <h4>当前设备信息</h4>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="设备ID">{{ currentDevice.id }}</el-descriptions-item>
          <el-descriptions-item label="设备名称">{{ currentDevice.name }}</el-descriptions-item>
          <el-descriptions-item label="序列号">{{ currentDevice.sn }}</el-descriptions-item>
          <el-descriptions-item label="所属门店">{{ currentDevice.store_name || "-" }}</el-descriptions-item>
          <el-descriptions-item label="省份">{{ currentDevice.province_name || "-" }}</el-descriptions-item>
          <el-descriptions-item label="城市">{{ currentDevice.city_name || "-" }}</el-descriptions-item>
          <el-descriptions-item label="区县">{{ currentDevice.district_name || "-" }}</el-descriptions-item>
          <el-descriptions-item label="绑定状态">
            <el-tag type="warning">未绑定</el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- 终端设备列表 -->
      <div class="terminal-list">
        <h4>选择要绑定的终端设备 (共 {{ pagination.total }} 条)</h4>
        <div class="selection-tip">
          <el-icon><InfoFilled /></el-icon>
          <span>点击任意行选中该终端设备</span>
        </div>

        <!-- 搜索区域 -->
        <div class="search-area">
          <el-input
            v-model="searchForm.sn"
            placeholder="请输入终端设备序列号"
            style="width: 300px; margin-right: 10px"
            clearable
            @keyup.enter="handleSearch"
          />
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </div>

        <!-- 调试信息 -->
        <div v-if="terminalList.length === 0 && !loading" style="text-align: center; padding: 20px; color: #999">
          暂无终端设备数据
        </div>

        <!-- 终端设备表格 -->
        <el-table
          :data="terminalList"
          v-loading="loading"
          @row-click="handleRowClick"
          highlight-current-row
          style="width: 100%; margin-top: 20px"
          title="点击选中该设备"
        >
          <el-table-column prop="id" label="ID" width="60" />
          <el-table-column prop="name" label="设备名称" width="150" show-overflow-tooltip />
          <el-table-column prop="sn" label="序列号" width="200">
            <template #default="scope">
              <span :title="scope.row.sn">{{ formatSerialNumber(scope.row.sn) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="device_type" label="设备类型" width="100" />
          <el-table-column prop="cpu" label="CPU" width="120" show-overflow-tooltip />
          <el-table-column prop="mem" label="内存" width="100" />
          <el-table-column prop="os" label="系统" width="120" show-overflow-tooltip />
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
      <div class="drawer-footer">
        <el-button @click="drawerVisible = false">取消</el-button>
        <el-button type="primary" :disabled="!selectedTerminal" @click="handleBind"> 确认绑定 </el-button>
      </div>
    </template>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, reactive } from "vue";
import { ElMessage } from "element-plus";
import { InfoFilled } from "@element-plus/icons-vue";
import { getTerminalList, type TerminalInfo, type DeviceInfo } from "@/api/modules/device";

// 响应式数据
const drawerVisible = ref(false);
const loading = ref(false);
const currentDevice = ref<DeviceInfo>({} as DeviceInfo);
const onBindCallback = ref<((terminalId: number) => Promise<void>) | null>(null);

// 搜索表单
const searchForm = reactive({
  sn: ""
});

// 终端设备列表
const terminalList = ref<TerminalInfo[]>([]);
const selectedTerminal = ref<TerminalInfo | null>(null);

// 分页信息
const pagination = reactive({
  pageNum: 1,
  pageSize: 10,
  total: 0
});

// 获取终端设备列表
const getTerminalListData = async () => {
  loading.value = true;
  try {
    const params = {
      page: pagination.pageNum,
      limit: pagination.pageSize,
      sn: searchForm.sn
    };

    const response = await getTerminalList(params);

    // 根据API返回的数据结构，数据在data字段中
    // 如果响应有code字段，说明是包装过的响应
    let data;
    if (response.code !== undefined) {
      data = response.data;
    } else {
      data = response;
    }

    terminalList.value = data.records || [];
    pagination.total = data.total || 0;
  } catch (error) {
    ElMessage.error("获取终端设备列表失败");
    console.error("获取终端设备列表失败:", error);
  } finally {
    loading.value = false;
  }
};

// 搜索
const handleSearch = () => {
  pagination.pageNum = 1;
  getTerminalListData();
};

// 重置搜索
const handleReset = () => {
  searchForm.sn = "";
  pagination.pageNum = 1;
  getTerminalListData();
};

// 分页大小变化
const handleSizeChange = (size: number) => {
  pagination.pageSize = size;
  pagination.pageNum = 1;
  getTerminalListData();
};

// 页码变化
const handleCurrentChange = (page: number) => {
  pagination.pageNum = page;
  getTerminalListData();
};

// 格式化序列号显示
const formatSerialNumber = (sn: string) => {
  if (!sn) return "";
  if (sn.length <= 10) return sn;
  return sn.substring(0, 4) + "..." + sn.substring(sn.length - 4);
};

// 行点击处理
const handleRowClick = (row: TerminalInfo) => {
  selectedTerminal.value = row;
};

// 确认绑定
const handleBind = async () => {
  if (!selectedTerminal.value) {
    ElMessage.warning("请选择要绑定的终端设备");
    return;
  }

  if (onBindCallback.value) {
    await onBindCallback.value(selectedTerminal.value.id);
    drawerVisible.value = false;
  }
};

// 接受参数
const acceptParams = (params: any) => {
  currentDevice.value = params.device;
  onBindCallback.value = params.onBind;
  drawerVisible.value = true;

  // 重置数据
  searchForm.sn = "";
  pagination.pageNum = 1;
  pagination.pageSize = 10;
  selectedTerminal.value = null;

  // 加载终端设备列表
  getTerminalListData();
};

// 暴露方法
defineExpose({
  acceptParams
});
</script>

<style scoped lang="scss">
.bind-drawer-content {
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

.terminal-list {
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
</style>
