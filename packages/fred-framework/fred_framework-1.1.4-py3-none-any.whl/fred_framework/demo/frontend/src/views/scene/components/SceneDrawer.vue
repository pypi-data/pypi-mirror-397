<template>
  <el-drawer v-model="drawerVisible" :destroy-on-close="true" size="80%" :title="`${drawerProps.title}场景`">
    <div class="drawer-content">
      <!-- 场景列表表格 -->
      <ProTable
        ref="proTable"
        :columns="columns"
        :request-api="getSceneList"
        :data-callback="dataCallback"
        :init-param="initParam"
        :pagination="true"
      >
        <!-- 表格 header 按钮 -->
        <template #tableHeader="scope">
          <el-button type="primary" :icon="CirclePlus" @click="openFormDrawer('新增')">新增场景</el-button>
          <el-button type="danger" :icon="Delete" plain :disabled="!scope.isSelected" @click="batchDelete(scope.selectedListIds)">
            批量删除场景
          </el-button>
        </template>

        <!-- 表格操作 -->
        <template #operation="scope">
          <div style="display: flex; gap: 8px; flex-wrap: wrap; align-items: center">
            <el-button type="primary" link :icon="View" @click="openFormDrawer('查看', scope.row)">查看</el-button>
            <el-button type="primary" link :icon="EditPen" @click="openFormDrawer('编辑', scope.row)">编辑</el-button>
            <el-button type="warning" link :icon="Document" @click="handleAnnotationContent(scope.row)">标注内容</el-button>
            <el-button type="danger" link :icon="Delete" @click="deleteScene(scope.row)">删除</el-button>
          </div>
        </template>
      </ProTable>
    </div>

    <!-- 场景表单抽屉 -->
    <SceneFormDrawer ref="formDrawerRef" />
  </el-drawer>
</template>

<script setup lang="tsx">
import { ref, reactive } from "vue";
import { useRouter } from "vue-router";
import { useHandleData } from "@/hooks/useHandleData";
import { useAuthButtons } from "@/hooks/useAuthButtons";
import ProTable from "@/components/ProTable/index.vue";
import SceneFormDrawer from "./SceneFormDrawer.vue";
import { ColumnProps, ProTableInstance } from "@/components/ProTable/interface";
import { CirclePlus, Delete, EditPen, Document, View } from "@element-plus/icons-vue";
import { getSceneList as getSceneListApi, updateSceneStatus, deleteScene as deleteSceneApi } from "@/api/modules/scene";

interface Scene {
  id?: number;
  name: string;
  description: string;
  status: number;
  sort_order: number;
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

interface DrawerProps {
  title: string;
  isView: boolean;
  row: Scene;
  api?: (params: any) => Promise<any>;
  getTableList?: () => void;
}

// ProTable 实例
const proTable = ref<ProTableInstance>();

// 抽屉
const drawerVisible = ref(false);
const formDrawerRef = ref();

// 路由
const router = useRouter();

// 页面按钮权限
const { BUTTONS } = useAuthButtons();

// 如果表格需要初始化请求参数，直接定义传给 ProTable
const initParam = reactive({});

// dataCallback 是对于返回的表格数据做处理
const dataCallback = (data: any) => {
  if (import.meta.env.DEV) {
  }
  return {
    records: data.records,
    total: data.total
  };
};

// 表格配置项
const columns = reactive<ColumnProps<Scene>[]>([
  {
    type: "selection",
    fixed: "left",
    width: 70
  },
  {
    prop: "id",
    label: "ID",
    width: 100
  },
  {
    prop: "name",
    label: "场景名称",
    width: 150,
    search: { el: "input" }
  },
  {
    prop: "description",
    label: "描述",
    showOverflowTooltip: true
  },
  {
    prop: "status",
    label: "状态",
    width: 100,
    enum: [
      { label: "启用", value: 1 },
      { label: "禁用", value: 0 }
    ],
    search: { el: "select", props: { filterable: true } },
    fieldNames: { label: "label", value: "value" },
    render: scope => {
      return (
        <>
          {BUTTONS.value.status ? (
            <el-switch
              style={{ "--el-switch-on-color": "#67c23a", "--el-switch-off-color": "#ff4949" }}
              model-value={scope.row.status === 1}
              active-text="启用"
              inactive-text="禁用"
              active-value={1}
              inactive-value={0}
              onClick={() => changeStatus(scope.row)}
            />
          ) : (
            <el-tag type={scope.row.status === 1 ? "success" : "danger"}>{scope.row.status === 1 ? "启用" : "禁用"}</el-tag>
          )}
        </>
      );
    }
  },
  {
    prop: "sort_order",
    label: "排序",
    width: 80
  },
  {
    prop: "created",
    label: "创建时间",
    width: 200
  },
  { prop: "operation", label: "操作", fixed: "right", width: 200 }
]);

const drawerProps = ref<DrawerProps>({
  isView: false,
  title: "",
  row: {
    name: "",
    description: "",
    status: 1,
    sort_order: 0
  }
});

/**
 * 请求场景列表数据
 * @param params 查询参数，包含分页和筛选条件
 * @returns Promise<ApiResponse> 返回API响应数据
 */
const getSceneList = async (params: SceneListParams) => {
  try {
    if (import.meta.env.DEV) {
    }
    const response = await getSceneListApi(params);
    if (import.meta.env.DEV) {
    }

    // 根据日志，API 返回的是 {code: 200, data: {...}}
    const apiResponse = response as unknown as ApiResponse;
    if (response && (apiResponse.code === 200 || apiResponse.code === "200")) {
      // const data = apiResponse.data || {};
      if (import.meta.env.DEV) {
      }

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
    console.error("getSceneList 请求失败:", error);
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
  await useHandleData(deleteSceneApi, { id: [params.id] }, `删除【${params.name}】场景`);
  proTable.value?.getTableList();
};

/**
 * 批量删除场景信息
 * @param id 场景ID数组
 */
const batchDelete = async (id: string[]) => {
  await useHandleData(deleteSceneApi, { id }, "删除所选场景信息");
  proTable.value?.clearSelection();
  proTable.value?.getTableList();
};

/**
 * 切换场景状态
 * @param row 场景对象
 */
const changeStatus = async (row: Scene) => {
  await useHandleData(updateSceneStatus, { id: row.id, status: row.status === 1 ? 0 : 1 }, `切换【${row.name}】场景状态`);
  proTable.value?.getTableList();
};

// 标注内容
const handleAnnotationContent = (row: Scene) => {
  // 跳转到标注管理页面，并传递场景ID作为筛选条件
  router.push({
    path: "/annotation/index",
    query: { sceneId: row.id, sceneName: row.name }
  });
};

// 打开表单抽屉(新增、查看、编辑)
const openFormDrawer = (title: string, row: Partial<Scene> = {}) => {
  const params = {
    title,
    isView: title === "查看",
    row: { ...row },
    api: title === "新增" ? undefined : title === "编辑" ? undefined : undefined,
    getTableList: proTable.value?.getTableList
  };
  formDrawerRef.value?.acceptParams(params);
};

// 接收父组件传过来的参数
const acceptParams = (params: DrawerProps) => {
  drawerProps.value = params;

  drawerVisible.value = true;
};

defineExpose({
  acceptParams
});
</script>

<style scoped lang="scss">
.drawer-content {
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
