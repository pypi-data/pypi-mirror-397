<script setup lang="ts">
import { ref, onUnmounted } from "vue";
import { ElMessage, FormInstance } from "element-plus";
import { Plus, Delete, InfoFilled } from "@element-plus/icons-vue";
import {
  getUnboundStores,
  type StoreInfo,
  type DeviceListParams,
  type DeviceInfo,
  type DeviceSaveParams
} from "@/api/modules/device";

interface DrawerProps {
  title: string;
  isView: boolean;
  row: Partial<DeviceInfo>;
  api?: (params: DeviceSaveParams) => Promise<any>;
  getTableList?: (operationType?: string) => void;
}

// 网络配置接口
export interface NetworkConfig {
  name: string;
  ip: string;
  ip_type: "IPv4" | "IPv6";
  mac?: string;
}

// 门店选项接口
export interface StoreOption {
  value: number;
  label: string;
}

const drawerVisible = ref(false);

const drawerProps = ref<DrawerProps>({
  isView: false,
  title: "",
  row: {}
});

// 门店选项
const storeOptions = ref<StoreOption[]>([]);

// 生成32位随机字符串
const generateRandomString = (length: number = 32): string => {
  const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
  return Array.from({ length }, () => chars.charAt(Math.floor(Math.random() * chars.length))).join("");
};

// 处理网络配置数据格式
const processNetworkData = (network: any): NetworkConfig[] => {
  if (!network) return [];

  if (typeof network === "string") {
    try {
      const parsed = JSON.parse(network);
      return Array.isArray(parsed)
        ? parsed.map(net => ({
            name: net.name || "",
            ip: net.ip || "",
            ip_type: net.ip_type || "IPv4",
            mac: net.mac || ""
          }))
        : [];
    } catch {
      // 如果解析失败，按换行符分割
      const networks = network.split("\n").filter(net => net.trim());
      return networks.map(net => {
        const parts = net.split(":");
        return {
          name: parts[0]?.trim() || "",
          ip: parts[1]?.trim() || "",
          ip_type: "IPv4",
          mac: parts[2]?.trim() || ""
        };
      });
    }
  }

  if (Array.isArray(network)) {
    return network.map(net => ({
      name: net.name || "",
      ip: net.ip || "",
      ip_type: net.ip_type || "IPv4",
      mac: net.mac || ""
    }));
  }

  return [];
};

// 接收父组件传过来的参数
const acceptParams = (params: DrawerProps) => {
  // 参数验证
  if (!params) {
    console.error("Invalid params passed to acceptParams");
    ElMessage.error("参数错误");
    return;
  }

  // 重置表单数据，确保每次打开都使用新的数据
  const rowData = params.row ? { ...params.row } : {};

  // 如果是新增操作，自动生成序列号
  if (params.title === "新增" && !rowData.sn) {
    rowData.sn = "TM-" + generateRandomString(32);
  }

  // 处理网络配置数据格式
  rowData.network = processNetworkData(rowData.network);

  drawerProps.value = {
    isView: params.isView || false,
    title: params.title || "",
    row: rowData,
    api: params.api,
    getTableList: params.getTableList
  };

  drawerVisible.value = true;

  // 加载门店数据
  loadStoreData();
};

// 处理API响应数据
const processApiResponse = (response: any) => {
  return response.code !== undefined ? response.data : response;
};

// 格式化门店标签
const formatStoreLabel = (store: StoreInfo): string => {
  const location = [store.province_name, store.city_name, store.district_name].filter(Boolean).join("");
  return `${store.name}${location ? ` (${location})` : ""}`;
};

// 加载门店数据
const loadStoreData = async () => {
  try {
    if (drawerProps.value.title === "新增") {
      // 新增时只加载未绑定的门店
      const params: DeviceListParams = { page: 1, limit: 1000 };
      const response = await getUnboundStores(params);
      const data = processApiResponse(response);

      storeOptions.value = data.records.map((store: StoreInfo) => ({
        value: store.id,
        label: formatStoreLabel(store)
      }));
    } else {
      // 编辑时，如果设备已有门店，显示当前门店；否则显示未绑定门店
      if (drawerProps.value.row.store_id) {
        // 设备已有门店，显示当前门店信息
        storeOptions.value = [
          {
            value: drawerProps.value.row.store_id,
            label: formatStoreLabel({
              id: drawerProps.value.row.store_id,
              name: drawerProps.value.row.store_name || "未知门店",
              province_name: drawerProps.value.row.province_name,
              city_name: drawerProps.value.row.city_name,
              district_name: drawerProps.value.row.district_name
            } as StoreInfo)
          }
        ];
      } else {
        // 设备没有门店，加载未绑定门店
        const params: DeviceListParams = { page: 1, limit: 1000 };
        const response = await getUnboundStores(params);
        const data = processApiResponse(response);

        storeOptions.value = data.records.map((store: StoreInfo) => ({
          value: store.id,
          label: formatStoreLabel(store)
        }));
      }
    }
  } catch (error) {
    ElMessage.error("加载门店数据失败");
    console.error("加载门店数据失败:", error);
  }
};

// 组件卸载时清理资源
onUnmounted(() => {
  // 清理全局回调函数
  (window as any).initDrawerMapCallback = undefined;
});

// 添加表单验证规则
const rules = ref({
  name: [{ required: true, message: "请填写设备名称" }],
  sn: [{ required: true, message: "请填写设备序列号" }],
  store_id: [{ required: true, message: "请选择所属门店" }]
  // 网络配置改为非必填
});

// 表单实例引用
const ruleFormRef = ref<FormInstance>();

// 防止重复提交的标志
const isSubmitting = ref(false);

// 构造提交数据
const buildFormData = (): DeviceSaveParams => {
  const row = drawerProps.value.row;
  return {
    name: row?.name || "",
    sn: row?.sn || "",
    store_id: row?.store_id || 0,
    cpu: row?.cpu || "",
    mem: row?.mem || "",
    os: row?.os || "",
    gpu: row?.gpu || "",
    npu: row?.npu || "",
    network: row?.network || []
  };
};

// 提交数据（新增/编辑）
const handleSubmit = () => {
  if (isSubmitting.value) {
    return;
  }

  // 确保表单引用存在
  if (!ruleFormRef.value) {
    console.error("Form reference is not available");
    ElMessage.error("表单引用不可用");
    return;
  }

  ruleFormRef.value.validate(async valid => {
    if (!valid) return;

    // 验证网络配置
    if (!validateNetworkConfig()) {
      return;
    }

    // 确保drawerProps的值存在
    if (!drawerProps.value) {
      console.error("Drawer props is not available");
      ElMessage.error("操作失败，数据异常");
      return;
    }

    // 确保API函数存在
    if (!drawerProps.value.api) {
      ElMessage.error("API函数未定义，操作失败");
      return;
    }

    isSubmitting.value = true;
    try {
      // 构造提交数据
      const formData = buildFormData();

      // 调用API
      await drawerProps.value.api(formData);

      // 关闭抽屉
      drawerVisible.value = false;

      // 刷新表格数据
      if (drawerProps.value.getTableList) {
        drawerProps.value.getTableList(drawerProps.value.title);
      }
    } catch (error) {
      console.error(error);
      ElMessage.error("操作失败");
    } finally {
      isSubmitting.value = false;
    }
  });
};

// 添加网络配置
const addNetwork = () => {
  if (!drawerProps.value.row.network) {
    drawerProps.value.row.network = [];
  }
  drawerProps.value.row.network.push({
    name: "",
    ip: "",
    ip_type: "IPv4" as const,
    mac: ""
  });
};

// 删除网络配置
const removeNetwork = (index: number) => {
  if (drawerProps.value.row.network && drawerProps.value.row.network.length > 0) {
    drawerProps.value.row.network.splice(index, 1);
  }
};

// 验证网络配置
const validateNetworkConfig = (): boolean => {
  const networks = drawerProps.value.row.network || [];
  for (const net of networks) {
    if (net.name && !net.ip) {
      ElMessage.warning("请填写完整的网络配置信息");
      return false;
    }
    if (net.ip && !net.name) {
      ElMessage.warning("请填写完整的网络配置信息");
      return false;
    }
  }
  return true;
};

// 重新生成序列号
const regenerateSn = () => {
  if (drawerProps.value?.title === "新增") {
    drawerProps.value.row.sn = "TM-" + generateRandomString(32);
    ElMessage.success("序列号已重新生成");
  }
};

// 关闭抽屉
const closeDrawer = () => {
  drawerVisible.value = false;
  isSubmitting.value = false;
};

defineExpose({
  acceptParams
});
</script>

<template>
  <el-drawer v-model="drawerVisible" :destroy-on-close="true" size="800px" :title="`${drawerProps?.title || ''}设备`">
    <el-form
      ref="ruleFormRef"
      label-width="100px"
      label-suffix=" :"
      :rules="rules"
      :disabled="drawerProps?.isView"
      :model="drawerProps?.row"
      :hide-required-asterisk="drawerProps?.isView"
    >
      <el-form-item label="设备名称" prop="name">
        <el-input v-model="drawerProps.row.name" placeholder="请填写设备名称" clearable></el-input>
      </el-form-item>

      <el-form-item label="序列号" prop="sn">
        <el-input
          v-model="drawerProps.row.sn"
          :placeholder="drawerProps?.title === '新增' ? '系统自动生成' : '请填写设备序列号'"
          :readonly="drawerProps?.title === '新增'"
          clearable
        >
          <template v-if="drawerProps?.title === '新增'" #suffix>
            <el-button type="primary" link @click="regenerateSn">重新生成</el-button>
          </template>
        </el-input>
      </el-form-item>

      <el-form-item label="所属门店" prop="store_id">
        <el-select
          v-model="drawerProps.row.store_id"
          placeholder="请选择所属门店"
          clearable
          filterable
          style="width: 100%"
          :disabled="drawerProps?.title === '编辑' || drawerProps?.isView"
        >
          <el-option v-for="store in storeOptions" :key="store.value" :label="store.label" :value="store.value" />
        </el-select>
        <div v-if="drawerProps?.title === '编辑'" class="form-tip">
          <el-icon><InfoFilled /></el-icon>
          <span>编辑时不能修改所属门店</span>
        </div>
      </el-form-item>

      <el-divider content-position="left">设备硬件信息</el-divider>

      <el-form-item label="CPU型号" prop="cpu">
        <el-input v-model="drawerProps.row.cpu" placeholder="请输入CPU型号" clearable />
      </el-form-item>

      <el-form-item label="内存" prop="mem">
        <el-input v-model="drawerProps.row.mem" placeholder="请输入内存信息" clearable />
      </el-form-item>

      <el-form-item label="操作系统" prop="os">
        <el-input v-model="drawerProps.row.os" placeholder="请输入操作系统" clearable />
      </el-form-item>

      <el-form-item label="GPU" prop="gpu">
        <el-input v-model="drawerProps.row.gpu" placeholder="请输入GPU信息" clearable />
      </el-form-item>

      <el-form-item label="NPU" prop="npu">
        <el-input v-model="drawerProps.row.npu" placeholder="请输入NPU信息" clearable />
      </el-form-item>

      <el-form-item label="网络配置">
        <div class="network-config-container">
          <div v-for="(net, index) in drawerProps.row.network" :key="index" class="network-item">
            <el-row :gutter="10" class="network-row">
              <el-col :span="3">
                <el-input v-model="net.name" placeholder="网络名称" />
              </el-col>
              <el-col :span="3">
                <el-select v-model="net.ip_type" placeholder="类型" style="width: 100%">
                  <el-option label="IPv4" value="IPv4" />
                  <el-option label="IPv6" value="IPv6" />
                </el-select>
              </el-col>
              <el-col :span="8">
                <el-input v-model="net.ip" placeholder="IP地址" />
              </el-col>
              <el-col :span="6">
                <el-input v-model="net.mac" placeholder="MAC地址" />
              </el-col>
              <el-col :span="4" class="delete-button-col">
                <el-button type="danger" :icon="Delete" @click="removeNetwork(index)" circle />
              </el-col>
            </el-row>
          </div>
          <div class="add-network-button">
            <el-button type="primary" :icon="Plus" @click="addNetwork">添加网络配置</el-button>
          </div>
        </div>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="closeDrawer">取消</el-button>
      <el-button v-show="!drawerProps?.isView" type="primary" @click="handleSubmit" :loading="isSubmitting">确定</el-button>
    </template>
  </el-drawer>
</template>

<style scoped lang="scss">
.network-config-container {
  width: 100%;
  min-width: 0; // 防止flex子项溢出

  .network-item {
    margin-bottom: 10px;
    border: 1px solid #e4e7ed;
    border-radius: 4px;
    background-color: #fafafa;
    padding-left: 5px;
    padding-top: 5px;
    padding-bottom: 5px;
    width: 100%;

    .el-row {
      width: 100%;
      margin: 0;
    }

    .el-col {
      padding: 0 2px;
    }
  }

  .network-item:last-child {
    margin-bottom: 15px;
  }

  .add-network-button {
    text-align: left;
    margin-top: 5px;
  }

  .network-row {
    align-items: center;
  }

  .delete-button-col {
    display: flex;
    justify-content: flex-end;
    align-items: center;
  }
}

.form-tip {
  display: flex;
  align-items: center;
  margin-top: 5px;
  color: #909399;
  font-size: 12px;

  .el-icon {
    margin-right: 4px;
  }
}
</style>
