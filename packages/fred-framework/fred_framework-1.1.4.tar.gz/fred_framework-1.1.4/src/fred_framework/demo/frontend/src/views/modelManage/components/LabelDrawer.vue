<template>
  <el-drawer v-model="drawerVisible" :title="`${modelName} - 标签管理`" direction="rtl" size="600px" :before-close="handleClose">
    <div class="label-drawer">
      <!-- 新增标签表单 -->
      <el-card class="add-label-card" shadow="never">
        <template #header>
          <div class="card-header">
            <span>新增标签</span>
          </div>
        </template>
        <el-form ref="formRef" :model="form" :rules="rules" label-width="80px" @submit.prevent="handleSubmit">
          <el-form-item label="标签名称" prop="name">
            <el-input v-model="form.name" placeholder="请输入标签名称" maxlength="50" show-word-limit />
          </el-form-item>
          <el-form-item label="标签颜色" prop="color">
            <el-color-picker v-model="form.color" :predefine="predefineColors" show-alpha />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSubmit" :loading="submitLoading"> 添加标签 </el-button>
            <el-button @click="resetForm">重置</el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <!-- 标签列表 -->
      <el-card class="label-list-card" shadow="never">
        <template #header>
          <div class="card-header">
            <span>标签列表</span>
            <el-button type="primary" size="small" @click="getLabelList">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </template>

        <div v-loading="loading" class="label-list">
          <div v-if="labelList.length === 0" class="empty-state">
            <el-empty description="暂无标签" />
          </div>
          <div v-else class="label-items">
            <div v-for="label in labelList" :key="label.id" class="label-item">
              <div class="label-content">
                <div class="label-color" :style="{ backgroundColor: label.color }"></div>
                <span class="label-name">{{ label.name }}</span>
              </div>
              <div class="label-actions">
                <el-button type="danger" size="small" link @click="deleteLabel(label)"> 删除 </el-button>
              </div>
            </div>
          </div>
        </div>
      </el-card>
    </div>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, reactive } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { Refresh } from "@element-plus/icons-vue";
import { getLabelListByModelApi, createLabelApi, deleteLabelApi } from "@/api/modules/label";

// 抽屉显示状态
const drawerVisible = ref(false);
const loading = ref(false);
const submitLoading = ref(false);

// 模型信息
const modelId = ref<number>(0);
const modelName = ref<string>("");

// 标签列表
const labelList = ref<any[]>([]);

// 表单相关
const formRef = ref();
const form = reactive({
  name: "",
  color: "#409EFF"
});

// 表单验证规则
const rules = {
  name: [
    { required: true, message: "请输入标签名称", trigger: "blur" },
    { min: 1, max: 50, message: "标签名称长度在1到50个字符", trigger: "blur" }
  ],
  color: [{ required: true, message: "请选择标签颜色", trigger: "change" }]
};

// 预定义颜色
const predefineColors = [
  "#409EFF",
  "#67C23A",
  "#E6A23C",
  "#F56C6C",
  "#909399",
  "#FF6B6B",
  "#4ECDC4",
  "#45B7D1",
  "#96CEB4",
  "#FFEAA7"
];

// 打开抽屉
const open = (params: { modelId: number; modelName: string }) => {
  modelId.value = params.modelId;
  modelName.value = params.modelName;
  drawerVisible.value = true;
  getLabelList();
};

// 关闭抽屉
const handleClose = () => {
  drawerVisible.value = false;
  resetForm();
  labelList.value = [];
};

// 获取标签列表
const getLabelList = async () => {
  if (!modelId.value) return;

  loading.value = true;
  try {
    const response = await getLabelListByModelApi({ modelId: modelId.value });
    labelList.value = response.data.records || [];
  } catch {
    ElMessage.error("获取标签列表失败");
  } finally {
    loading.value = false;
  }
};

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return;

  const valid = await formRef.value.validate();
  if (!valid) return;

  submitLoading.value = true;
  try {
    await createLabelApi({
      name: form.name,
      color: form.color,
      model_id: modelId.value
    });

    ElMessage.success("标签添加成功");
    resetForm();
    getLabelList();
  } catch {
    ElMessage.error("添加标签失败");
  } finally {
    submitLoading.value = false;
  }
};

// 重置表单
const resetForm = () => {
  form.name = "";
  form.color = "#409EFF";
  formRef.value?.resetFields();
};

// 删除标签
const deleteLabel = async (label: any) => {
  try {
    await ElMessageBox.confirm(`确定要删除标签"${label.name}"吗？`, "确认删除", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning"
    });

    await deleteLabelApi({ id: label.id });
    ElMessage.success("标签删除成功");
    getLabelList();
  } catch (error) {
    if (error !== "cancel") {
      ElMessage.error("删除标签失败");
    }
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

.add-label-card,
.label-list-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.label-list {
  min-height: 200px;
}

.empty-state {
  text-align: center;
  padding: 40px 0;
}

.label-items {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.label-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  background-color: #fafafa;
  transition: all 0.3s;
}

.label-item:hover {
  background-color: #f5f7fa;
  border-color: #c0c4cc;
}

.label-content {
  display: flex;
  align-items: center;
  gap: 12px;
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
