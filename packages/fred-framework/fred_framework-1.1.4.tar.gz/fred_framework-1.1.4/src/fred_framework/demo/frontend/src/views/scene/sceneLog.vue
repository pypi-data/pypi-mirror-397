<template>
  <div class="scene-log-container">
    <div class="layout-wrapper">
      <!-- 左侧门店筛选器 -->
      <StoreFilter v-model="currentStoreId" @change="handleStoreChange" />

      <!-- 右侧表格 -->
      <div class="table-box">
        <ProTable
          ref="proTable"
          :columns="columns"
          :request-api="getSceneLogList"
          :data-callback="dataCallback"
          :request-auto="false"
        >
          <!-- 表格操作 -->
          <template #operation="scope">
            <el-button v-if="scope.row.show_notification" type="primary" link @click="handleViewNotification(scope.row)">
              {{ t("sceneLog.viewNotification") }}
            </el-button>
          </template>
        </ProTable>
      </div>
    </div>

    <!-- 通知侧滑框 -->
    <NotificationDrawer ref="notificationDrawerRef" />
  </div>
</template>

<script setup lang="tsx" name="sceneLog">
import { getSceneList } from "@/api/modules/scene";
import { getSceneLogList as getSceneLogListApi } from "@/api/modules/sceneLog";
import type { StoreInfo } from "@/api/modules/store";
import ProTable from "@/components/ProTable/index.vue";
import { ColumnProps, ProTableInstance } from "@/components/ProTable/interface";
import StoreFilter from "@/components/StoreFilter/index.vue";
import { computed, onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import NotificationDrawer from "./components/NotificationDrawer.vue";

// 国际化
const { t } = useI18n();

// ProTable 实例
const proTable = ref<ProTableInstance>();

// NotificationDrawer 实例
const notificationDrawerRef = ref<InstanceType<typeof NotificationDrawer> | null>(null);

// 门店选择相关
const currentStoreId = ref<number | null>(null);
// 场景列表
const sceneList = ref<Array<{ id: number; name: string }>>([]);

// 处理门店选择变化
const handleStoreChange = (store: StoreInfo | null) => {
  if (store) {
    currentStoreId.value = store.id;
    // 触发表格刷新
    if (proTable.value) {
      proTable.value.searchParam = {
        ...proTable.value.searchParam,
        store_id: store.id
      };
      proTable.value.getTableList();
    }
  }
};

// 加载场景列表
const loadSceneList = async () => {
  try {
    const response = await getSceneList({ pageNum: 1, pageSize: 1000 });
    if (response && response.data && response.data.records) {
      sceneList.value = response.data.records.map((item: any) => ({
        id: item.id,
        name: item.name
      }));
    }
  } catch (error: any) {
    // 如果是请求被取消（CanceledError），静默处理，不显示错误消息
    // 这通常发生在组件卸载或页面切换时，正在进行的请求被取消
    if (error?.name === "CanceledError" || error?.code === "ERR_CANCELED" || error?.message === "canceled") {
      return;
    }
    console.error("加载场景列表失败:", error);
  }
};

// dataCallback 是对于返回的表格数据做处理
const dataCallback = (data: any) => {
  if (Array.isArray(data)) {
    return {
      records: data,
      total: data.length
    };
  }
  return {
    records: data.records || [],
    total: data.total || 0
  };
};

// 获取场景日志列表
const getSceneLogList = (params: any) => {
  const queryParams: any = {
    pageNum: params.pageNum,
    pageSize: params.pageSize
  };

  // 如果有选中的门店，传递门店ID
  if (currentStoreId.value) {
    queryParams.store_id = currentStoreId.value;
  }

  // 如果有场景ID，传递场景ID
  if (params.scene_id) {
    queryParams.scene_id = params.scene_id;
  }

  return getSceneLogListApi(queryParams);
};

// 格式化时间
const formatDateTime = (dateString: string | null | undefined) => {
  if (!dateString) return "-";
  try {
    const date = new Date(dateString);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    const hours = String(date.getHours()).padStart(2, "0");
    const minutes = String(date.getMinutes()).padStart(2, "0");
    const seconds = String(date.getSeconds()).padStart(2, "0");
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
  } catch {
    return "-";
  }
};
// 表格配置项
const columns = computed<ColumnProps<any>[]>(() => [
  {
    prop: "id",
    label: t("sceneLog.id"),
    width: 100
  },
  {
    prop: "store_name",
    label: t("sceneLog.storeName"),
    width: 200,
    render: (scope: any) => {
      return <span>{scope.row.store_name || "-"}</span>;
    }
  },
  {
    prop: "scene_id",
    label: t("sceneLog.sceneName"),
    width: 200,
    isFilterEnum: false,
    search: {
      el: "select",
      props: {
        placeholder: t("sceneLog.selectScene"),
        clearable: true,
        filterable: true
      }
    },
    enum: async () => {
      try {
        // 禁用取消机制，避免 enum 函数被多次调用时请求被取消
        const response: any = await getSceneList({ pageNum: 1, pageSize: 1000 }, { cancel: false });

        let records: any[] = [];
        if (response && typeof response === "object") {
          if (response.data && response.data.records && Array.isArray(response.data.records)) {
            records = response.data.records;
          } else if (response.records && Array.isArray(response.records)) {
            records = response.records;
          } else if (Array.isArray(response.data)) {
            records = response.data;
          }
        }

        // 同步更新 sceneList，供 render 函数使用
        sceneList.value = records.map((item: any) => ({
          id: item.id,
          name: item.name
        }));

        const options = records.map((item: any) => ({
          label: item.name,
          value: item.id
        }));

        return {
          data: options
        };
      } catch (error: any) {
        // 如果是请求被取消（CanceledError），延迟重试
        if (error?.name === "CanceledError" || error?.code === "ERR_CANCELED" || error?.message === "canceled") {
          // 延迟 100ms 后重试
          await new Promise(resolve => setTimeout(resolve, 100));
          try {
            const retryResponse: any = await getSceneList({ pageNum: 1, pageSize: 1000 }, { cancel: false });
            let records: any[] = [];
            if (retryResponse && typeof retryResponse === "object") {
              if (retryResponse.data && retryResponse.data.records && Array.isArray(retryResponse.data.records)) {
                records = retryResponse.data.records;
              } else if (retryResponse.records && Array.isArray(retryResponse.records)) {
                records = retryResponse.records;
              } else if (Array.isArray(retryResponse.data)) {
                records = retryResponse.data;
              }
            }
            sceneList.value = records.map((item: any) => ({
              id: item.id,
              name: item.name
            }));
            const options = records.map((item: any) => ({
              label: item.name,
              value: item.id
            }));
            return { data: options };
          } catch {
            sceneList.value = [];
            return { data: [] };
          }
        }
        sceneList.value = [];
        return { data: [] };
      }
    },
    render: (scope: any) => {
      if (scope.row.scene_name) {
        return <span>{scope.row.scene_name}</span>;
      }
      return <span>-</span>;
    }
  },
  {
    prop: "message",
    label: t("sceneLog.message"),
    showOverflowTooltip: true
  },
  {
    prop: "status",
    label: t("sceneLog.status"),
    width: 120,
    render: (scope: any) => {
      const status = scope.row.status;
      return <span>{status !== undefined && status !== null ? status : "-"}</span>;
    }
  },
  {
    prop: "the_time",
    label: t("sceneLog.theTime"),
    width: 180,
    render: (scope: any) => {
      return <span>{formatDateTime(scope.row.the_time)}</span>;
    }
  },
  {
    prop: "operation",
    label: t("sceneLog.operation"),
    fixed: "right",
    width: 150
  }
]);

// 查看通知
const handleViewNotification = (row: any) => {
  if (row && row.id) {
    notificationDrawerRef.value?.openDrawer(row.id);
  }
};

// 组件挂载时初始化
onMounted(() => {
  // 加载场景列表
  loadSceneList();
});
</script>

<style scoped lang="scss">
@import "@/styles/table-optimization.scss";

.scene-log-container {
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
</style>
