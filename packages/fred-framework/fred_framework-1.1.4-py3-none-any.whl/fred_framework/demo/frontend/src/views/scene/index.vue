<template>
  <div class="table-box">
    <ProTable
      :key="locale"
      ref="proTable"
      :columns="columns"
      :request-api="getTableList"
      :init-param="initParam"
      :data-callback="dataCallback"
    >
      <!-- 表格 header 按钮 -->
      <template #tableHeader="scope">
        <el-button v-auth="'新增场景'" type="primary" :icon="CirclePlus" @click="openDrawer('新增')">{{
          t("scene.addScene")
        }}</el-button>
        <el-button
          v-auth="'delete'"
          type="danger"
          :icon="Delete"
          plain
          :disabled="!scope.isSelected"
          @click="batchDelete(scope.selectedListIds)"
        >
          {{ t("scene.batchDelete") }}
        </el-button>
      </template>
      <!-- 表格操作 -->
      <template #operation="scope">
        <div style="display: flex; gap: 8px; flex-wrap: wrap; align-items: center">
          <el-button v-auth="'bindModel'" type="success" link :icon="Link" @click="handleBindModels(scope.row)">
            {{ t("scene.bindModels") }}
          </el-button>
          <el-button v-auth="'sceneEdit'" type="primary" link :icon="EditPen" @click="openDrawer('编辑', scope.row)">
            {{ t("scene.edit") }}
          </el-button>
          <el-button v-auth="'sceneForbidden'" type="danger" link :icon="Delete" @click="deleteScene(scope.row)">
            {{ t("scene.delete") }}
          </el-button>
        </div>
      </template>
    </ProTable>
    <SceneFormDrawer ref="drawerRef" />
    <SceneModelDrawer ref="modelDrawerRef" />
  </div>
</template>

<script setup lang="tsx">
import { computed, ref, h } from "vue";
import { useI18n } from "vue-i18n";
import { useHandleData } from "@/hooks/useHandleData";
// import { useAuthButtons } from "@/hooks/useAuthButtons";
import ProTable from "@/components/ProTable/index.vue";
import SceneFormDrawer from "./components/SceneFormDrawer.vue";
import SceneModelDrawer from "./components/SceneModelDrawer.vue";
import { ProTableInstance } from "@/components/ProTable/interface";
import { CirclePlus, Delete, EditPen, Link } from "@element-plus/icons-vue";
import { ElSwitch, ElTag } from "element-plus";
import { getSceneList, updateSceneStatus, saveScene, deleteScene as deleteSceneApi } from "@/api/modules/scene";

interface Scene {
  id?: number;
  name: string;
  description: string;
  status: number;
  sort_order: number;
  hz?: number;
  created?: string;
}

interface ApiResponse<T = any> {
  code: string | number;
  data: T;
  message?: string;
}

interface SceneListParams {
  pageNum: number;
  pageSize: number;
  name?: string;
  status?: number;
}

// ProTable 实例
const proTable = ref<ProTableInstance>();

// 如果表格需要初始化请求参数，直接定义传给 ProTable
const initParam = ref({});

// dataCallback 是对于返回的表格数据做处理，如果你后台返回的数据不是 list && total 这些字段，可以在这里进行处理成这些字段
const dataCallback = (data: any) => {
  if (import.meta.env.DEV) {
  }
  return {
    records: data.records,
    total: data.total
  };
};

// 国际化
const { t, locale } = useI18n();

// 抽屉
const drawerRef = ref();
const modelDrawerRef = ref();

// 页面按钮权限
// const { BUTTONS } = useAuthButtons();

// 表格配置项
const columns = computed(() => [
  {
    prop: "id",
    label: t("scene.id"),
    width: 100
  },
  {
    prop: "name",
    label: t("scene.sceneName"),
    width: 150,
    search: { el: "input", props: { placeholder: t("scene.inputSceneName") } }
  },
  {
    prop: "description",
    label: t("scene.sceneDescription"),
    showOverflowTooltip: true
  },
  {
    prop: "status",
    label: t("scene.status"),
    width: 160,
    enum: [
      { label: t("scene.enabled"), value: 1 },
      { label: t("scene.disabled"), value: 0 }
    ],
    search: { el: "select", props: { filterable: true, placeholder: t("scene.selectStatus") } },
    fieldNames: { label: "label", value: "value" },
    render: scope => {
      // 调试信息
      if (import.meta.env.DEV) {
      }

      // 如果状态未定义，显示加载中
      if (scope.row.status === undefined) {
        return h(ElTag, { type: "info" }, t("scene.loading"));
      }

      return h(ElSwitch, {
        style: { "--el-switch-on-color": "#67c23a", "--el-switch-off-color": "#ff4949" },
        modelValue: scope.row.status === 1,
        "active-text": t("scene.enabled"),
        "inactive-text": t("scene.disabled"),
        onChange: (value: string | number | boolean) => {
          // 只有在状态真正改变时才触发
          const newStatus = Number(value);
          if (newStatus !== scope.row.status) {
            handleStatusChange(scope.row, value);
          }
        }
      });
    }
  },
  {
    prop: "hz",
    label: t("scene.executionFrequency"),
    width: 120,
    render: scope => {
      if (scope.row.hz !== undefined && scope.row.hz !== null) {
        return <el-tag type="info">{scope.row.hz}秒</el-tag>;
      } else {
        return <span>-</span>;
      }
    }
  },
  {
    prop: "created",
    label: t("scene.created"),
    width: 200
  },
  { prop: "operation", label: t("scene.operation"), fixed: "right", width: 280 }
]);

/**
 * 请求场景列表数据
 * @param params 查询参数，包含分页和筛选条件
 * @returns Promise<ApiResponse> 返回API响应数据
 */
const getTableList = async (params: SceneListParams) => {
  try {
    if (import.meta.env.DEV) {
    }
    const response = await getSceneList(params);
    if (import.meta.env.DEV) {
    }

    // 根据日志，API 返回的是 {code: 200, data: {...}}
    const apiResponse = response as unknown as ApiResponse;
    if (response && (apiResponse.code === 200 || apiResponse.code === "200")) {
      // const data = apiResponse.data || {};

      // 返回完整的响应对象，让 useTable 正确解构 data 字段
      return response;
    } else {
      console.error("API 响应错误:", response);
      return {
        code: 200,
        data: {
          records: [],
          total: 0
        }
      };
    }
  } catch (error) {
    console.error("getTableList 请求失败:", error);
    return {
      code: 200,
      data: {
        records: [],
        total: 0
      }
    };
  }
};

/**
 * 删除场景信息
 * @param params 场景对象，包含id和name
 */
const deleteScene = async (params: Scene) => {
  if (!params.id) {
    console.error("场景ID不能为空");
    return;
  }
  await useHandleData(deleteSceneApi, { id: [params.id] }, t("scene.deleteConfirm", { name: params.name }), "warning", t);
  proTable.value?.getTableList();
};

/**
 * 批量删除场景信息
 * @param id 场景ID数组
 */
const batchDelete = async (id: string[]) => {
  if (!id || id.length === 0) {
    console.error("请选择要删除的场景");
    return;
  }
  // 将字符串ID转换为数字ID
  const numericIds = id.map(id => parseInt(id, 10)).filter(id => !isNaN(id));
  if (numericIds.length === 0) {
    console.error("无效的场景ID");
    return;
  }
  await useHandleData(deleteSceneApi, { id: numericIds }, t("scene.batchDeleteConfirm"), "warning", t);
  proTable.value?.clearSelection();
  proTable.value?.getTableList();
};

/**
 * 处理状态开关变化
 * @param row 场景对象
 * @param newStatus 新状态值
 */
const handleStatusChange = async (row: Scene, newStatus: string | number | boolean) => {
  const status = Number(newStatus);
  const action = status === 1 ? t("scene.enabled") : t("scene.disabled");
  await useHandleData(
    updateSceneStatus,
    { id: row.id, status: status },
    t("scene.statusChangeConfirm", { action, name: row.name }),
    "warning",
    t
  );
  proTable.value?.getTableList();
};

// 打开 drawer(新增、查看、编辑)
const openDrawer = (title: string, row: Partial<Scene> = {}) => {
  const params = {
    title,
    isView: title === "查看",
    row: { ...row },
    api: title === "新增" ? saveScene : title === "编辑" ? saveScene : undefined,
    getTableList: proTable.value?.getTableList
  };
  drawerRef.value?.acceptParams(params);
};

// 查看已绑定模型
const handleBindModels = (row: Scene) => {
  // 打开场景模型抽屉（只显示已绑定模型）
  modelDrawerRef.value?.openDrawer(row);
};
</script>

<style scoped lang="scss">
@import "@/styles/table-optimization.scss";

.table-box {
  @extend .table-box;
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
