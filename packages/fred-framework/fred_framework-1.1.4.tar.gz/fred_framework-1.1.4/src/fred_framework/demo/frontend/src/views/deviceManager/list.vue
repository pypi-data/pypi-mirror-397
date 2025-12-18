<template>
  <div class="device-list-container">
    <div class="layout-wrapper">
      <!-- 左侧树形筛选器 -->
      <TreeFilter
        ref="treeFilterRef"
        label="label"
        id="id"
        :title="t('device.title')"
        :request-api="loadTreeData"
        :default-value="currentNodeKey"
        @change="handleTreeFilterChange"
        :show-search="true"
      />

      <!-- 右侧设备列表 -->
      <div class="descriptions-box card table-container">
        <ProTable
          :key="locale"
          ref="proTable"
          :title="t('device.deviceList')"
          row-key="id"
          :columns="columns"
          :request-api="getTableList"
          :data-callback="dataCallback"
          :request-error="handleRequestError"
          :init-param="initParam"
          :pagination="true"
          :request-auto="false"
          :search-col="{ xs: 1, sm: 1, md: 2, lg: 3, xl: 4 }"
        >
          <!-- 表格 header 按钮 -->
          <template #tableHeader>
            <el-button type="primary" :icon="CirclePlus" @click="openDrawer('新增')"> {{ t("device.addDevice") }} </el-button>
            <el-button type="success" :icon="View" @click="openUnboundDevicesDrawer"> {{ t("device.viewUnbound") }} </el-button>
          </template>

          <!-- 绑定状态 -->
          <template #binding_status_text="scope">
            <el-tag :type="scope.row.binding_status === 1 ? 'success' : 'warning'">
              {{ scope.row.binding_status_text }}
            </el-tag>
          </template>

          <!-- 网络配置 -->
          <template #network="scope">
            <div
              v-if="scope.row.network && Array.isArray(scope.row.network) && scope.row.network.length > 0"
              class="network-display"
            >
              <div v-for="(net, index) in scope.row.network as NetworkInfo[]" :key="index" class="network-item">
                {{ net.name }}: {{ net.ip }} ({{ net.ip_type || "IPv4" }}){{ net.mac ? ` [${net.mac}]` : "" }}
              </div>
            </div>
            <span v-else>-</span>
          </template>

          <!-- 设备操作 -->
          <template #operation="scope">
            <div class="operation-buttons">
              <el-tooltip :content="t('device.viewDeviceDetail')" placement="top">
                <el-button type="info" link :icon="View" @click="openViewDialog(scope.row)" size="small">
                  {{ t("device.view") }}
                </el-button>
              </el-tooltip>

              <el-tooltip :content="t('device.editDeviceInfo')" placement="top">
                <el-button type="primary" link :icon="EditPen" @click="openDrawer('编辑', scope.row)" size="small">
                  {{ t("device.edit") }}
                </el-button>
              </el-tooltip>

              <el-tooltip v-if="scope.row.binding_status === 0" :content="t('device.bindDevice')" placement="top">
                <el-button type="success" link @click="openBindDrawer(scope.row)" size="small">
                  <el-icon><Link /></el-icon>
                  {{ t("device.bind") }}
                </el-button>
              </el-tooltip>

              <el-tooltip :content="t('device.deleteDevice')" placement="top">
                <el-button type="danger" link @click="handleDelete(scope.row)" size="small">
                  <el-icon><Delete /></el-icon>
                  {{ t("device.delete") }}
                </el-button>
              </el-tooltip>
            </div>
          </template>
        </ProTable>
      </div>
    </div>

    <!-- 新增/编辑设备抽屉 -->
    <DeviceDrawer ref="drawerRef" />

    <!-- 绑定设备抽屉 -->
    <BindDeviceDrawer ref="bindDrawerRef" />

    <!-- 未绑定设备抽屉 -->
    <UnboundDevicesDrawer ref="unboundDevicesDrawerRef" @refresh="handleRefreshDeviceList" />

    <!-- 查看设备弹框 -->
    <el-dialog
      v-model="viewDialogVisible"
      :title="t('device.deviceDetail')"
      :width="dialogWidth"
      :close-on-click-modal="false"
      :destroy-on-close="true"
      :center="false"
      :align-center="true"
      class="device-detail-dialog"
    >
      <div v-if="currentDevice.id" class="device-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item :label="t('device.id')">{{ currentDevice.id }}</el-descriptions-item>
          <el-descriptions-item :label="t('device.name')">{{ currentDevice.name }}</el-descriptions-item>
          <el-descriptions-item :label="t('device.sn')">{{ currentDevice.sn }}</el-descriptions-item>
          <el-descriptions-item :label="t('device.store')">{{ currentDevice.store_name || "-" }}</el-descriptions-item>
          <el-descriptions-item :label="t('device.province')">{{ currentDevice.province_name || "-" }}</el-descriptions-item>
          <el-descriptions-item :label="t('device.city')">{{ currentDevice.city_name || "-" }}</el-descriptions-item>
          <el-descriptions-item :label="t('device.district')">{{ currentDevice.district_name || "-" }}</el-descriptions-item>
          <el-descriptions-item :label="t('device.type')">{{ currentDevice.device_type || "-" }}</el-descriptions-item>
          <el-descriptions-item :label="t('device.os')">{{ currentDevice.os || "-" }}</el-descriptions-item>
          <el-descriptions-item :label="t('device.npu')">{{ currentDevice.npu || "-" }}</el-descriptions-item>
          <el-descriptions-item :label="t('device.created')" :span="2">{{ currentDevice.created || "-" }}</el-descriptions-item>
          <el-descriptions-item :label="t('device.modified')" :span="2">{{ currentDevice.modified || "-" }}</el-descriptions-item>
        </el-descriptions>

        <!-- CPU信息 -->
        <div class="info-section">
          <h4>{{ t("device.cpu") }}</h4>
          <div
            v-if="currentDevice.cpu_raw && Array.isArray(currentDevice.cpu_raw) && currentDevice.cpu_raw.length > 0"
            class="info-list"
          >
            <div v-for="(cpu, index) in currentDevice.cpu_raw" :key="index" class="info-item-detail">
              <div class="info-item-title">{{ cpu.model || "-" }}</div>
              <div class="info-item-content">
                <span v-if="cpu.physical_cores">{{ t("device.physicalCores") }}: {{ cpu.physical_cores }}</span>
                <span v-if="cpu.logical_cores">{{ t("device.logicalCores") }}: {{ cpu.logical_cores }}</span>
              </div>
            </div>
          </div>
          <div v-else-if="currentDevice.cpu" class="info-item-simple">{{ currentDevice.cpu }}</div>
          <div v-else class="no-data">{{ t("device.noData") }}</div>
        </div>

        <!-- 内存信息 -->
        <div class="info-section">
          <h4>{{ t("device.mem") }}</h4>
          <div v-if="currentDevice.mem" class="info-item-simple">{{ currentDevice.mem }}</div>
          <div v-else class="no-data">{{ t("device.noData") }}</div>
        </div>

        <!-- GPU信息 -->
        <div class="info-section">
          <h4>{{ t("device.gpu") }}</h4>
          <div
            v-if="currentDevice.gpu_raw && Array.isArray(currentDevice.gpu_raw) && currentDevice.gpu_raw.length > 0"
            class="info-list"
          >
            <div v-for="(gpu, index) in currentDevice.gpu_raw" :key="index" class="info-item-detail">
              <div class="info-item-title">{{ gpu.name || "-" }}</div>
              <div class="info-item-content">
                <span v-if="gpu.type">{{ t("device.gpuType") }}: {{ gpu.type }}</span>
                <span v-if="gpu.memory_mb">{{ t("device.memory") }}: {{ gpu.memory_mb }}MB</span>
                <span v-if="gpu.driver_version">{{ t("device.driverVersion") }}: {{ gpu.driver_version }}</span>
              </div>
            </div>
          </div>
          <div v-else-if="currentDevice.gpu" class="info-item-simple">{{ currentDevice.gpu }}</div>
          <div v-else class="no-data">{{ t("device.noData") }}</div>
        </div>

        <!-- 网络配置 -->
        <div class="network-section">
          <h4>{{ t("device.network") }}</h4>
          <div
            v-if="currentDevice.network && Array.isArray(currentDevice.network) && currentDevice.network.length > 0"
            class="network-list"
          >
            <div v-for="(net, index) in currentDevice.network as NetworkInfo[]" :key="index" class="network-item-detail">
              <div class="network-item-title">{{ net.name }}</div>
              <div class="network-item-content">
                <span>{{ t("device.ip") }}: {{ net.ip }}</span>
                <span>({{ net.ip_type || "IPv4" }})</span>
                <span v-if="net.mac">{{ t("device.mac") }}: {{ net.mac }}</span>
                <span v-if="net.is_physical !== undefined">
                  {{ t("device.physicalNetworkCard") }}: {{ net.is_physical ? t("device.yes") : t("device.no") }}
                </span>
              </div>
            </div>
          </div>
          <div v-else class="no-data">{{ t("device.noNetworkConfig") }}</div>
        </div>
      </div>

      <template #footer>
        <el-button @click="viewDialogVisible = false">{{ t("device.close") }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from "vue";
import { useI18n } from "vue-i18n";
import { ElMessage, ElMessageBox } from "element-plus";

// 国际化
const { t, locale } = useI18n();
import { EditPen, CirclePlus, View, Link, Delete } from "@element-plus/icons-vue";
import ProTable from "@/components/ProTable/index.vue";
import TreeFilter from "@/components/TreeFilter/index.vue";
import {
  getDeviceList,
  saveDevice,
  updateDevice,
  deleteDevice,
  bindDeviceToTerminal,
  type DeviceInfo,
  type DeviceListParams,
  type DeviceSaveParams,
  type NetworkInfo
} from "@/api/modules/device";
import { getRegionTree } from "@/api/modules/store";
import DeviceDrawer from "./components/device/DeviceDrawer.vue";
import BindDeviceDrawer from "./components/device/BindDeviceDrawer.vue";
import UnboundDevicesDrawer from "./components/device/UnboundDevicesDrawer.vue";

// 响应式数据
const currentNodeKey = ref<string>("");
const drawerRef = ref();
const bindDrawerRef = ref();
const unboundDevicesDrawerRef = ref();
const proTable = ref();
const treeFilterRef = ref();

// 查看弹框相关
const viewDialogVisible = ref(false);
const currentDevice = ref<DeviceInfo>({} as DeviceInfo);

// 计算弹框宽度 - 自适应
const dialogWidth = computed(() => {
  // 获取窗口宽度
  const windowWidth = window.innerWidth;

  // 根据屏幕宽度设置不同的弹框宽度
  if (windowWidth <= 768) {
    // 移动端：占满屏幕宽度，留出边距
    return "95%";
  } else if (windowWidth <= 1024) {
    // 平板端：适中宽度
    return "80%";
  } else if (windowWidth <= 1440) {
    // 小屏桌面：较大宽度
    return "70%";
  } else {
    // 大屏桌面：最大宽度限制，避免过宽
    return "min(1200px, 60%)";
  }
});

// 搜索防抖定时器
const searchTimeout = ref<ReturnType<typeof setTimeout> | null>(null);

// 窗口大小变化处理
const handleResize = () => {
  // 延迟执行，确保DOM更新完成
  setTimeout(() => {
    if (proTable.value) {
      // 触发表格重新计算尺寸
      proTable.value.getTableList();
    }
  }, 100);
};

// 搜索参数，用于联动树形选择
const initParam = ref<DeviceListParams>({
  province_id: undefined,
  city_id: undefined,
  district_id: undefined,
  store_id: undefined
});

// 表格列定义
const columns = computed(() => [
  { prop: "id", label: t("device.id"), width: 50 },
  {
    prop: "name",
    label: t("device.name"),
    width: 100,
    search: {
      el: "input",
      order: 1,
      props: { placeholder: t("device.inputDeviceName"), clearable: true }
    }
  },
  {
    prop: "sn",
    label: t("device.sn"),
    width: 350,
    search: {
      el: "input",
      order: 2,
      span: 2,
      props: { placeholder: t("device.inputDeviceSn"), clearable: true }
    }
  },
  { prop: "store_name", label: t("device.store") },
  { prop: "binding_status_text", label: t("device.bindingStatus"), width: 100 },
  { prop: "network", label: t("device.network"), width: 200, showOverflowTooltip: true },
  { prop: "created", label: t("device.created"), width: 200 },
  { prop: "modified", label: t("device.modified"), width: 200 },
  { prop: "operation", label: t("device.operation"), width: 250, fixed: "right" }
]);

// 加载树形数据（适配 TreeFilter 组件）
const loadTreeData = async () => {
  try {
    return await getRegionTree(true, "device"); // 请求带设备数量统计的数据
  } catch (error) {
    ElMessage.error(t("device.loadTreeFailed"));
    console.error("加载树形数据失败:", error);
    return { data: [] };
  }
};

// 处理 TreeFilter 组件的选择变化
const handleTreeFilterChange = (selectedId: string) => {
  currentNodeKey.value = selectedId;

  // 临时保存新的参数
  const newParams: Partial<DeviceListParams> = {};

  // 如果选择了 "全部" 选项，清空所有筛选条件
  if (!selectedId) {
    newParams.province_id = undefined;
    newParams.city_id = undefined;
    newParams.district_id = undefined;
    Object.assign(initParam.value, newParams);
    if (proTable.value) {
      proTable.value.getTableList();
    }
    return;
  }

  // 解析节点ID以提取省市区ID
  const idParts = selectedId.split("_");
  // 根据ID格式提取省市区ID
  // ID格式示例: country_1_province_2_city_3_district_4

  // 先清空所有参数
  newParams.province_id = undefined;
  newParams.city_id = undefined;
  newParams.district_id = undefined;

  // 根据选择的节点类型设置相应的参数
  for (let i = 0; i < idParts.length; i += 2) {
    const key = idParts[i];
    const value = parseInt(idParts[i + 1]);
    if (key === "province") {
      newParams.province_id = value;
      // 选择省份时，清空城市和区县参数
      newParams.city_id = undefined;
      newParams.district_id = undefined;
    } else if (key === "city") {
      newParams.city_id = value;
      // 选择城市时，清空区县参数
      newParams.district_id = undefined;
    } else if (key === "district") {
      newParams.district_id = value;
    }
  }

  // 更新搜索参数
  Object.assign(initParam.value, newParams);

  // 调试信息

  // 刷新表格数据
  if (proTable.value) {
    proTable.value.getTableList();
  }
};

// 处理请求错误
const handleRequestError = (error: any) => {
  console.error("请求设备列表失败:", error);
  ElMessage.error("获取设备列表失败");
};

// 获取表格数据
const getTableList = (params: DeviceListParams) => {
  // 添加防抖处理
  if (searchTimeout.value) {
    clearTimeout(searchTimeout.value);
  }

  return new Promise(resolve => {
    searchTimeout.value = setTimeout(async () => {
      try {
        const response = await getDeviceList(params);
        resolve(response);
      } catch (error) {
        console.error("获取设备列表失败:", error);
        ElMessage.error(t("device.loadListFailed"));
        resolve({ data: { records: [], total: 0, pageNum: 1, pageSize: 10 } });
      }
    }, 300); // 300ms防抖
  });
};

// 表格数据回调处理
const dataCallback = (data: any) => {
  return {
    ...data,
    records: data.records.map((item: DeviceInfo) => {
      return {
        ...item,
        // 确保所有必要字段存在
        id: item.id || 0,
        name: item.name || "",
        sn: item.sn || "",
        store_name: item.store_name || "",
        province_name: item.province_name || "",
        city_name: item.city_name || "",
        district_name: item.district_name || "",
        device_type: item.device_type || "",
        cpu: item.cpu || "",
        cpu_raw: item.cpu_raw || null,
        mem: item.mem || "",
        mem_raw: item.mem_raw || null,
        os: item.os || "",
        gpu: item.gpu || "",
        gpu_raw: item.gpu_raw || null,
        npu: item.npu || "",
        created: item.created || "",
        modified: item.modified || "",
        network: (item.network || []).map((net: any) => ({
          name: net.name || "",
          ip: net.ip || "",
          ip_type: net.ip_type || "IPv4",
          mac: net.mac || "",
          is_physical: net.is_physical
        })),
        binding_status: item.binding_status || 0,
        binding_status_text: item.binding_status_text || "未绑定"
      };
    })
  };
};

// 打开查看弹框
const openViewDialog = (row: DeviceInfo) => {
  currentDevice.value = { ...row };
  viewDialogVisible.value = true;
};

// 打开抽屉
const openDrawer = (title: string, row: DeviceInfo = {} as DeviceInfo) => {
  // 先加载最新的树形数据，确保传递给抽屉的是最新数据
  loadTreeData().then(treeData => {
    const params = {
      title,
      row: { ...row },
      api: title === "新增" ? saveDevice : (data: DeviceSaveParams) => updateDevice(row.id, data),
      getTableList: async (operationType?: string) => {
        // 新增操作后需要刷新树形数据和表格数据
        if (operationType === "新增") {
          await loadTreeData(); // 刷新树形数据
        }

        // 刷新表格数据
        if (proTable.value) {
          await proTable.value.getTableList();
        }
      },
      // 将树形数据传递给抽屉组件
      regionTreeData: treeData?.data || []
    };

    drawerRef.value?.acceptParams(params);
  });
};

// 打开绑定抽屉
const openBindDrawer = (row: DeviceInfo) => {
  const params = {
    device: { ...row },
    onBind: async (terminalId: number) => {
      try {
        await bindDeviceToTerminal({
          device_id: row.id,
          terminal_id: terminalId
        });
        ElMessage.success("绑定成功");

        // 刷新表格数据
        if (proTable.value) {
          await proTable.value.getTableList();
        }
      } catch (error) {
        ElMessage.error("绑定失败");
        console.error("绑定设备失败:", error);
      }
    }
  };

  bindDrawerRef.value?.acceptParams(params);
};

// 打开未绑定设备抽屉
const openUnboundDevicesDrawer = () => {
  unboundDevicesDrawerRef.value?.open();
};

// 刷新设备列表
const handleRefreshDeviceList = () => {
  if (proTable.value) {
    proTable.value.getTableList();
  }
};

// 删除设备
const handleDelete = (row: DeviceInfo) => {
  ElMessageBox.confirm(t("device.deleteConfirm"), t("common.confirmTitle"), {
    type: "warning"
  })
    .then(async () => {
      try {
        await deleteDevice({ id: row.id });
        ElMessage.success(t("device.deleteSuccess"));

        // 删除后刷新树形数据和表格数据
        await loadTreeData(); // 刷新树形数据

        // 刷新表格数据
        if (proTable.value) {
          await proTable.value.getTableList();
        }
      } catch (error) {
        ElMessage.error(t("device.deleteFailed"));
        console.error("删除设备失败:", error);
      }
    })
    .catch(() => {
      // 用户取消删除
    });
};

// 组件挂载时初始化
onMounted(() => {
  // 初始加载表格数据
  if (proTable.value) {
    proTable.value.getTableList();
  }

  // 添加窗口大小变化监听
  window.addEventListener("resize", handleResize);

  // 默认折叠全部树形节点
  setTimeout(() => {
    if (treeFilterRef.value?.treeRef?.value) {
      const nodes = treeFilterRef.value.treeRef.value.store.nodesMap;
      if (nodes) {
        for (const node in nodes) {
          if (nodes.hasOwnProperty(node)) {
            nodes[node].expanded = false;
          }
        }
      }
    }
  }, 100);
});

// 组件卸载时清理
onUnmounted(() => {
  if (searchTimeout.value) {
    clearTimeout(searchTimeout.value);
  }
  // 移除窗口大小变化监听
  window.removeEventListener("resize", handleResize);
});
</script>

<style scoped lang="scss">
@import "@/styles/table-optimization.scss";

.device-list-container {
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

.tree-filter-wrapper {
  width: 300px;
  flex-shrink: 0;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* 右侧表格区域样式 */
.table-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0; /* 防止flex子项溢出 */
  overflow: hidden;
}

// 确保搜索区域和表格区域之间有间距
:deep(.table-search) {
  margin-bottom: 20px !important;
}

/* TreeFilter组件内部样式调整 */
:deep(.card.filter) {
  margin-bottom: 0;
  border: none;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  height: 100%;
}

:deep(.tree-filter-content) {
  flex: 1;
  overflow-y: auto;
}

:deep(.el-table) {
  height: 100%;
  min-height: 400px;
}

/* 网络配置列样式优化 */
:deep(.el-table .cell) {
  line-height: 1.4;
  padding: 8px 12px;
}

/* 网络配置多行显示样式 */
.network-display {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.network-item {
  padding: 2px 6px;
  background-color: #f5f7fa;
  border-radius: 4px;
  font-size: 12px;
  line-height: 1.3;
  color: #606266;
  border: 1px solid #e4e7ed;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 表格行高优化，支持多行内容 */
:deep(.el-table__row) {
  height: auto;
  min-height: 40px;
}

:deep(.el-table__body tr td) {
  vertical-align: top;
  padding: 8px 12px;
}

/* 查看弹框样式 */
.device-detail-dialog {
  :deep(.el-dialog) {
    margin: 0 auto;
    max-height: 90vh;
    overflow-y: auto;
  }

  :deep(.el-dialog__body) {
    padding: 20px;
    max-height: calc(90vh - 120px);
    overflow-y: auto;
  }

  :deep(.el-dialog__header) {
    padding: 20px 20px 10px 20px;
    border-bottom: 1px solid #e4e7ed;
  }

  :deep(.el-dialog__footer) {
    padding: 10px 20px 20px 20px;
    border-top: 1px solid #e4e7ed;
  }
}

.device-detail {
  .info-section,
  .network-section {
    margin-top: 20px;

    h4 {
      margin: 0 0 10px 0;
      color: #303133;
      font-size: 14px;
      font-weight: 600;
    }
  }

  .info-list,
  .network-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .info-item-detail,
  .network-item-detail {
    padding: 10px 12px;
    background-color: #f5f7fa;
    border: 1px solid #e4e7ed;
    border-radius: 6px;
    font-size: 13px;
    color: #606266;
  }

  .info-item-title,
  .network-item-title {
    font-weight: 600;
    color: #303133;
    margin-bottom: 6px;
  }

  .info-item-content,
  .network-item-content {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    font-size: 12px;
    color: #606266;

    span {
      white-space: nowrap;
    }
  }

  .info-item-simple {
    padding: 8px 12px;
    background-color: #f5f7fa;
    border: 1px solid #e4e7ed;
    border-radius: 6px;
    font-size: 13px;
    color: #606266;
    word-break: break-all;
  }

  .no-data {
    color: #909399;
    font-style: italic;
    text-align: center;
    padding: 20px;
  }
}

/* 操作按钮样式 */
.operation-buttons {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
}

.operation-buttons .el-button {
  margin: 0;
  padding: 4px 8px;
  font-size: 12px;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.operation-buttons .el-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.operation-buttons .el-button--info:hover {
  background-color: #e6f7ff;
  color: #1890ff;
}

.operation-buttons .el-button--primary:hover {
  background-color: #e6f7ff;
  color: #1890ff;
}

.operation-buttons .el-button--success:hover {
  background-color: #f6ffed;
  color: #52c41a;
}

.operation-buttons .el-button--danger:hover {
  background-color: #fff2f0;
  color: #ff4d4f;
}

/* 响应式布局 */
@media (max-width: 768px) {
  .layout-wrapper {
    flex-direction: column;
  }

  .device-list-container {
    padding: 10px;
  }

  :deep(.el-table) {
    height: 100%;
    min-height: 300px;
  }

  /* 移动端弹框优化 */
  .device-detail-dialog {
    :deep(.el-dialog) {
      margin: 5vh auto;
      width: 95% !important;
      max-height: 90vh;
    }

    :deep(.el-dialog__body) {
      padding: 15px;
      max-height: calc(90vh - 100px);
    }

    :deep(.el-dialog__header) {
      padding: 15px 15px 10px 15px;
    }

    :deep(.el-dialog__footer) {
      padding: 10px 15px 15px 15px;
    }
  }

  /* 移动端设备详情内容优化 */
  .device-detail {
    :deep(.el-descriptions) {
      .el-descriptions__label {
        font-size: 12px;
        width: 80px;
      }

      .el-descriptions__content {
        font-size: 12px;
        word-break: break-all;
      }
    }
  }

  /* 移动端操作按钮优化 */
  .operation-buttons {
    flex-direction: column;
    gap: 2px;
  }

  .operation-buttons .el-button {
    width: 100%;
    justify-content: center;
    font-size: 11px;
    padding: 2px 4px;
  }
}
</style>
