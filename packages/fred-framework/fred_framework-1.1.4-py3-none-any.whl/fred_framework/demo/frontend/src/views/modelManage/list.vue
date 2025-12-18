<template>
  <div class="table-box">
    <ProTable
      ref="proTable"
      :columns="currentColumns"
      :request-api="getModelList"
      :init-param="initParam"
      :data-callback="dataCallback"
    >
      <!-- 表格 header 按钮 -->
      <template #tableHeader="scope">
        <el-button type="primary" :icon="CirclePlus" @click="openDrawer('新增')">{{ t("model.addModel") }}</el-button>
        <el-button
          v-auth="'delete'"
          type="danger"
          :icon="Delete"
          plain
          :disabled="!scope.isSelected"
          @click="batchDelete(scope.selectedListIds)"
        >
          {{ t("model.batchDelete") }}
        </el-button>
      </template>

      <!-- 表格操作 -->
      <template #operation="scope">
        <!-- 普通模型列表操作 -->
        <el-button type="primary" link :icon="View" @click="openDrawer('查看', scope.row)">{{ t("model.view") }}</el-button>
        <el-button type="primary" link :icon="EditPen" @click="openDrawer('编辑', scope.row)">{{ t("model.edit") }}</el-button>
        <el-button type="success" link :icon="PriceTag" @click="openLabelDrawer(scope.row)">{{ t("model.viewLabel") }}</el-button>
        <el-button type="warning" link :icon="Picture" @click="openImageManager(scope.row)">{{
          t("model.autoInferencePath")
        }}</el-button>
        <el-button v-auth="'delete'" type="danger" link :icon="Delete" @click="deleteModel(scope.row)">{{
          t("model.delete")
        }}</el-button>
      </template>
    </ProTable>
    <ModelDrawer ref="drawerRef" />
    <ModelLabelDrawer ref="labelDrawerRef" />
    <ModelImageManager ref="imageManagerRef" />
  </div>
</template>

<script setup lang="tsx">
import { reactive, ref, onMounted, computed } from "vue";
import { useI18n } from "vue-i18n";
import { useHandleData } from "@/hooks/useHandleData";

const { t } = useI18n();
import ProTable from "@/components/ProTable/index.vue";
import ModelDrawer from "./components/ModelDrawer.vue";
import ModelLabelDrawer from "./components/ModelLabelDrawer.vue";
import ModelImageManager from "./components/ModelImageManager.vue";
import { ColumnProps, ProTableInstance } from "@/components/ProTable/interface";
import { CirclePlus, Delete, EditPen, View, PriceTag, Picture } from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";
import { getModelListApi, deleteModelApi, createModelApi, updateModelApi } from "@/api/modules/model";

// ProTable 实例
const proTable = ref<ProTableInstance>();

// 初始化参数
const initParam = reactive({});

// dataCallback 是对于返回的表格数据做处理
const dataCallback = (data: any) => {
  // 确保records是数组，即使后端返回空数据
  const records = Array.isArray(data.records) ? data.records : [];
  const total = data.total || 0;

  return {
    records: records,
    total: total
  };
};

// 获取模型列表
const getModelList = (params: any) => {
  // 如果有场景ID参数，则调用场景关联模型列表API
  if (params.scene_id) {
    return getSceneModelListApi(params);
  }
  // 否则调用普通模型列表API
  return getModelListApi(params);
};

// 表格配置项 - 使用 computed 确保语言切换时能够响应更新
const columns = computed<ColumnProps<any>[]>(() => [
  {
    type: "selection",
    fixed: "left",
    width: 70
  },
  {
    prop: "id",
    label: t("model.id"),
    width: 80
  },
  {
    prop: "name",
    label: t("model.name"),
    width: 200,
    search: {
      el: "input",
      props: { placeholder: t("model.enterModelName") }
    }
  },
  {
    prop: "desc",
    label: t("model.description")
  },
  {
    prop: "image_paths",
    label: t("model.autoInferencePath"),
    width: 300,
    render: (scope: any) => {
      const paths = scope.row.image_paths || [];
      if (paths.length === 0) {
        return <span style="color: #999;">{t("model.noRelatedPath")}</span>;
      }
      return (
        <div>
          <div style="margin-bottom: 4px;">
            {paths.map((path: string, index: number) => (
              <div key={index} style="color: #409eff; font-size: 12px; margin-bottom: 2px;">
                {path}
              </div>
            ))}
          </div>
        </div>
      );
    }
  },
  {
    prop: "created",
    label: t("model.created"),
    width: 200
  },
  {
    prop: "modified",
    label: t("model.modified"),
    width: 200
  },
  { prop: "operation", label: t("model.operation"), fixed: "right", width: 300 }
]);

// 当前表格列配置 - 直接使用 computed columns
const currentColumns = columns;

// 删除模型信息
const deleteModel = async (params: any) => {
  await useHandleData(deleteModelApi, { id: params.id }, t("model.deleteConfirm", { name: params.name }));
  proTable.value?.getTableList();
};

// 批量删除模型信息
const batchDelete = async (ids: (string | number)[]) => {
  if (ids.length === 0) {
    ElMessage.warning(t("model.selectModelToDelete"));
    return;
  }

  try {
    // 批量删除需要逐个删除
    for (const id of ids) {
      const numericId = typeof id === "string" ? parseInt(id, 10) : id;
      await useHandleData(deleteModelApi, { id: numericId }, t("model.deleteConfirm", { name: numericId }));
    }
    proTable.value?.clearSelection();
    proTable.value?.getTableList();
    ElMessage.success(t("model.deleteSuccess", { count: ids.length }));
  } catch {
    ElMessage.error(t("model.batchDeleteFailed"));
  }
};

// 打开 drawer(新增、查看、编辑)
const drawerRef = ref<InstanceType<typeof ModelDrawer> | null>(null);
const openDrawer = (title: string, row: Partial<any> = {}) => {
  let api;
  if (title === "新增") {
    api = createModelApi;
  } else if (title === "编辑") {
    api = updateModelApi;
  }

  // 如果是场景关联模型，需要转换数据格式
  let processedRow = { ...row };
  if (initParam.scene_id && row.model_id) {
    // 将场景关联模型的数据格式转换为普通模型格式
    processedRow = {
      id: row.model_id,
      name: row.model_name,
      desc: row.model_desc,
      file_path: row.file_path
    };
  }

  const params = {
    title,
    isView: title === "查看",
    row: processedRow,
    api: api,
    getTableList: proTable.value?.getTableList
  };
  drawerRef.value?.acceptParams(params);
};

// 打开标签抽屉
const labelDrawerRef = ref<InstanceType<typeof ModelLabelDrawer> | null>(null);
const openLabelDrawer = (row: Partial<any>) => {
  // 如果是场景关联模型，需要转换数据格式
  let modelId = row.id;
  let modelName = row.name;

  if (initParam.scene_id && row.model_id) {
    modelId = row.model_id;
    modelName = row.model_name;
  }

  const params = {
    modelId: modelId,
    modelName: modelName
  };
  labelDrawerRef.value?.open(params);
};

// 打开图片管理抽屉
const imageManagerRef = ref<InstanceType<typeof ModelImageManager> | null>(null);
const openImageManager = (row: Partial<any>) => {
  // 如果是场景关联模型，需要转换数据格式
  let modelId = row.id;
  let modelName = row.name;

  if (initParam.scene_id && row.model_id) {
    modelId = row.model_id;
    modelName = row.model_name;
  }

  const params = {
    modelId: modelId,
    modelName: modelName
  };
  imageManagerRef.value?.openDrawer(params);
};

// 页面初始化
onMounted(() => {
  // 页面初始化逻辑
});
</script>

<style scoped>
.table-box {
  padding: 20px;
}

:deep(.el-table) {
  border-radius: 8px;
  overflow: hidden;
}

:deep(.el-table__header) {
  background-color: #f5f7fa;
}

:deep(.el-button--link) {
  padding: 4px 8px;
  margin: 0 2px;
}

:deep(.el-drawer__header) {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e4e7ed;
}

:deep(.el-form-item__label) {
  font-weight: 500;
}
</style>
