<template>
  <el-dialog
    v-model="dialogVisible"
    title="导出标注内容"
    width="600px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    @close="handleClose"
  >
    <div class="export-dialog-content">
      <el-form :model="exportForm" label-width="100px">
        <!-- 模型选择 -->
        <el-form-item label="选择模型" required>
          <el-select
            v-model="selectedModel"
            placeholder="请选择模型"
            filterable
            clearable
            @change="handleModelChange"
            style="width: 100%"
          >
            <el-option v-for="model in modelList" :key="model.id" :label="model.name" :value="model.id" />
          </el-select>
          <div class="form-tip">提示：选择模型后将导出该模型关联的所有标签</div>
        </el-form-item>

        <!-- 标签显示（当选择了模型时） -->
        <el-form-item v-if="selectedModel && availableLabelsForModel.length > 0" label="模型标签">
          <div class="label-selection">
            <div class="selection-header">
              <span class="selected-count">共 {{ availableLabelsForModel.length }} 个标签</span>
            </div>
            <div class="label-list">
              <div v-for="label in availableLabelsForModel" :key="label.id" class="label-item display-only">
                <div class="label-content">
                  <div class="label-sort">{{ label.sort || 0 }}</div>
                  <div class="label-color" :style="{ backgroundColor: label.color }"></div>
                  <span class="label-name">{{ label.name }}</span>
                </div>
              </div>
            </div>
          </div>
        </el-form-item>

        <!-- 选择标签提示 -->
        <el-form-item v-else-if="!selectedModel">
          <el-alert title="提示" type="warning" :closable="false" show-icon>
            <template #default>
              <p>请先选择一个模型，系统将显示该模型关联的所有标签</p>
            </template>
          </el-alert>
        </el-form-item>

        <!-- 导出说明 -->
        <el-form-item>
          <el-alert title="导出说明" type="info" :closable="false" show-icon>
            <template #default>
              <ul class="export-tips">
                <li v-if="selectedModel">选择了模型后，将导出该模型关联的所有标签的标注内容</li>
                <li v-else>请选择一个模型，系统将显示该模型关联的所有标签并导出相应的标注内容</li>
                <li>导出的文件为YOLO格式的ZIP压缩包</li>
                <li>包含图片文件和对应的标注文件</li>
              </ul>
            </template>
          </el-alert>
        </el-form-item>
      </el-form>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" :loading="exportLoading" :disabled="!selectedModel" @click="handleExport">
          <el-icon><Download /></el-icon>
          导出标注
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import { Download } from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";
import { getModelListApi } from "@/api/modules/model";
import { getLabelListByModelApi } from "@/api/modules/label";

interface LabelItem {
  id: number;
  name: string;
  color: string;
  sort?: number;
}

interface ModelItem {
  id: number;
  name: string;
}

interface Props {
  visible: boolean;
  availableLabels: LabelItem[];
  exportLoading?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  exportLoading: false
});

const emit = defineEmits<{
  (e: "close"): void;
  (e: "export", modelId: number): void;
}>();

// 响应式数据
const dialogVisible = ref(false);
const selectedModel = ref<number | null>(null);
const modelList = ref<ModelItem[]>([]);
const availableLabelsForModel = ref<LabelItem[]>([]);

// 监听visible变化，加载模型列表
watch(
  () => props.visible,
  async newVal => {
    dialogVisible.value = newVal;
    if (newVal) {
      // 对话框打开时重置选择状态
      selectedModel.value = null;
      // 加载模型列表
      await loadModelList();
    }
  }
);

// 加载模型列表
const loadModelList = async () => {
  try {
    const response = await getModelListApi({ pageNum: 1, pageSize: 1000 });
    if (response.data) {
      modelList.value = response.data.records || [];
    }
  } catch (error) {
    console.error("加载模型列表失败:", error);
  }
};

// 加载模型的标签列表
const loadLabelsByModel = async (modelId: number) => {
  try {
    const response = await getLabelListByModelApi({ modelId });
    if (response.data) {
      // 按照 sort 排序
      const labels = response.data.records || [];
      availableLabelsForModel.value = labels.sort((a, b) => (a.sort || 0) - (b.sort || 0));
    }
  } catch (error) {
    console.error("加载模型标签列表失败:", error);
    availableLabelsForModel.value = [];
  }
};

// 模型选择变化
const handleModelChange = async (modelId: number | null) => {
  if (modelId) {
    // 加载模型对应的标签列表
    await loadLabelsByModel(modelId);
  } else {
    // 如果没有选择模型，清空模型标签列表
    availableLabelsForModel.value = [];
  }
};

// 关闭对话框
const handleClose = () => {
  dialogVisible.value = false;
  emit("close");
};

// 导出标注
const handleExport = () => {
  if (!selectedModel.value) {
    ElMessage.warning("请先选择一个模型");
    return;
  }

  // 导出选中模型的所有标签
  emit("export", selectedModel.value);
};
</script>

<style lang="scss" scoped>
.export-dialog-content {
  .label-selection {
    .selection-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 16px;
      padding: 12px;
      background-color: #f5f7fa;
      border-radius: 6px;

      .selected-count {
        font-size: 14px;
        color: #606266;
      }
    }

    .label-list {
      max-height: 300px;
      overflow-y: auto;
      border: 1px solid #dcdfe6;
      border-radius: 6px;
      padding: 8px;
      display: flex;
      flex-wrap: wrap;
      gap: 8px;

      .label-item {
        min-width: 120px;
        max-width: 200px;
        padding: 8px 12px;
        border-radius: 6px;
        border: 1px solid #f0f0f0;
        background-color: #fff;

        .label-content {
          display: flex;
          align-items: center;
          gap: 8px;

          .label-sort {
            min-width: 20px;
            height: 20px;
            background-color: #409eff;
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: bold;
            flex-shrink: 0;
          }

          .label-color {
            width: 16px;
            height: 16px;
            border-radius: 3px;
            border: 1px solid #dcdfe6;
            flex-shrink: 0;
          }

          .label-name {
            font-weight: 500;
            color: #303133;
            font-size: 14px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
          }
        }
      }

      .label-item.display-only {
        background-color: #f5f7fa;
        border-left: 3px solid #409eff;
      }
    }
  }

  .export-tips {
    margin: 0;
    padding-left: 16px;

    li {
      margin-bottom: 4px;
      line-height: 1.5;
    }
  }

  .form-tip {
    margin-top: 8px;
    font-size: 12px;
    color: #909399;
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
