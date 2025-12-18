<template>
  <el-drawer v-model="drawerVisible" :title="`${modelName} - 标签管理`" direction="rtl" size="600px" :before-close="handleClose">
    <div class="label-drawer">
      <!-- 已绑定标签列表 -->
      <el-card class="label-list-card" shadow="never">
        <template #header>
          <div class="card-header">
            <div class="card-title">
              <span>已绑定标签</span>
              <el-tag type="info" size="small" effect="plain">
                <el-icon><Rank /></el-icon>
                可拖拽排序
              </el-tag>
            </div>
            <el-button type="primary" size="small" @click="getLabelList">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </template>

        <div v-loading="loading" class="label-list">
          <div v-if="labelList.length === 0" class="empty-state">
            <el-empty description="暂无已绑定标签" />
          </div>
          <draggable v-else v-model="labelList" @end="handleDragEnd" class="label-items">
            <template #item="{ element: label, index }">
              <div class="label-item">
                <div class="label-content">
                  <el-icon class="drag-handle"><Rank /></el-icon>
                  <span class="sort-number">{{ index }}</span>
                  <div class="label-color" :style="{ backgroundColor: formatColorToHex(label.color) }"></div>
                  <span class="label-name">{{ label.name }}</span>
                  <span class="label-color-text">{{ formatColorToHex(label.color) }}</span>
                </div>
                <div class="label-actions">
                  <el-button type="warning" size="small" link @click="unlinkLabel(label)"> 解除关联 </el-button>
                </div>
              </div>
            </template>
          </draggable>
        </div>
      </el-card>

      <!-- 未绑定标签列表 -->
      <el-card class="unbound-label-card" shadow="never">
        <template #header>
          <div class="card-header">
            <span>未绑定标签</span>
            <div class="header-actions">
              <el-checkbox v-model="selectAll" @change="handleSelectAll">全选</el-checkbox>
              <el-button type="success" size="small" :disabled="selectedLabels.length === 0" @click="batchBindLabels">
                批量绑定({{ selectedLabels.length }})
              </el-button>
              <el-button type="primary" size="small" @click="getUnboundLabelList">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
          </div>
        </template>

        <div v-loading="unboundLoading" class="unbound-label-list">
          <div v-if="unboundLabelList.length === 0" class="empty-state">
            <el-empty description="暂无未绑定标签" />
          </div>
          <div v-else class="unbound-label-items">
            <div v-for="label in unboundLabelList" :key="label.id" class="unbound-label-item">
              <div class="label-content">
                <el-checkbox v-model="label.selected" @change="handleLabelSelect(label)" />
                <div class="label-color" :style="{ backgroundColor: formatColorToHex(label.color) }"></div>
                <span class="label-name">{{ label.name }}</span>
                <span class="label-color-text">{{ formatColorToHex(label.color) }}</span>
              </div>
              <div class="label-actions">
                <el-button type="primary" size="small" link @click="bindLabel(label)"> 绑定到模型 </el-button>
              </div>
            </div>
          </div>
        </div>
      </el-card>
    </div>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { Refresh, Rank } from "@element-plus/icons-vue";
import draggable from "vuedraggable";
import {
  getLabelListByModelApi,
  unlinkLabelFromModelApi,
  getUnboundLabelsApi,
  bindLabelToModelApi,
  batchBindLabelsToModelApi,
  updateLabelSortApi
} from "@/api/modules/label";
import { rgbToHex } from "@/utils/color";

// 抽屉显示状态
const drawerVisible = ref(false);
const loading = ref(false);
const unboundLoading = ref(false);

// 模型信息
const modelId = ref<number>(0);
const modelName = ref<string>("");

// 标签列表
const labelList = ref<any[]>([]);
const unboundLabelList = ref<any[]>([]);

// 未绑定标签选择
const selectAll = ref(false);

// 选中的标签列表
const selectedLabels = computed(() => {
  return unboundLabelList.value.filter(label => label.selected);
});

// 颜色格式化函数：确保颜色值以十六进制格式显示
const formatColorToHex = (color: string): string => {
  // 如果颜色为空或无效，返回默认颜色
  if (!color || typeof color !== "string") {
    return "#409EFF";
  }

  // 去除首尾空格
  const trimmedColor = color.trim();

  // 如果已经是十六进制格式，直接返回
  if (trimmedColor.startsWith("#")) {
    return trimmedColor.toUpperCase();
  }

  // 如果是 rgb 格式，转换为十六进制
  if (trimmedColor.startsWith("rgb")) {
    const match = trimmedColor.match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/);
    if (match) {
      const r = parseInt(match[1]);
      const g = parseInt(match[2]);
      const b = parseInt(match[3]);
      const result = rgbToHex(r, g, b);
      return typeof result === "string" ? result : "#409EFF";
    }
  }

  // 如果是 rgba 格式，转换为十六进制（忽略透明度）
  if (trimmedColor.startsWith("rgba")) {
    const match = trimmedColor.match(/rgba\((\d+),\s*(\d+),\s*(\d+),\s*([\d.]+)\)/);
    if (match) {
      const r = parseInt(match[1]);
      const g = parseInt(match[2]);
      const b = parseInt(match[3]);
      const result = rgbToHex(r, g, b);
      return typeof result === "string" ? result : "#409EFF";
    }
  }

  // 如果是其他格式或无效格式，返回默认颜色
  return "#409EFF";
};

// 打开抽屉
const open = (params: { modelId: number; modelName: string }) => {
  modelId.value = params.modelId;
  modelName.value = params.modelName;
  drawerVisible.value = true;
  getLabelList();
  getUnboundLabelList();
};

// 关闭抽屉
const handleClose = () => {
  drawerVisible.value = false;
  labelList.value = [];
  unboundLabelList.value = [];
};

// 获取标签列表
const getLabelList = async () => {
  if (!modelId.value) return;

  loading.value = true;
  try {
    const response = await getLabelListByModelApi({ modelId: modelId.value });

    // response.data 包含 ResPage 数据
    const data = response.data;
    if (data && data.records) {
      labelList.value = data.records;
    } else if (Array.isArray(data)) {
      labelList.value = data;
    } else {
      labelList.value = [];
    }
  } catch {
    ElMessage.error("获取标签列表失败");
  } finally {
    loading.value = false;
  }
};

// 获取未绑定标签列表
const getUnboundLabelList = async () => {
  if (!modelId.value) return;

  unboundLoading.value = true;
  try {
    const response = await getUnboundLabelsApi({ getAll: true, model_id: modelId.value });

    // response.data 包含 ResPage 数据
    const data = response.data as any;
    if (data && data.records) {
      unboundLabelList.value = data.records.map((label: any) => ({ ...label, selected: false }));
    } else if (Array.isArray(data)) {
      unboundLabelList.value = data.map((label: any) => ({ ...label, selected: false }));
    } else {
      unboundLabelList.value = [];
    }
  } catch {
    ElMessage.error("获取未绑定标签列表失败");
  } finally {
    unboundLoading.value = false;
  }
};

// 绑定标签到模型
const bindLabel = async (label: any) => {
  try {
    await ElMessageBox.confirm(`确定要将标签"${label.name}"绑定到模型"${modelName.value}"吗？`, "确认绑定", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "info"
    });

    await bindLabelToModelApi({
      label_id: label.id,
      model_id: modelId.value
    });

    ElMessage.success("标签绑定成功");
    // 刷新两个列表
    getLabelList();
    getUnboundLabelList();
  } catch (error) {
    if (error !== "cancel") {
      ElMessage.error("绑定标签失败");
    }
  }
};

// 解除标签与模型的关联关系
const unlinkLabel = async (label: any) => {
  try {
    await ElMessageBox.confirm(`确定要解除标签"${label.name}"与模型的关联关系吗？`, "确认解除关联", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning"
    });

    await unlinkLabelFromModelApi({ label_id: label.id, model_id: modelId.value });
    ElMessage.success("标签与模型关联已解除");
    // 刷新两个列表
    getLabelList();
    getUnboundLabelList();
  } catch (error) {
    if (error !== "cancel") {
      ElMessage.error("解除关联失败");
    }
  }
};

// 全选/取消全选
const handleSelectAll = (checked: any) => {
  const isChecked = Boolean(checked);
  unboundLabelList.value.forEach(label => {
    label.selected = isChecked;
  });
};

// 单个标签选择状态变化
const handleLabelSelect = (label: any) => {
  if (label.selected) {
    selectAll.value = selectedLabels.value.length === unboundLabelList.value.length;
  } else {
    selectAll.value = false;
  }
};

// 批量绑定标签
const batchBindLabels = async () => {
  if (selectedLabels.value.length === 0) {
    ElMessage.warning("请至少选择一个标签");
    return;
  }

  try {
    await ElMessageBox.confirm(
      `确定要将选中的 ${selectedLabels.value.length} 个标签绑定到模型"${modelName.value}"吗？`,
      "确认批量绑定",
      {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "info"
      }
    );

    const labelIds = selectedLabels.value.map(label => label.id);
    await batchBindLabelsToModelApi({
      label_ids: labelIds,
      model_id: modelId.value
    });

    ElMessage.success(`成功绑定 ${labelIds.length} 个标签`);
    // 刷新两个列表
    getLabelList();
    getUnboundLabelList();
    selectAll.value = false;
  } catch (error) {
    if (error !== "cancel") {
      ElMessage.error("批量绑定标签失败");
    }
  }
};

// 拖拽排序结束
const handleDragEnd = async () => {
  // 生成新的排序数据，排序值从0开始
  const labelOrders = labelList.value.map((label, index) => ({
    label_id: label.id,
    sort: index
  }));

  try {
    await updateLabelSortApi({
      model_id: modelId.value,
      label_orders: labelOrders
    });
    ElMessage.success("排序已保存");
  } catch {
    ElMessage.error("更新排序失败");
    // 重新获取列表以恢复正确的顺序
    getLabelList();
  }
};

// 暴露方法
defineExpose({
  open
});
</script>

<style scoped>
.label-drawer {
  padding: 0;
}

.unbound-label-card,
.label-list-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.unbound-label-list,
.label-list {
  min-height: 200px;
}

.empty-state {
  text-align: center;
  padding: 40px 0;
}

.unbound-label-items,
.label-items {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.unbound-label-item,
.label-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  background-color: #fafafa;
  transition: all 0.3s;
  cursor: move;
}

.unbound-label-item:hover,
.label-item:hover {
  background-color: #f5f7fa;
  border-color: #c0c4cc;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.label-content {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.drag-handle {
  cursor: move;
  color: #909399;
  font-size: 16px;
  transition: color 0.3s;
}

.drag-handle:hover {
  color: #409eff;
}

.sort-number {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 4px;
  background: #f0f0f0;
  color: #666;
  font-size: 12px;
  font-weight: 600;
}

.label-color {
  width: 20px;
  height: 20px;
  border-radius: 4px;
  border: 1px solid #dcdfe6;
}

.label-name {
  font-size: 14px;
  color: #303133;
  font-weight: 500;
}

.label-color-text {
  font-size: 12px;
  color: #909399;
  margin-left: 8px;
  font-family: monospace;
}

.label-actions {
  display: flex;
  gap: 8px;
}

:deep(.el-card__header) {
  padding: 16px 20px;
  border-bottom: 1px solid #e4e7ed;
}

:deep(.el-card__body) {
  padding: 20px;
}

:deep(.el-form-item) {
  margin-bottom: 20px;
}

:deep(.el-color-picker) {
  vertical-align: top;
}
</style>
