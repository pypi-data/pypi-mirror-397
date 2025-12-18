<template>
  <div class="store-tree-list-container">
    <div class="layout-wrapper">
      <!-- 左侧树形筛选器 -->
      <TreeFilter
        ref="treeFilterRef"
        label="label"
        id="id"
        :title="t('store.title')"
        :request-api="loadTreeData"
        :default-value="currentNodeKey"
        @change="handleTreeFilterChange"
      />

      <!-- 右侧门店列表 -->
      <div class="descriptions-box card">
        <ProTable
          :key="locale"
          ref="proTable"
          :title="t('store.storeList')"
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
            <el-button type="primary" v-auth="'storeAdd'" :icon="CirclePlus" @click="openDrawer('新增')">
              {{ t("store.addStore") }}
            </el-button>
          </template>

          <!-- 门店操作 -->
          <template #operation="scope">
            <el-button type="primary" v-auth="'storeEdit'" link :icon="EditPen" @click="openDrawer('编辑', scope.row)">
              {{ t("store.edit") }}
            </el-button>
            <el-button type="success" link :icon="Setting" @click="openSceneDrawer(scope.row)">
              {{ t("store.viewScenes") }}
            </el-button>
            <el-button type="warning" link :icon="Link" @click="openBindSceneDrawer(scope.row)">
              {{ t("store.bindScene") }}
            </el-button>
            <el-button type="danger" v-auth="'storeDel'" link @click="handleDelete(scope.row)">
              {{ t("store.delete") }}
            </el-button>
          </template>
        </ProTable>
      </div>
    </div>

    <!-- 新增/编辑门店抽屉 -->
    <StoreDrawer ref="drawerRef" />

    <!-- 门店场景管理抽屉 -->
    <StoreSceneDrawer ref="sceneDrawerRef" />

    <!-- 绑定场景抽屉 -->
    <BindSceneDrawer ref="bindSceneDrawerRef" />
  </div>
</template>

<script setup lang="ts">
import {
  deleteStore,
  getRegionTree,
  getStoreList,
  saveStore,
  updateStore,
  type StoreInfo,
  type StoreListParams
} from "@/api/modules/store";
import ProTable from "@/components/ProTable/index.vue";
import TreeFilter from "@/components/TreeFilter/index.vue";
import { CirclePlus, EditPen, Link, Setting } from "@element-plus/icons-vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { computed, nextTick, onMounted, onUnmounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import BindSceneDrawer from "./components/BindSceneDrawer.vue";
import StoreDrawer from "./components/StoreDrawer.vue";
import StoreSceneDrawer from "./components/StoreSceneDrawer.vue";

// 国际化
const { t, locale } = useI18n();

// 响应式数据
const currentNodeKey = ref<string>("");
const drawerRef = ref();
const proTable = ref();
const treeFilterRef = ref();
const sceneDrawerRef = ref();
const bindSceneDrawerRef = ref();

// 搜索防抖定时器
const searchTimeout = ref<ReturnType<typeof setTimeout> | null>(null);

// 表格实例引用

// resize事件处理函数
const handleResize = () => {
  // 触发表格重新布局
  if (proTable.value && proTable.value.element && proTable.value.element.value) {
    proTable.value.element.value.doLayout();
  }
};

// 搜索参数，用于联动树形选择
const initParam = ref<StoreListParams>({
  province: "",
  city: "",
  district: "",
  // 新增省市区ID参数
  country_id: undefined,
  province_id: undefined,
  city_id: undefined,
  district_id: undefined
});

// 表格列定义
const columns = computed(() => [
  { prop: "id", label: t("store.id"), width: 80 },
  {
    prop: "name",
    label: t("store.name"),
    width: 150,
    search: {
      el: "input",
      order: 1,
      props: { placeholder: t("store.inputStoreName"), clearable: true }
    }
  },
  {
    prop: "region_info",
    label: t("store.region"),
    width: 260,
    render: (scope: any) => {
      const row = scope.row;
      const parts: string[] = [];
      if (row.country_name && row.country_name.trim()) parts.push(row.country_name);
      if (row.province_name && row.province_name.trim()) parts.push(row.province_name);
      if (row.city_name && row.city_name.trim()) parts.push(row.city_name);
      if (row.district_name && row.district_name.trim()) parts.push(row.district_name);

      const result = parts.length > 0 ? parts.join(" / ") : t("store.notSet");
      return result;
    }
  },
  {
    prop: "address",
    label: t("store.address"),
    minWidth: 200,
    search: {
      el: "input",
      order: 2,
      span: 2,
      props: { placeholder: t("store.inputAddress"), clearable: true }
    }
  },
  {
    prop: "scene_num",
    label: t("store.sceneCount"),
    width: 100,
    formatter: (row: any) => {
      const count = row.scene_num || 0;
      return `${count} ${t("store.scenes")}`;
    }
  },
  { prop: "operation", label: t("store.operation"), width: 360, fixed: "right" }
]);

// 加载树形数据（适配 TreeFilter 组件）
const loadTreeData = async () => {
  try {
    return await getRegionTree(true, "store"); // 请求带门店数量统计的数据
  } catch {
    ElMessage.error(t("store.loadTreeFailed"));
    return { data: [] };
  }
};

// 处理 TreeFilter 组件的选择变化
const handleTreeFilterChange = (selectedId: string) => {
  currentNodeKey.value = selectedId;

  // 临时保存新的参数
  const newParams = {
    province: "",
    city: "",
    district: "",
    country_id: undefined as number | undefined,
    province_id: undefined as number | undefined,
    city_id: undefined as number | undefined,
    district_id: undefined as number | undefined
  };

  // 如果选择了 "全部" 选项，清空所有筛选条件
  if (!selectedId) {
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
  for (let i = 0; i < idParts.length; i += 2) {
    const key = idParts[i];
    const value = parseInt(idParts[i + 1]);
    if (key === "country") newParams.country_id = value;
    else if (key === "province") newParams.province_id = value;
    else if (key === "city") newParams.city_id = value;
    else if (key === "district") newParams.district_id = value;
  }

  // 更新搜索参数
  Object.assign(initParam.value, newParams);

  // 刷新表格数据
  if (proTable.value) {
    proTable.value.getTableList();
  }
};

// 表格数据回调处理
const dataCallback = (data: any) => {
  return {
    ...data,
    records: data.records.map((item: any) => {
      return {
        ...item,
        // 确保经纬度字段存在
        latitude: item.latitude || 0,
        longitude: item.longitude || 0,
        // 确保场景数量字段存在
        scene_num: item.scene_num || 0
      };
    })
  };
};

// 处理请求错误
const handleRequestError = () => {
  ElMessage.error(t("store.loadListFailed"));
};

// 获取表格数据
const getTableList = (params: StoreListParams) => {
  // 添加防抖处理
  if (searchTimeout.value) {
    clearTimeout(searchTimeout.value);
  }

  return new Promise(resolve => {
    searchTimeout.value = setTimeout(async () => {
      try {
        const response = await getStoreList(params);
        resolve(response);
      } catch {
        ElMessage.error(t("store.loadListFailed"));
        resolve({ data: { records: [], total: 0, pageNum: 1, pageSize: 10 } });
      }
    }, 300); // 300ms防抖
  });
};

// 打开抽屉
const openDrawer = (title: string, row: any = {}) => {
  // 先加载最新的树形数据，确保传递给抽屉的是最新数据
  loadTreeData().then(treeData => {
    const params = {
      title,
      row: { ...row },
      api: title === "新增" ? saveStore : (params: any) => updateStore(row.id, params),
      getTableList: (operationType?: string) => {
        // 新增操作后需要刷新树形数据和表格数据
        if (operationType === "新增") {
          loadTreeData(); // 刷新树形数据
        }

        // 刷新表格数据
        if (proTable.value) {
          proTable.value.getTableList();
        }
      },
      // 将树形数据传递给抽屉组件
      regionTreeData: treeData?.data || []
    };

    drawerRef.value.acceptParams(params);
  });
};

// 打开场景管理抽屉
const openSceneDrawer = (row: StoreInfo) => {
  sceneDrawerRef.value?.openDrawer({
    title: `已绑定场景 - ${row.name}`,
    storeId: row.id,
    storeName: row.name,
    getTableList: () => {
      // 刷新表格数据
      if (proTable.value) {
        proTable.value.getTableList();
      }
    }
  });
};

// 打开绑定场景抽屉
const openBindSceneDrawer = (row: StoreInfo) => {
  bindSceneDrawerRef.value?.openDrawer({
    title: `绑定场景 - ${row.name}`,
    storeId: row.id,
    storeName: row.name,
    getTableList: () => {
      // 刷新表格数据
      if (proTable.value) {
        proTable.value.getTableList();
      }
    }
  });
};

// 删除门店
const handleDelete = (row: StoreInfo) => {
  ElMessageBox.confirm(t("store.deleteConfirm"), t("common.confirmTitle"), {
    type: "warning"
  })
    .then(async () => {
      try {
        await deleteStore(row.id);
        ElMessage.success(t("store.deleteSuccess"));

        // 删除后刷新树形数据和表格数据
        loadTreeData(); // 刷新树形数据

        // 刷新表格数据
        if (proTable.value) {
          proTable.value.getTableList();
        }
      } catch {
        ElMessage.error(t("store.deleteFailed"));
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

  // 添加resize事件监听器
  window.addEventListener("resize", handleResize);

  // 确保在DOM更新后重新计算表格高度
  nextTick(() => {
    // 延迟执行以确保DOM完全渲染
    setTimeout(() => {
      handleResize();
    }, 100);
  });

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
  // 移除resize事件监听器
  window.removeEventListener("resize", handleResize);
});
</script>

<style scoped lang="scss">
@import "@/styles/table-optimization.scss";

.store-tree-list-container {
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

.descriptions-box.card {
  flex: 1;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

// 确保搜索区域和表格区域之间有间距
:deep(.table-search) {
  margin-bottom: 20px !important;
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

/* 右侧表格区域样式通过 .descriptions-box.card 实现 */

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

/* 确保 ProTable 的 table-main 使用 flex 布局，让分页组件正常显示 */
:deep(.table-main) {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 0;
}

/* 表格部分使用 flex: 1，让分页组件有空间显示 */
:deep(.el-table) {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 0;
}

:deep(.el-table__inner-wrapper) {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 0;
}

/* 确保分页组件可见 */
:deep(.pagination-wrapper) {
  flex-shrink: 0;
  padding: 20px 0;
  text-align: center;
  background: #fff;
  border-top: 1px solid #ebeef5;
}

/* 场景数量显示样式 */
.scene-count-display {
  display: flex;
  justify-content: center;
  align-items: center;
}

/* 响应式布局 */
@media (max-width: 768px) {
  .layout-wrapper {
    flex-direction: column;
  }

  .store-tree-list-container {
    padding: 10px;
  }

  :deep(.el-table) {
    height: calc(100vh - 400px);
  }
}
</style>
