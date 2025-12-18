<template>
  <el-drawer
    v-model="dialogVisible"
    :title="t('inference.addConfigTitle')"
    :size="drawerSize"
    :close-on-click-modal="false"
    :destroy-on-close="true"
    direction="rtl"
    class="inference-config-add-drawer"
    @close="handleClose"
  >
    <!-- 无门店时的提示信息 -->
    <div v-if="availableStores.length === 0" class="no-stores-tip">
      <el-result icon="info" :title="t('inference.allStoreConfigured')" :sub-title="t('inference.allStoreConfiguredSubtitle')">
        <template #extra>
          <el-button type="primary" @click="handleCancel">{{ t("inference.cancel") }}</el-button>
        </template>
      </el-result>
    </div>

    <!-- 有门店时的表单 -->
    <el-form v-else ref="formRef" :model="form" :rules="formRules" label-width="100px" label-position="left">
      <el-form-item :label="t('inference.selectStore')" prop="store_id">
        <el-select
          v-model="form.store_id"
          :placeholder="t('inference.selectStorePlaceholder')"
          filterable
          clearable
          style="width: 100%"
          @change="handleStoreChange"
        >
          <el-option v-for="store in availableStores" :key="store.id" :label="store.name" :value="store.id" />
        </el-select>
      </el-form-item>

      <el-form-item :label="t('inference.version')" prop="version">
        <el-input v-model="form.version" :placeholder="t('inference.versionPlaceholder')" :disabled="!form.store_id" />
      </el-form-item>

      <el-form-item :label="t('inference.content')" prop="content">
        <div class="config-content-wrapper">
          <JsonViewer
            :content="form.content"
            :title="t('inference.configContent')"
            :height="'calc(100vh - 400px)'"
            :show-stats="true"
            :show-actions="true"
            :show-expand-all="true"
            :show-collapse-all="true"
            :show-copy="true"
            :show-download="true"
            :download-file-name="`inference-config-${form.version || 'config'}.json`"
          />
        </div>
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="drawer-footer">
        <el-button @click="handleCancel">{{ t("inference.cancel") }}</el-button>
        <el-button v-if="availableStores.length > 0" type="primary" @click="handleSave" :loading="loading">
          {{ t("inference.saveConfig") }}
        </el-button>
      </div>
    </template>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, computed, watch } from "vue";
import { ElMessage } from "element-plus";
import { useI18n } from "vue-i18n";
import { saveInferenceConfig, getStoresWithoutConfig, getLatestInferenceConfig } from "../api/inference.api";
import { type StoreInfo } from "../types/inference.types";
import JsonViewer from "@/components/JsonViewer/index.vue";

const { t } = useI18n();

// 类型定义
interface Props {
  visible: boolean;
  storeList: StoreInfo[];
  defaultStoreId?: number | null;
}

interface Emits {
  (e: "update:visible", value: boolean): void;
  (e: "success"): void;
}

// Props & Emits
const props = withDefaults(defineProps<Props>(), {
  visible: false,
  storeList: () => [],
  defaultStoreId: null
});

const emit = defineEmits<Emits>();

// 响应式数据
const formRef = ref();
const loading = ref(false);
const storesWithoutConfig = ref<StoreInfo[]>([]);

const form = ref({
  store_id: null as number | null,
  version: "",
  content: ""
});

// 表单验证规则
const formRules = computed(() => ({
  store_id: [{ required: true, message: t("inference.selectStorePlaceholder"), trigger: "change" }],
  version: [{ required: true, message: t("inference.versionPlaceholder"), trigger: "blur" }],
  content: [{ required: true, message: t("inference.content") + t("common.isRequired"), trigger: "blur" }]
}));

// 计算属性
const dialogVisible = computed({
  get: () => props.visible,
  set: value => emit("update:visible", value)
});

const drawerSize = computed(() => {
  const windowWidth = window.innerWidth;
  if (windowWidth <= 768) return "90%";
  if (windowWidth <= 1024) return "60%";
  if (windowWidth <= 1440) return "50%";
  return "40%";
});

const availableStores = computed(() => storesWithoutConfig.value);

// 监听器
watch(
  () => props.visible,
  async newVal => {
    if (newVal) {
      resetForm();
      await loadStoresWithoutConfig();

      if (props.defaultStoreId) {
        form.value.store_id = props.defaultStoreId;
        form.value.version = "1.0";
        // 只有在选择了门店时才加载配置
        await loadLatestConfig(props.defaultStoreId);
      }
    }
  }
);

// 方法
const resetForm = () => {
  form.value = {
    store_id: null,
    version: "",
    content: ""
  };
  if (formRef.value) {
    formRef.value.clearValidate();
  }
};

const handleStoreChange = async (storeId: number) => {
  if (storeId) {
    form.value.version = "1.0";
    await loadLatestConfig(storeId);
  } else {
    // 如果没有选择门店，清空配置内容
    form.value.content = "";
  }
};

const loadStoresWithoutConfig = async () => {
  try {
    const response = await getStoresWithoutConfig();
    storesWithoutConfig.value = (response.data || []) as StoreInfo[];
  } catch (error) {
    handleError(error, "加载门店列表失败");
  }
};

const loadLatestConfig = async (storeId: number) => {
  try {
    const response = await getLatestInferenceConfig(storeId);
    if (response.data) {
      // 从 content 字段读取配置内容
      const content = response.data.content;
      if (typeof content === "string") {
        form.value.content = content;
      } else if (typeof content === "object") {
        // 如果 content 是对象，转换为 JSON 字符串
        form.value.content = JSON.stringify(content, null, 2);
      } else {
        form.value.content = "";
      }

      // 从 version 字段读取版本号
      form.value.version = response.data.version || "1.0";
    } else {
      // 如果没有返回数据，则设置为空配置
      form.value.content = "";
      form.value.version = "1.0";
    }
  } catch (error) {
    // 如果获取最新配置失败，则设置为空配置
    console.warn("获取门店最新配置失败，设置为空配置:", error);
    form.value.content = "";
    form.value.version = "1.0";
  }
};

const handleSave = async () => {
  if (!formRef.value) return;

  try {
    await formRef.value.validate();

    if (!form.value.content) {
      ElMessage.warning(t("inference.content") + t("common.isRequired"));
      return;
    }

    // 验证/修正 JSON 格式：兼容 Python 字典风格（True/False/None）
    const ensureJsonString = (raw: string): string | null => {
      const prettyJson = (obj: any) => JSON.stringify(obj, null, 2);
      const tryParseJson = (text: string): string | null => {
        try {
          const obj = JSON.parse(text);
          return prettyJson(obj);
        } catch {
          return null;
        }
      };
      const tryParsePythonLike = (text: string): string | null => {
        try {
          const normalized = text
            .replace(/\bNone\b/g, "null")
            .replace(/\bTrue\b/g, "true")
            .replace(/\bFalse\b/g, "false");
          // 使用函数构造安全求值为 JS 对象字面量
          // 注意：这里仅在受信任的管理端环境使用
          // eslint-disable-next-line no-new-func
          const obj = new Function("return (" + normalized + ")")();
          return prettyJson(obj);
        } catch {
          return null;
        }
      };
      return tryParseJson(raw) ?? tryParsePythonLike(raw);
    };

    const normalizedContent = ensureJsonString(String(form.value.content).trim());
    if (!normalizedContent) {
      ElMessage.error(t("inference.contentFormatError"));
      return;
    }
    // 将内容替换为格式化后的合法 JSON，确保后端校验通过
    form.value.content = normalizedContent;

    loading.value = true;

    await saveInferenceConfig({
      store_id: form.value.store_id!,
      version: form.value.version,
      content: form.value.content
    });

    ElMessage.success(t("inference.saveSuccess"));
    emit("success");
    dialogVisible.value = false;
  } catch (error) {
    handleError(error, "保存配置失败");
  } finally {
    loading.value = false;
  }
};

const handleCancel = () => {
  dialogVisible.value = false;
};

const handleClose = () => {
  resetForm();
};

const handleError = (error: any, defaultMessage: string = "操作失败") => {
  console.error("操作失败:", error);
  const errorMessage = error?.response?.data?.message || error?.message || defaultMessage;
  ElMessage.error(errorMessage);
};
</script>

<style scoped lang="scss">
.inference-config-add-drawer {
  .drawer-footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    padding: 16px 0;
    border-top: 1px solid #e4e7ed;
    margin-top: 20px;
  }

  .no-stores-tip {
    padding: 40px 20px;
    text-align: center;

    .el-result {
      padding: 0;

      :deep(.el-result__icon) {
        font-size: 64px;
        color: #909399;
      }

      :deep(.el-result__title) {
        font-size: 18px;
        color: #303133;
        margin: 16px 0 8px;
      }

      :deep(.el-result__subtitle) {
        font-size: 14px;
        color: #606266;
        margin-bottom: 24px;
      }
    }
  }

  // 配置内容区域样式优化
  .config-content-wrapper {
    width: 100%;

    :deep(.json-viewer-wrapper) {
      width: 100%;

      .content-display {
        width: 100%;

        .json-viewer-container {
          width: 100%;
        }

        .empty-json {
          width: 100%;
          min-height: 300px;

          :deep(.el-empty) {
            width: 100%;

            .el-empty__description {
              color: #909399;
              font-size: 14px;
            }
          }
        }
      }
    }
  }
}
</style>
