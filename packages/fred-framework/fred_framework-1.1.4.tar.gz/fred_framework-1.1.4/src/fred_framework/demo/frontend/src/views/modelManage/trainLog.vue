<template>
  <div class="table-box">
    <ProTable ref="proTable" :columns="columns" :request-api="getTrainLogList" :data-callback="dataCallback">
      <!-- 操作列 -->
      <template #operation="scope">
        <el-button v-if="Number(scope.row.status) === 1" type="danger" size="small" @click="handleStopTrain(scope.row)">
          {{ t("trainLog.stopTrain") || "终止训练" }}
        </el-button>
        <span v-else>-</span>
      </template>
    </ProTable>
  </div>
</template>

<script setup lang="tsx" name="trainLog">
import { ref, computed } from "vue";
import ProTable from "@/components/ProTable/index.vue";
import { ColumnProps, ProTableInstance } from "@/components/ProTable/interface";
import { getTrainLogListApi, stopTrainApi } from "@/api/modules/annotation";
import { getModelListApi } from "@/api/modules/model";
import { useI18n } from "vue-i18n";
import { useHandleData } from "@/hooks/useHandleData";

// 国际化
const { t } = useI18n();

// ProTable 实例
const proTable = ref<ProTableInstance>();

// dataCallback 是对于返回的表格数据做处理
const dataCallback = (data: any) => {
  // 确保数据格式正确，统一转换状态值为数字类型
  if (data.records && Array.isArray(data.records)) {
    data.records = data.records.map((record: any) => {
      // 转换状态值为数字
      if (record.status !== null && record.status !== undefined) {
        record.status = Number(record.status);
      }
      // 转换时间戳为数字
      if (record.start_time !== null && record.start_time !== undefined) {
        record.start_time = Number(record.start_time);
      }
      if (record.end_time !== null && record.end_time !== undefined) {
        record.end_time = Number(record.end_time);
      }
      return record;
    });
  }
  return {
    records: data.records || [],
    total: data.total || 0
  };
};

// 获取训练日志列表
const getTrainLogList = (params: any) => {
  return getTrainLogListApi(params);
};

// 格式化时间戳为日期时间字符串
const formatTimestamp = (timestamp: number | null) => {
  if (!timestamp) return "-";
  const date = new Date(timestamp * 1000);
  return date.toLocaleString("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit"
  });
};

// 格式化状态显示
const formatStatus = (status: number | null) => {
  if (status === null || status === undefined) return "-";
  const statusMap: Record<number, string> = {
    0: t("trainLog.statusNotStarted") || "未开始",
    1: t("trainLog.statusTraining") || "训练中",
    2: t("trainLog.statusCompleted") || "训练完成",
    3: t("trainLog.statusError") || "训练异常",
    4: t("trainLog.statusTerminated") || "主动终止"
  };
  return statusMap[status] || `${t("trainLog.statusUnknown") || "未知"}(${status})`;
};

// 获取模型列表选项（用于下拉菜单）
const getModelOptions = async () => {
  try {
    const response: any = await getModelListApi({
      pageNum: 1,
      pageSize: 1000 // 获取所有模型
    });

    let records: any[] = [];
    if (response && response.data && response.data.records) {
      records = response.data.records;
    } else if (response && response.records) {
      // 兼容直接返回records的情况
      records = response.records;
    }

    // 返回格式需要与 ProTable 期望的一致：{ data: [...] }
    return {
      data: records.map((item: any) => ({
        label: item.name,
        value: item.name // 使用模型名字作为值，因为后端支持通过 model_name 搜索
      }))
    };
  } catch (error) {
    console.error("获取模型列表失败:", error);
    return { data: [] };
  }
};

// 表格配置项 - 使用 computed 确保语言切换时能够响应更新
const columns = computed<ColumnProps<any>[]>(() => [
  {
    prop: "id",
    label: t("trainLog.id") || "ID",
    width: 80
  },
  {
    prop: "model_name",
    label: t("trainLog.modelName") || "模型",
    width: 150,
    enum: getModelOptions,
    search: {
      el: "select",
      props: {
        placeholder: t("trainLog.selectModelName") || "请选择模型",
        filterable: true
      }
    },
    fieldNames: { label: "label", value: "value" }
  },
  {
    prop: "user_name",
    label: t("trainLog.userName") || "用户名字",
    width: 150,
    search: {
      el: "input",
      props: { placeholder: t("trainLog.inputUserName") || "请输入用户名字" }
    }
  },
  {
    prop: "start_time",
    label: t("trainLog.startTime") || "开始时间",
    width: 200,
    render: ({ row }: { row: any }) => {
      return <span>{formatTimestamp(row.start_time)}</span>;
    }
  },
  {
    prop: "end_time",
    label: t("trainLog.endTime") || "结束时间",
    width: 200,
    render: ({ row }: { row: any }) => {
      return <span>{formatTimestamp(row.end_time)}</span>;
    }
  },
  {
    prop: "source_path",
    label: t("trainLog.sourcePath") || "资源路径",
    minWidth: 200
  },
  {
    prop: "result_path",
    label: t("trainLog.resultPath") || "结果路径",
    minWidth: 200
  },
  {
    prop: "log_file",
    label: t("trainLog.logFile") || "日志文件",
    minWidth: 150
  },
  {
    prop: "status",
    label: t("trainLog.status") || "状态",
    width: 100,
    enum: [
      { label: t("trainLog.statusNotStarted") || "未开始", value: 0 },
      { label: t("trainLog.statusTraining") || "训练中", value: 1 },
      { label: t("trainLog.statusCompleted") || "训练完成", value: 2 },
      { label: t("trainLog.statusError") || "训练异常", value: 3 },
      { label: t("trainLog.statusTerminated") || "主动终止", value: 4 }
    ],
    search: {
      el: "select",
      props: {
        placeholder: t("trainLog.selectStatus") || "请选择状态"
      }
    },
    fieldNames: { label: "label", value: "value" },
    render: ({ row }: { row: any }) => {
      return <span>{formatStatus(row.status)}</span>;
    }
  },
  {
    prop: "operation",
    label: t("trainLog.operation") || "操作",
    width: 120,
    fixed: "right"
  }
]);

// 终止训练
const handleStopTrain = async (row: any) => {
  await useHandleData(stopTrainApi, { id: row.id }, t("trainLog.stopTrainConfirm") || "确定要终止该训练任务吗？", "warning", t);
  proTable.value?.getTableList();
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
