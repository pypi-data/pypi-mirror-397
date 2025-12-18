<template>
  <div class="iotdb-paths-box">
    <ProTable
      :key="locale"
      ref="proTable"
      :columns="columns"
      :request-api="getPathsApi"
      :data-callback="dataCallback"
      :init-param="initParam"
    >
      <template #tableHeader>
        <el-button type="primary" :icon="Refresh" @click="refresh">{{ t("dataBase.refresh") }}</el-button>
        <el-button type="danger" :icon="Delete" @click="deleteAllPaths">{{ t("dataBase.deleteAllPaths") }}</el-button>
      </template>
      <template #operation="scope">
        <el-button type="danger" link :icon="Delete" @click="() => deletePath(scope.row)">
          {{ t("dataBase.deletePath") }}
        </el-button>
      </template>
    </ProTable>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { useI18n } from "vue-i18n";
import ProTable from "@/components/ProTable/index.vue";
import { getIoTDBPaths, clearIoTDBData } from "@/api/modules/dataBase";
import { Refresh, Delete } from "@element-plus/icons-vue";
import { ElMessage, ElMessageBox } from "element-plus";

const { t, locale } = useI18n();

interface PathItem {
  path: string;
  count: number;
}

const proTable = ref();
const initParam = ref({
  path_pattern: "root.inference.**"
});

const columns = computed(() => {
  void locale.value;
  return [
    { prop: "path", label: t("dataBase.path"), align: "left" },
    { prop: "count", label: t("dataBase.recordCount"), width: 200, align: "center" },
    { prop: "operation", label: t("dataBase.operation"), width: 150, fixed: "right" }
  ];
});

const dataCallback = (data: any) => {
  // 后端返回的数据格式：{ records: [...], total: 42, pageNum: 1, pageSize: 10 }
  if (data?.records && Array.isArray(data.records)) {
    return { records: data.records, total: data.total || data.records.length };
  }
  // 兼容其他可能的格式
  if (data?.paths && Array.isArray(data.paths)) {
    return { records: data.paths, total: data.total || data.paths.length };
  }
  return { records: [], total: 0 };
};

const getPathsApi = async (params: any) => {
  try {
    const result = await getIoTDBPaths(params);
    return result;
  } catch (error) {
    throw error;
  }
};

const refresh = () => {
  proTable.value?.getTableList();
};

const deleteAllPaths = () => {
  ElMessageBox.confirm(t("dataBase.deleteAllPathsConfirm"), t("dataBase.prompt"), {
    confirmButtonText: t("dataBase.confirm"),
    cancelButtonText: t("dataBase.cancel"),
    type: "warning"
  })
    .then(() => {
      clearIoTDBData({ delete_path: true })
        .then(() => {
          ElMessage.success(t("dataBase.deletePathSuccess"));
          proTable.value?.getTableList();
        })
        .catch(() => {
          // 错误信息已在拦截器中处理
        });
    })
    .catch(() => {
      // 用户取消
    });
};

const deletePath = (row: PathItem) => {
  ElMessageBox.confirm(t("dataBase.deletePathConfirm", { path: row.path }), t("dataBase.prompt"), {
    confirmButtonText: t("dataBase.confirm"),
    cancelButtonText: t("dataBase.cancel"),
    type: "warning"
  })
    .then(() => {
      clearIoTDBData({ path: row.path, delete_path: true })
        .then(() => {
          ElMessage.success(t("dataBase.deletePathSuccess"));
          proTable.value?.getTableList();
        })
        .catch(() => {
          // 错误信息已在拦截器中处理
        });
    })
    .catch(() => {
      // 用户取消
    });
};
</script>

<style scoped lang="scss">
@import "@/styles/table-optimization.scss";

.iotdb-paths-box {
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
