<template>
  <el-drawer
    v-model="drawerVisible"
    :title="drawerTitle"
    :size="drawerSize"
    :close-on-click-modal="false"
    :destroy-on-close="true"
    class="camera-drawer"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px" class="camera-form">
      <!-- 基本信息 -->
      <el-card class="form-card" shadow="never">
        <template #header>
          <div class="card-header">
            <span>基本信息</span>
          </div>
        </template>

        <el-form-item label="所属门店" prop="store_id">
          <el-select
            v-model="form.store_id"
            placeholder="请选择门店"
            filterable
            remote
            :remote-method="searchStores"
            :loading="storeLoading"
            style="width: 100%"
            @change="handleStoreChange"
            @focus="handleStoreFocus"
            no-data-text="暂无门店数据"
            no-match-text="未找到匹配的门店"
          >
            <el-option v-for="store in storeOptions" :key="store.id" :label="store.name" :value="store.id">
              <span style="float: left">{{ store.name }}</span>
              <span style="float: right; color: #8492a6; font-size: 13px">{{ store.address || "暂无地址" }}</span>
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="IP地址" prop="ip">
          <el-input v-model="form.ip" placeholder="请输入IP地址" />
        </el-form-item>

        <el-form-item label="账号" prop="user">
          <el-input v-model="form.user" placeholder="请输入账号" />
        </el-form-item>

        <el-form-item label="密码" prop="pwd">
          <el-input v-model="form.pwd" type="text" placeholder="请输入密码" />
        </el-form-item>

        <el-form-item label="品牌" prop="brand_id">
          <el-select
            v-model="form.brand_id"
            placeholder="请选择品牌"
            filterable
            clearable
            remote
            :remote-method="searchBrands"
            :loading="brandLoading"
            style="width: 100%"
            @change="handleBrandChange"
            @focus="handleBrandFocus"
            :filter-method="filterBrands"
            no-data-text="暂无品牌数据"
            no-match-text="未找到匹配的品牌"
          >
            <el-option
              v-for="brand in filteredBrandOptions"
              :key="brand.id"
              :label="brand.name"
              :value="brand.id"
              :disabled="false"
            >
              <span style="float: left">{{ brand.name }}</span>
              <span style="float: right; color: #8492a6; font-size: 13px">ID: {{ brand.id }}</span>
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="类型" prop="type">
          <el-radio-group v-model="form.type" @change="handleTypeChange">
            <el-radio label="nvr">NVR</el-radio>
            <el-radio label="camera">摄像头</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-card>
    </el-form>

    <template #footer>
      <div class="drawer-footer">
        <el-button @click="drawerVisible = false" :disabled="submitLoading">
          <el-icon><Close /></el-icon>
          取消
        </el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit" :disabled="submitLoading">
          <el-icon v-if="!submitLoading"><Check /></el-icon>
          {{ submitLoading ? "保存中..." : form.id ? "更新" : "确定" }}
        </el-button>
      </div>
    </template>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from "vue";
import { ElMessage, FormInstance, FormRules } from "element-plus";
import { Close, Check } from "@element-plus/icons-vue";
import type { CameraInfo, CameraSaveParams, CameraBrandInfo } from "@/api/modules/camera";
import type { StoreInfo } from "@/api/modules/store";
import { getAllCameraBrands } from "@/api/modules/cameraBrand";

// 组件属性
interface Props {
  title: string;
  row: CameraInfo;
  api: (data: CameraSaveParams) => Promise<any>;
  getTableList: () => Promise<void>;
  storeList: StoreInfo[];
  currentStoreId?: number | null;
}

// 响应式数据
const drawerVisible = ref(false);
const formRef = ref<FormInstance>();
const submitLoading = ref(false);
const storeLoading = ref(false);
const brandLoading = ref(false);
const brandLoaded = ref(false); // 添加品牌加载状态标记
const brandSearchKeyword = ref(""); // 品牌搜索关键词
const storeOptions = ref<StoreInfo[]>([]);
const brandOptions = ref<CameraBrandInfo[]>([]);
const filteredBrandOptions = ref<CameraBrandInfo[]>([]);
const drawerTitle = ref("新增摄像头"); // 添加抽屉标题响应式变量

// 表单数据
const form = reactive<CameraSaveParams & { id?: number }>({
  id: undefined, // 添加id字段用于判断是新增还是编辑
  store_id: null, // 使用null作为默认值，避免显示0
  ip: "",
  user: "",
  pwd: "",
  brand_id: undefined, // 使用undefined作为默认值
  type: "camera"
});

// 表单验证规则
const rules: FormRules = {
  store_id: [
    {
      required: true,
      message: "请选择门店",
      trigger: "change",
      validator: (rule, value, callback) => {
        if (!value || value === null) {
          callback(new Error("请选择门店"));
          return;
        }
        callback();
      }
    }
  ],
  ip: [
    { required: true, message: "请输入IP地址", trigger: "blur" },
    {
      validator: (rule, value, callback) => {
        if (value) {
          // 支持IP地址和端口号格式：192.168.1.1 或 192.168.1.1:8080
          const ipWithPortPattern = /^(\d{1,3}\.){3}\d{1,3}(:\d{1,5})?$/;

          if (!ipWithPortPattern.test(value)) {
            callback(new Error("请输入正确的IP地址格式（如：192.168.1.1 或 192.168.1.1:8080）"));
            return;
          }

          // 分离IP地址和端口号
          const [ip, port] = value.split(":");

          // 验证IP地址部分
          const parts = ip.split(".");
          for (const part of parts) {
            const num = parseInt(part, 10);
            if (num < 0 || num > 255) {
              callback(new Error("IP地址每个段必须在0-255之间"));
              return;
            }
          }

          // 验证端口号部分（如果存在）
          if (port) {
            const portNum = parseInt(port, 10);
            if (portNum < 1 || portNum > 65535) {
              callback(new Error("端口号必须在1-65535之间"));
              return;
            }
          }
        }
        callback();
      },
      trigger: "blur"
    }
  ],
  user: [
    { required: true, message: "请输入账号", trigger: "blur" },
    { min: 1, max: 50, message: "账号长度应在1-50个字符之间", trigger: "blur" }
  ],
  pwd: [
    { required: true, message: "请输入密码", trigger: "blur" },
    { min: 1, max: 50, message: "密码长度应在1-50个字符之间", trigger: "blur" }
  ],
  brand_id: [
    {
      required: true,
      message: "请选择品牌",
      trigger: "change",
      validator: (rule, value, callback) => {
        if (!value || value === null || value === 0) {
          callback(new Error("请选择品牌"));
          return;
        }
        callback();
      }
    }
  ],
  type: [
    { required: true, message: "请选择类型", trigger: "change" },
    {
      validator: (rule, value, callback) => {
        if (!["camera", "nvr"].includes(value)) {
          callback(new Error("请选择有效的设备类型"));
          return;
        }
        callback();
      },
      trigger: "change"
    }
  ]
};

// 计算属性 - 移除原来的drawerTitle计算属性，使用响应式变量

const drawerSize = computed(() => {
  const windowWidth = window.innerWidth;
  if (windowWidth <= 768) {
    return "100%";
  } else if (windowWidth <= 1024) {
    return "80%";
  } else {
    return "60%";
  }
});

// 监听类型变化
const handleTypeChange = () => {
  // 类型变化时不需要处理通道逻辑
};

// 统一错误处理
const handleError = (error: any, defaultMessage: string = "操作失败") => {
  const errorMessage = error?.response?.data?.message || error?.message || defaultMessage;
  ElMessage.error(errorMessage);
};

// 搜索门店
const searchStores = (query: string) => {
  if (!query) {
    storeOptions.value = props.storeList || [];
    return;
  }

  storeLoading.value = true;
  try {
    // 从传入的门店列表中搜索
    storeOptions.value = (props.storeList || []).filter(
      store =>
        store.name.toLowerCase().includes(query.toLowerCase()) ||
        (store.address && store.address.toLowerCase().includes(query.toLowerCase()))
    );
  } catch {
    ElMessage.error("搜索门店失败");
  } finally {
    storeLoading.value = false;
  }
};

// 处理门店选择变化
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const handleStoreChange = (storeId: number) => {
  // 门店选择变化处理
};

// 处理门店下拉框获得焦点
const handleStoreFocus = () => {
  if (storeOptions.value.length === 0 && !storeLoading.value) {
    // 如果门店列表为空且没有在加载，重新加载门店列表
    storeOptions.value = props.storeList || [];
  }
};

// 处理品牌选择变化
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const handleBrandChange = (brandId: number) => {
  // 品牌选择变化处理
};

// 处理品牌下拉框获得焦点
const handleBrandFocus = () => {
  if (brandOptions.value.length === 0 && !brandLoading.value) {
    loadBrandList();
  }
};

// 品牌搜索方法
const searchBrands = (query: string) => {
  brandSearchKeyword.value = query;
  filterBrands();
};

// 品牌过滤方法
const filterBrands = () => {
  if (!brandSearchKeyword.value.trim()) {
    filteredBrandOptions.value = brandOptions.value;
  } else {
    const keyword = brandSearchKeyword.value.toLowerCase();
    filteredBrandOptions.value = brandOptions.value.filter(brand => brand.name.toLowerCase().includes(keyword));
  }
};

// 设置默认门店
const setDefaultStore = () => {
  // 如果当前没有选择门店且门店列表不为空，可以选择第一个门店作为默认值
  if (!form.store_id && storeOptions.value.length > 0) {
    // 这里可以根据业务需求设置默认门店
    // 比如选择第一个门店，或者根据某种规则选择
    // 暂时不设置默认值，让用户主动选择
  }
};

// 设置默认品牌
const setDefaultBrand = () => {
  // 如果当前没有选择品牌且品牌列表不为空，可以选择第一个品牌作为默认值
  if (!form.brand_id && brandOptions.value.length > 0) {
    // 这里可以根据业务需求设置默认品牌
    // 比如选择第一个品牌，或者根据某种规则选择
    // 暂时不设置默认值，让用户主动选择
  }
};

// 加载品牌列表
const loadBrandList = async () => {
  // 如果正在加载或已经加载过，直接返回
  if (brandLoading.value || brandLoaded.value) {
    return;
  }

  try {
    brandLoading.value = true;
    const response = await getAllCameraBrands();
    // 确保数据结构正确
    brandOptions.value = response.data || response || [];
    filteredBrandOptions.value = brandOptions.value; // 初始化过滤后的选项
    brandLoaded.value = true; // 标记为已加载

    // 设置默认品牌
    setDefaultBrand();
  } catch (error: any) {
    // 如果是请求被取消的错误，不显示错误消息
    if (error?.name === "CanceledError" || error?.code === "ERR_CANCELED") {
      return;
    }
    ElMessage.error("加载品牌列表失败");
  } finally {
    brandLoading.value = false;
  }
};

// 重置表单
const resetForm = () => {
  // 重置id字段
  form.id = undefined;
  // 如果有当前选中的门店，自动选中，否则设为null让用户选择
  form.store_id = props.currentStoreId || null;
  form.ip = "";
  form.user = "";
  form.pwd = "";
  form.brand_id = undefined; // 重置为undefined，让用户主动选择
  form.type = "camera";

  // 初始化门店选项
  storeOptions.value = props.storeList || [];

  // 设置默认门店
  setDefaultStore();

  if (formRef.value) {
    formRef.value.resetFields();
  }
};

// 填充表单数据
const fillForm = (data: CameraInfo) => {
  form.id = data.id; // 设置id字段用于判断是新增还是编辑
  form.store_id = data.store_id || null; // 编辑时使用实际的store_id，如果没有则设为null
  form.ip = data.ip;
  form.user = data.user;
  form.pwd = data.pwd;
  form.brand_id = data.brand_id || undefined; // 编辑时使用实际的brand_id，如果没有则设为undefined
  form.type = data.type;

  // 初始化门店选项
  storeOptions.value = props.storeList || [];
};

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return;

  try {
    await formRef.value.validate();

    submitLoading.value = true;

    // 准备提交数据 - 只包含摄像头基本信息
    const submitData: CameraSaveParams = {
      store_id: Number(form.store_id),
      ip: String(form.ip).trim(),
      user: String(form.user).trim(),
      pwd: String(form.pwd).trim(),
      brand_id: form.brand_id ? Number(form.brand_id) : undefined,
      type: form.type
    };

    await props.api(submitData);

    ElMessage.success(form.id ? "更新成功" : "新增成功");
    drawerVisible.value = false;

    // 刷新表格数据
    await props.getTableList();
  } catch (error) {
    handleError(error, "操作失败");
  } finally {
    submitLoading.value = false;
  }
};

// 组件属性
let props: Props;

// 接受参数
const acceptParams = (params: Props) => {
  props = params;

  // 设置抽屉标题
  drawerTitle.value = params.title || "新增摄像头";

  // 初始化门店选项
  storeOptions.value = params.storeList || [];

  // 如果品牌列表未加载，加载品牌列表
  if (!brandLoaded.value) {
    loadBrandList();
  }

  // 重置表单
  resetForm();

  // 如果是编辑模式，填充数据
  if (params.row && params.row.id) {
    fillForm(params.row);
  }

  // 显示抽屉
  drawerVisible.value = true;
};

// 组件初始化时不立即加载品牌数据，避免CanceledError

// 暴露方法
defineExpose({
  acceptParams
});
</script>

<style scoped lang="scss">
.camera-drawer {
  :deep(.el-drawer__body) {
    padding: 20px;
    overflow-y: auto;
  }
}

.camera-form {
  .form-card {
    margin-bottom: 20px;
    border: 1px solid #e4e7ed;
    border-radius: 8px;

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-weight: 600;
      color: #303133;

      .channel-tip {
        font-size: 12px;
        color: #909399;
        font-weight: normal;
      }
    }
  }

  // 优化下拉菜单选项样式
  :deep(.el-select-dropdown__item) {
    height: auto;
    line-height: 1.4;
    padding: 8px 20px;

    &:hover {
      background-color: #f5f7fa;
    }

    &.is-selected {
      background-color: #ecf5ff;
      color: #409eff;
    }
  }

  // 优化表单项样式
  .el-form-item {
    margin-bottom: 20px;

    .el-form-item__label {
      font-weight: 500;
      color: #303133;
    }

    .el-form-item__content {
      .el-input,
      .el-select {
        .el-input__wrapper {
          border-radius: 6px;
          transition: all 0.3s;

          &:hover {
            border-color: #c0c4cc;
          }

          &.is-focus {
            border-color: #409eff;
            box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.1);
          }
        }
      }
    }
  }
}

.drawer-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px;
  border-top: 1px solid #e4e7ed;
  background-color: #fafafa;

  .el-button {
    min-width: 80px;

    .el-icon {
      margin-right: 4px;
    }
  }
}

/* 响应式布局 */
@media (max-width: 768px) {
  .camera-drawer {
    :deep(.el-drawer) {
      width: 100% !important;
    }

    :deep(.el-drawer__body) {
      padding: 15px;
    }
  }

  .camera-form {
    .form-card {
      margin-bottom: 15px;
    }
  }

  .drawer-footer {
    padding: 15px;
    flex-direction: column;

    .el-button {
      width: 100%;
    }
  }
}
</style>
