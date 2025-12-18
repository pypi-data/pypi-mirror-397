<template>
  <div class="table-box">
    <ProTable ref="proTable" :columns="columns" :request-api="debugGetLabelListApi" :data-callback="dataCallback">
      <!-- 表格 header 按钮 -->
      <template #tableHeader>
        <el-button type="primary" :icon="CirclePlus" @click="openDrawer('新增')">{{ t("annotation.addLabel") }}</el-button>
      </template>
      <!-- 表格操作 -->
      <template #operation="scope">
        <el-button type="primary" link :icon="Edit" @click="openDrawer('编辑', scope.row)">{{
          t("annotation.editLabel")
        }}</el-button>
        <el-button type="danger" link :icon="Delete" @click="deleteLabelHandler(scope.row)">{{
          t("annotation.deleteLabel")
        }}</el-button>
      </template>
    </ProTable>
    <LabelDrawer ref="drawerRef" />
  </div>
</template>

<script setup lang="ts">
import { ref, h, computed } from "vue";
import { useI18n } from "vue-i18n";
import { useHandleData } from "@/hooks/useHandleData";
import ProTable from "@/components/ProTable/index.vue";
import LabelDrawer from "./components/dialogs/LabelDrawer.vue";
import { ColumnProps, ProTableInstance } from "@/components/ProTable/interface";
import { CirclePlus, Delete, Edit } from "@element-plus/icons-vue";
import { getLabelListApi, deleteLabelApi } from "@/api/modules/label";
import type { LabelItem } from "@/api/model/labelModel";

// 国际化
const { t } = useI18n();

// ProTable 实例
const proTable = ref<ProTableInstance>();

// dataCallback 是对于返回的表格数据做处理
const dataCallback = (data: any) => {
  // 检查返回的数据结构
  if (data && data.records) {
    return {
      records: data.records,
      total: data.total || data.records.length || 0
    };
  }
  // 如果没有records字段，但有data字段，尝试使用data
  if (data && data.data && data.data.records) {
    return {
      records: data.data.records,
      total: data.data.total || data.data.records.length || 0
    };
  }
  // 如果直接返回了数组，包装成records格式
  if (Array.isArray(data)) {
    return {
      records: data,
      total: data.length
    };
  }
  // 默认情况
  return {
    records: [],
    total: 0
  };
};

// 调试用的API函数
const debugGetLabelListApi = async (params: any) => {
  return await getLabelListApi(params);
};

// 表格配置项 - 使用 computed 确保语言切换时能够响应更新
const columns = computed<ColumnProps<LabelItem>[]>(() => [
  {
    type: "index",
    label: "#",
    width: 80
  },
  {
    prop: "id",
    label: "ID",
    width: 80
  },
  {
    prop: "name",
    label: t("annotation.labelName"),
    search: {
      el: "input",
      key: "name",
      props: { placeholder: t("annotation.labelName") }
    }
  },
  {
    prop: "color",
    label: t("annotation.color"),
    width: 140,
    render: ({ row }) => {
      return h("div", { class: "color-display" }, [
        h("span", {
          class: "color-box",
          style: {
            backgroundColor: row.color,
            display: "inline-block",
            width: "30px",
            height: "30px",
            borderRadius: "4px",
            border: "1px solid #ddd"
          }
        }),
        h("span", { style: { marginLeft: "10px" } }, row.color)
      ]);
    }
  },
  { prop: "operation", label: t("annotation.operation"), fixed: "right", width: 200 }
]);

// 删除标签
const deleteLabelHandler = async (row: LabelItem) => {
  await useHandleData(deleteLabelApi, { id: row.id }, t("annotation.deleteConfirm", { name: row.name }), "warning", t);
  proTable.value?.getTableList();
};

// 打开 drawer(新增、编辑)
const drawerRef = ref<InstanceType<typeof LabelDrawer> | null>(null);
const openDrawer = (title: string, row: Partial<LabelItem> = {}) => {
  const params = {
    title,
    isView: title === "查看",
    row: { ...row },
    getTableList: proTable.value?.getTableList
  };
  drawerRef.value?.acceptParams(params);
};
</script>

<style scoped lang="scss">
.color-display {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  height: 100%;
}
</style>
